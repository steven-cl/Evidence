import os
import time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from audio_manager import AudioManager

# Import internal gameplay modules
from menu import MainMenu
from camera import CameraFPS
from skybox import Skybox
from load_screen import render_loading_screen
from scene_loader import (
    load_scene_assets,
    toggle_nearest_visible_door,
    draw_static_model,
    update_doors,
    draw_doors,
)

# =============================================================================
# --- TACTICAL DEBUG SYSTEM (F1, F2, F3) ---
# =============================================================================
class DebugState:
    def __init__(self):
        self.overlay = False   # F1: Bounding boxes and physics spheres
        self.hud = False       # F2: On-screen telemetry text overlay
        self.wireframe = False # F3: Global wireframe polygon rendering mode

_debug_font = None

def init_debug_font():
    global _debug_font
    if _debug_font is None:
        pygame.font.init()
        try:
            _debug_font = pygame.font.SysFont("Courier New", 18, bold=True)
        except:
            _debug_font = pygame.font.Font(None, 24)

def draw_debug_text(x, y, text, color=(0, 255, 0)):
    global _debug_font
    text_surface = _debug_font.render(text, True, color)
    w, h = text_surface.get_size()
    text_data = pygame.image.tobytes(text_surface, "RGBA", False)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)

    glColor4f(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glDeleteTextures([tex_id])

def draw_debug_visuals(camera, house, setting_doors, is_wireframe_global):
    """
    Renders the physical collision overlay (bounding boxes and entities) over the environment.
    """
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glDisable(GL_DEPTH_TEST) # X-Ray diagnostic visibility override

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(1.5)

    # 1. Geometry Colliders
    glColor3f(0.0, 1.0, 0.0) # Green wireframes
    glBegin(GL_TRIANGLES)
    for tri in house.colliders:
        glVertex3f(tri.a.x, tri.a.y, tri.a.z)
        glVertex3f(tri.b.x, tri.b.y, tri.b.z)
        glVertex3f(tri.c.x, tri.c.y, tri.c.z)
        
    for door in setting_doors:
        for tri in door.get_transformed_triangles(house):
            glVertex3f(tri.a.x, tri.a.y, tri.a.z)
            glVertex3f(tri.b.x, tri.b.y, tri.b.z)
            glVertex3f(tri.c.x, tri.c.y, tri.c.z)
    glEnd()

    # 2. Detective Collision Hierarchy Rings
    if hasattr(camera, 'feet_pos'):
        glColor3f(1.0, 0.0, 0.0) # Red wireframes
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_LINE)

        glPushMatrix()
        glTranslatef(camera.torso_pos.x, camera.torso_pos.y, camera.torso_pos.z)
        gluSphere(quadric, camera.radius, 10, 10)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(camera.feet_pos.x, camera.feet_pos.y, camera.feet_pos.z)
        gluSphere(quadric, camera.radius, 10, 10)
        glPopMatrix()

        gluDeleteQuadric(quadric)
        glColor3f(1.0, 1.0, 1.0)

    # --- INTELLIGENT RENDER MODE RESTORATION ---
    # Respect the F3 toggle status. Return to LINE if active, else restore standard FILL
    if is_wireframe_global:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_FOG)
# =============================================================================

def setup_fog():
    """Configures global OpenGL exponential fog parameters for atmospheric mystery effect"""
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.1)
    fog_color = [0.1, 0.1, 0.15, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    glHint(GL_FOG_HINT, GL_NICEST)

def setup_display():
    """Initializes Pygame subsystem and setups a borderless fullscreen window relative to the mouse"""
    os.environ['SDL_VIDEO_WINDOW_POS'] = "mouse"
    pygame.init()
    
    monitor_info = pygame.display.Info()
    screen_width = monitor_info.current_w
    screen_height = monitor_info.current_h
    
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL | NOFRAME)
    pygame.display.set_caption("Evidence - Resolve the Mystery")
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    return screen_width, screen_height

def setup_camera(screen_width, screen_height):
    """Instantiates the standard FPS interaction camera with initial transform look parameters"""
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    camera.pos_x = 0.0 
    camera.pos_y = 1.65
    camera.pos_z = 0.0   
    camera.pitch = -45.0 
    camera.yaw = -90.0   

    camera.update_camera_vectors()
    return camera

def setup_skybox():
    """Maps architectural asset texturing locations to instantiate the environmental Skybox"""
    skybox_paths = {
        'posz': 'source/textures/posz.jpg',
        'posx': 'source/textures/posx.jpg',
        'negz': 'source/textures/negz.jpg',
        'posy': 'source/textures/posy.jpg',
        'negx': 'source/textures/negx.jpg',
        'negy': 'source/textures/negy.jpg',
    }
    return Skybox(skybox_paths)

def process_game_event(event, menu, camera, setting_doors, debug_state, audio):
    """Processes interactive operational keyboard inputs during active gameplay simulation loop"""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            menu.state = 'MENU'
            audio.play_sfx("ui_click")
        elif event.key == pygame.K_e:
            door_interacted = toggle_nearest_visible_door(setting_doors, camera)
            if door_interacted:
                audio.play_sfx("door_open")

        # [F1] PHYSICS INTERACTIVE OVERLAY (Raycast testing and diagnostic wireframes)
        elif event.key == pygame.K_F1:
            debug_state.overlay = not debug_state.overlay
            audio.play_sfx("ui_click")
            
        # [F2] HUD ON-SCREEN TELEMETRY TEXT (FPS metrics counter data)
        elif event.key == pygame.K_F2:
            debug_state.hud = not debug_state.hud
            audio.play_sfx("ui_click")
            
        # [F3] GLOBAL POLYGON WIREFRAME RENDERING OVERRIDEMODE
        elif event.key == pygame.K_F3:
            debug_state.wireframe = not debug_state.wireframe
            audio.play_sfx("ui_click")
            if debug_state.wireframe:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

def handle_events(menu, camera, setting_doors, debug_state, audio):
    """Centralizes global OS events queue delegation matrices routes loops"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if menu.state in ['MENU', 'OPTIONS']:
            # Capture tracking coordinates indices before input parsing to verify selection mutations
            old_selection = menu.options_selection if menu.state == 'OPTIONS' else menu.current_selection
            
            menu.handle_input(event, camera)
            
            new_selection = menu.options_selection if menu.state == 'OPTIONS' else menu.current_selection
            
            # Play a tactical acoustic UI click on navigational selection mutations or execution confirmations
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if old_selection != new_selection:
                        audio.play_sfx("ui_click")
                elif event.key == pygame.K_RETURN:
                    audio.play_sfx("ui_click")
                    
                    # Sychronize changes made inside the Options volume adjustment layout component
                    if menu.state == 'OPTIONS' and menu.options_selection == 0:
                        audio.set_volume(menu.volume)

            if menu.state == 'QUIT':
                return False
                
        elif menu.state == 'GAME':
            process_game_event(event, menu, camera, setting_doors, debug_state, audio)

    return True

def render_game_world(camera, skybox, house, config_visual, setting_doors, door_materials, dt):
    """Draws spatial object models and environment geometry profiles"""
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_FOG)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    gluLookAt(
        0.0, 0.0, 0.0,
        camera.front_x, camera.front_y, camera.front_z,
        0.0, 1.0, 0.0,
    )
    skybox.draw()

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_FOG)

    camera.update_view()
    update_doors(setting_doors, dt)
    draw_static_model(house, config_visual, door_materials)
    draw_doors(setting_doors, house, config_visual)

def render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt, clock, debug_state, audio):
    """Executes specific clear procedures and decides whether to paint UI or 3D spaces matrices"""
    glClearColor(0.1, 0.1, 0.15, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    if menu.state in ['MENU', 'OPTIONS']:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        menu.render()
    else:
        pygame.event.set_grab(True)
        pygame.mouse.set_visible(False)
        
        dx, dy = pygame.mouse.get_rel()
        camera.process_mouse(dx, dy) 
        
        frame_colliders = list(house.colliders)
        for door in setting_doors:
            frame_colliders.extend(door.get_transformed_triangles(house))

        # 1. Capture the keys state BEFORE processing movement to check for input displacement
        keys = pygame.key.get_pressed()
        is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        
        camera.process_keyboard(dt, frame_colliders)

        # 2. Update footsteps acoustics using delta time cadences sync
        # (Assuming camera has an internal state variable 'is_grounded', if not pass True)
        is_grounded = getattr(camera, 'is_grounded', True)
        audio.update_footsteps(dt, is_moving, is_grounded)

        render_game_world(camera, skybox, house, config_visual, setting_doors, door_materials, dt)

        # 1. Diagnostics Graphics Visual Overlay (F1: Colliders and Entities)
        if debug_state.overlay:
            draw_debug_visuals(camera, house, setting_doors, debug_state.wireframe)

        # 2. Telemetry HUD Overlay (F2: Diagnostic strings text rendering mapping matrices)
        if debug_state.hud:
            current_fps = clock.get_fps()
            state_str = "GROUNDED" if camera.is_grounded else "JUMPING/FALLING"
            
            glMatrixMode(GL_PROJECTION)
            glPushMatrix()
            glLoadIdentity()
            glOrtho(0, camera.width, camera.height, 0, -1, 1)
            
            glMatrixMode(GL_MODELVIEW)
            glPushMatrix()
            glLoadIdentity()
            
            glDisable(GL_DEPTH_TEST)
            glDisable(GL_LIGHTING)
            glDisable(GL_FOG) 
            
            init_debug_font()
            draw_debug_text(10, 10, f"FPS  : {current_fps:.1f}", (255, 255, 0))
            draw_debug_text(10, 30, f"XYZ  : {camera.pos_x:.2f}, {camera.pos_y:.2f}, {camera.pos_z:.2f}", (0, 255, 255))
            draw_debug_text(10, 50, f"STATE: {state_str}", (0, 255, 0) if camera.is_grounded else (255, 100, 100))
            
            glEnable(GL_FOG)
            glEnable(GL_DEPTH_TEST)
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW)
            glPopMatrix()

    pygame.display.flip()

def main():
    # Setup display framework layout environment metrics settings
    screen_width, screen_height = setup_display()

    # Initialize global professional Audio Management subsystem engine
    audio = AudioManager()
    audio.load_sfx("ui_click", "click.wav")
    audio.load_sfx("door_open", "door_open.wav")    
    audio.load_sfx("door_close", "door_close.wav") 
    audio.load_sfx("footstep", "footstep.wav")
    
    # Start looping streaming nighttime mystery ambient background music immediately on launch
    audio.play_ambient_music("suspense_ambient.mp3", loops=-1)

    # Initialize Core interface and visual layout component objects
    menu = MainMenu(screen_width, screen_height)
    camera = setup_camera(screen_width, screen_height)
    skybox = setup_skybox()
    
    debug_state = DebugState()
    
    # Fire initial execution loading timeline screens layouts splits
    render_loading_screen(screen_width, screen_height, duration=1.5, start_progress=0.0, target_progress=0.85)

    glEnable(GL_DEPTH_TEST)
    setup_fog()

    # Stream geometry coordinates profiles files data sets assets mapping
    house, config_visual, setting_doors, door_materials = load_scene_assets()
    
    # Terminate diagnostic load bars matrices layouts splits
    render_loading_screen(screen_width, screen_height, duration=0.4, start_progress=0.85, target_progress=1.0)

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    # Core engine frame process loop
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05) # Constrain spikes tracking factors layout sizes execution anomalies

        running = handle_events(menu, camera, setting_doors, debug_state, audio)
        
        if running:
            render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt, clock, debug_state, audio)

    pygame.quit()

if __name__ == '__main__':
    main()