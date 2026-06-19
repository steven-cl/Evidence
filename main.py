import os
import json
from time import sleep
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from audio_manager import AudioManager
import glm   


# Import internal gameplay modules
from menu import MainMenu
from camera import CameraFPS
from skybox import Skybox
from safe_interface import SafeInterface
from load_screen import render_loading_screen
from scene_loader import (
    load_scene_assets,
    toggle_nearest_visible_door,
    get_looked_at_door,
    draw_static_model,
    update_doors,
    draw_doors,
    draw_inspectables_world,
    draw_inspected_hud,
    ray_intersects_triangle
)

# =============================================================================
# --- PERSISTENCE ENGINE (SAVING) ---
# =============================================================================

SETTINGS_FILE = "settings.json"

def load_settings():
    """
    Loads previous settings from a JSON file. 
    If no file is found, returns default fallback values.
    """
    default_settings = {
        "width": 0,          # 0 indicates "Not configured, default to maximized"
        "height": 0,
        "is_fullscreen": False,
        "volume": 80
    }
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return default_settings

def save_settings(camera, menu):
    """
    Saves the exact state of the window resolution and menu configuration 
    to a JSON file before application exit to ensure persistence across sessions.
    """
    settings = {
        "width": camera.width,
        "height": camera.height,
        "is_fullscreen": getattr(menu, 'is_fullscreen', False),
        "volume": getattr(menu, 'volume', 80)
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving settings: {e}")

# =============================================================================
# --- TACTICAL DEBUG & UI SYSTEM ---
# =============================================================================

class DebugState:
    """
    Manages the toggle states for various on-screen debugging tools 
    available to the developer during runtime.
    """
    def __init__(self):
        self.overlay = False   # F1: Bounding boxes and physics spheres
        self.hud = False       # F2: On-screen telemetry text overlay (FPS, coordinates)
        self.wireframe = False # F3: Global wireframe polygon rendering mode

_debug_font = None
_ui_font = None

def init_fonts():
    """
    Initializes global Pygame fonts used for rendering the UI and debugging overlays.
    Uses fallback standard fonts if the requested system fonts are unavailable.
    """
    global _debug_font, _ui_font
    if _debug_font is None:
        pygame.font.init()
        try:
            _debug_font = pygame.font.SysFont("Courier New", 18, bold=True)
            _ui_font = pygame.font.SysFont("Courier New", 22, bold=True)
        except:
            _debug_font = pygame.font.Font(None, 24)
            _ui_font = pygame.font.Font(None, 28)

def init_debug_font():
    """
    Initializes specifically the debug font instance if not already loaded.
    """
    global _debug_font
    if _debug_font is None:
        pygame.font.init()
        try:
            _debug_font = pygame.font.SysFont("Courier New", 18, bold=True)
        except:
            _debug_font = pygame.font.Font(None, 24)

def draw_debug_text(x, y, text, color=(0, 255, 0)):
    """
    Renders simple unshadowed text to an OpenGL 2D quad for debugging purposes.
    Generates a texture from a Pygame surface on the fly.
    """
    init_debug_font()
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

def create_shadowed_text_texture(text, font, color):
    """
    Creates an OpenGL texture from a Pygame surface containing text with a drop shadow effect.
    Improves UI readability against complex 3D backgrounds.
    
    Returns:
        tex_id: The OpenGL texture ID.
        cw, ch: The width and height of the generated texture.
    """
    main_surf = font.render(text, True, color)
    shadow_surf = font.render(text, True, (10, 10, 10)) 
    
    offset = 2 
    w, h = main_surf.get_size()
    
    combined_surf = pygame.Surface((w + offset, h + offset), pygame.SRCALPHA)
    combined_surf.blit(shadow_surf, (offset, offset)) 
    combined_surf.blit(main_surf, (0, 0))             
    
    text_data = pygame.image.tobytes(combined_surf, "RGBA", False)
    cw, ch = combined_surf.get_size()
    
    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, cw, ch, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    
    return tex_id, cw, ch

def draw_game_ui(width, height, remaining_time, action_text=None, notification_text=None):
    """
    Renders the main gameplay heads-up display (HUD).
    Draws the pause reminder, countdown timer, central crosshair interaction text, 
    and system notifications (like collecting keys) using Orthographic projection.
    """
    init_fonts()
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    
    glColor4f(1.0, 1.0, 1.0, 1.0) 
    
    # 1. PAUSE INDICATOR 
    pause_text = "[ESC] Pause"
    tex_p, w_p, h_p = create_shadowed_text_texture(pause_text, _ui_font, (220, 220, 220))
    glBindTexture(GL_TEXTURE_2D, tex_p)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(25, 25)
    glTexCoord2f(1, 0); glVertex2f(25 + w_p, 25)
    glTexCoord2f(1, 1); glVertex2f(25 + w_p, 25 + h_p)
    glTexCoord2f(0, 1); glVertex2f(25, 25 + h_p)
    glEnd()
    glDeleteTextures([tex_p])
    
    # 2. COUNTDOWN TIMER 
    minutes = max(0, int(remaining_time) // 60)
    seconds = max(0, int(remaining_time) % 60)
    timer_text = f"{minutes:02d}:{seconds:02d}"
    
    # Turn timer red if there are 3 minutes (180 seconds) or less remaining
    timer_color = (255, 60, 60) if remaining_time < 180.0 else (240, 240, 240)
    tex_t, w_t, h_t = create_shadowed_text_texture(timer_text, _ui_font, timer_color)
    x_pos_timer = width - w_t - 25
    
    glBindTexture(GL_TEXTURE_2D, tex_t)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x_pos_timer, 25)
    glTexCoord2f(1, 0); glVertex2f(x_pos_timer + w_t, 25)
    glTexCoord2f(1, 1); glVertex2f(x_pos_timer + w_t, 25 + h_t)
    glTexCoord2f(0, 1); glVertex2f(x_pos_timer, 25 + h_t)
    glEnd()
    glDeleteTextures([tex_t])

    # 3. INTERACTION INDICATOR
    if action_text:
        tex_i, w_i, h_i = create_shadowed_text_texture(action_text, _ui_font, (255, 255, 255))
        x_pos_interact = (width - w_i) // 2
        y_pos_interact = 40 
        glBindTexture(GL_TEXTURE_2D, tex_i)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x_pos_interact, y_pos_interact)
        glTexCoord2f(1, 0); glVertex2f(x_pos_interact + w_i, y_pos_interact)
        glTexCoord2f(1, 1); glVertex2f(x_pos_interact + w_i, y_pos_interact + h_i)
        glTexCoord2f(0, 1); glVertex2f(x_pos_interact, y_pos_interact + h_i)
        glEnd()
        glDeleteTextures([tex_i])

    # 4. NOTIFICATION INDICATOR (For Key Collection)
    if notification_text:
        tex_n, w_n, h_n = create_shadowed_text_texture(notification_text, _ui_font, (255, 255, 100)) # Yellowish text
        x_pos_notif = (width - w_n) // 2
        y_pos_notif = 80 
        glBindTexture(GL_TEXTURE_2D, tex_n)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x_pos_notif, y_pos_notif)
        glTexCoord2f(1, 0); glVertex2f(x_pos_notif + w_n, y_pos_notif)
        glTexCoord2f(1, 1); glVertex2f(x_pos_notif + w_n, y_pos_notif + h_n)
        glTexCoord2f(0, 1); glVertex2f(x_pos_notif, y_pos_notif + h_n)
        glEnd()
        glDeleteTextures([tex_n])
    
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_FOG)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_crosshair(width, height):
    """
    Renders a stylized crosshair in the center of the screen using basic OpenGL primitives.
    It consists of an inner shadow and an outer bright layer to remain visible on both dark and bright backgrounds.
    """
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_FOG)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    cx = width // 2
    cy = height // 2
    
    t = 1.0  # Thickness
    s = 8.0  # Length
    g = 4.0  # Gap from center
    o = 1.5  # Outline offset
    
    def draw_rect(x1, x2, y1, y2):
        glBegin(GL_QUADS)
        glVertex2f(x1, y1); glVertex2f(x2, y1)
        glVertex2f(x2, y2); glVertex2f(x1, y2)
        glEnd()
    
    # Draw shadow outlines
    glColor4f(0.0, 0.0, 0.0, 0.85) 
    draw_rect(cx - g - s - o, cx - g + o, cy - t - o, cy + t + o)
    draw_rect(cx + g - o, cx + g + s + o, cy - t - o, cy + t + o)
    draw_rect(cx - t - o, cx + t + o, cy - g - s - o, cy - g + o)
    draw_rect(cx - t - o, cx + t + o, cy + g - o, cy + g + s + o)
    
    # Draw main bright crosshair
    glColor4f(1.0, 1.0, 1.0, 0.95)
    draw_rect(cx - g - s, cx - g, cy - t, cy + t)
    draw_rect(cx + g, cx + g + s, cy - t, cy + t)
    draw_rect(cx - t, cx + t, cy - g - s, cy - g)
    draw_rect(cx - t, cx + t, cy + g, cy + g + s)
    
    glDisable(GL_BLEND)
    glEnable(GL_FOG)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_debug_visuals(camera, house, setting_doors, is_wireframe_global):
    """
    Renders physical bounds, collision spheres, and wireframes when debug mode is active.
    Helps developers visualize what the physics engine is calculating vs what is visually rendered.
    """
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glDisable(GL_DEPTH_TEST) 

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(1.5)

    # Draw environmental collision triangles
    glColor3f(0.0, 1.0, 0.0) 
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

    # Draw player bounding spheres
    if hasattr(camera, 'feet_pos'):
        glColor3f(1.0, 0.0, 0.0) 
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

    # Restore polygon rendering modes based on state
    if is_wireframe_global:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_FOG)

def setup_fog(density):
    """
    Configures global OpenGL exponential fog parameters to create an atmospheric mystery effect.
    The fog density limits visibility and helps mask draw distance limitations.
    """
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, density)
    fog_color = [0.25, 0.26, 0.30, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    glHint(GL_FOG_HINT, GL_NICEST)

def setup_display():
    """
    Initializes the Pygame environment, creates the display window, and sets up the OpenGL context.
    Reads saved settings to determine resolution and fullscreen state.
    """
    os.environ['SDL_VIDEO_CENTERED'] = "mouse"
    pygame.init()
    
    settings = load_settings()
    info = pygame.display.Info()
    
    screen_width = settings["width"]
    screen_height = settings["height"]
    
    if screen_width == 0 or screen_height == 0:
        screen_width = info.current_w
        screen_height = info.current_h - 60 
    
    flags = DOUBLEBUF | OPENGL | RESIZABLE
    if settings["is_fullscreen"]:
        flags |= FULLSCREEN
        
    pygame.display.set_mode((screen_width, screen_height), flags)
    pygame.display.set_caption("Evidence - Resolve the Mystery")
    
    return screen_width, screen_height, settings

def setup_camera(screen_width, screen_height):
    """
    Instantiates the standard FPS interaction camera with initial transform look parameters
    and gameplay variables (inventory, timers).
    """
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    camera.pos_x = 0.0 
    camera.pos_y = 1.65
    camera.pos_z = 0.0   
    camera.pitch = -45.0 
    camera.yaw = -90.0   

    # Variables for inventory and notifications
    camera.has_key = False
    camera.key_message_timer = 0.0

    camera.update_camera_vectors()
    return camera

def setup_skybox():
    """
    Maps architectural asset texturing locations to instantiate the environmental Skybox
    that surrounds the 3D map bounds.
    """
    skybox_paths = {
        'posz': 'source/textures/posz.jpg',
        'posx': 'source/textures/posx.jpg',
        'negz': 'source/textures/negz.jpg',
        'posy': 'source/textures/posy.jpg',
        'negx': 'source/textures/negx.jpg',
        'negy': 'source/textures/negy.jpg',
    }
    return Skybox(skybox_paths)

def process_game_event(event, menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui):
    """
    Handles core gameplay input events, specifically object inspection, door interaction, 
    and triggering of debug modes. Returns the currently inspected object.
    """
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            menu.state = 'MENU'
            audio.play_sfx("ui_click")
        elif event.key == pygame.K_e:
            if inspected_object:
                # Drop the object currently being inspected
                inspected_object.reset_rotation()
                inspected_object = None
            else:
                grabbed = False
                looked_obj = None
                
                # Check for collision against all inspectable items in the world
                for obj in setting_inspectables:
                    if obj.can_be_inspected(camera.pos_x, camera.pos_y, camera.pos_z, camera.front_x, camera.front_y, camera.front_z):
                        
                        # Block key interaction if the safe is closed
                        if getattr(obj, 'name', '') == 'Key':
                            safe_door = next((d for d in setting_doors if getattr(d, 'is_safe', False)), None)
                            if safe_door and not getattr(safe_door, 'is_open', False):
                                continue # Pretend the key is not there and keep scanning
                                
                        looked_obj = obj

                        obj_name = getattr(obj, 'name', '').lower()
                        obj_mats = "".join(getattr(obj, 'mat_names', [])).lower()

                        # TRIGGER: Detect object type name to play specific environmental SFX
                        if "botella" in obj_name or "glass" in obj_name or "botella" in obj_mats:
                            audio.play_sfx("inspect_glass")
                        elif "papel" in obj_name or "paper" in obj_name or "nota" in obj_name or "nota" in obj_mats:
                            audio.play_sfx("inspect_paper")
                        elif "machete" in obj_name or "knife" in obj_name or "machete" in obj_mats:
                            audio.play_sfx("inspect_knife")
                        else:
                            audio.play_sfx("ui_click") # Default fallback
                        break
                
                if looked_obj:
                    # If the object is the key, collect it instead of opening the inspection UI
                    if getattr(looked_obj, 'name', '') == 'Key':
                        camera.has_key = True
                        camera.key_message_timer = 3.0 # Show text for 3 seconds
                        setting_inspectables.remove(looked_obj) # Remove from world geometry
                        grabbed = True
                    else:
                        inspected_object = looked_obj
                        grabbed = True
                
                # If no object was grabbed, attempt to interact with doors
                if not grabbed:
                    toggle_nearest_visible_door(setting_doors, house, camera, audio, safe_ui)
            
        elif event.key == pygame.K_F1:
            debug_state.overlay = not debug_state.overlay
            audio.play_sfx("ui_click")
            
        elif event.key == pygame.K_F2:
            debug_state.hud = not debug_state.hud
            audio.play_sfx("ui_click")
            
        elif event.key == pygame.K_F3:
            debug_state.wireframe = not debug_state.wireframe
            audio.play_sfx("ui_click")
            if debug_state.wireframe:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                
    return inspected_object

def handle_events(menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui):
    """
    Main event routing function. Dispatches Pygame window inputs to the active UI state
    (Menu, Safe interface, or Gameplay physics).
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, inspected_object

        # Handle dynamic window resizing
        if event.type == pygame.VIDEORESIZE:
            glViewport(0, 0, event.w, event.h)
            camera.width = event.w
            camera.height = event.h
            camera.configure_projection()
            
            menu.width = event.w
            menu.height = event.h
            menu.center_x = event.w // 2
            menu.center_y = event.h // 2
            menu.options_start_y = menu.center_y + 20

        # Route inputs to menu systems
        if menu.state in ['MENU', 'OPTIONS', 'GAME_OVER']:
            menu.handle_input(event, camera, audio)
            
            if menu.state == 'QUIT':
                return False, inspected_object
                
        elif menu.state == 'GAME':
            # Route input to Safe UI if active, suppressing normal movement/look
            if safe_ui.active:
                unlocked = safe_ui.handle_event(event, audio)
                if unlocked:
                    for door in setting_doors:
                        if getattr(door, 'is_safe', False):
                            door.is_locked = False
                            door.toggle() 
                            audio.play_sfx("safe_open")
            else:
                # Process standard game physics and interaction
                inspected_object = process_game_event(event, menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui)
        
    # Real-time dynamic volume tracking during settings adjustments
    if menu.state == 'OPTIONS':
        audio.set_volume(menu.volume)

    return True, inspected_object

def render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt, clock, debug_state, game_time, house_display_list, static_colliders, current_fog_density, audio, setting_inspectables, inspected_object, safe_ui):
    """
    Executes specific screen clear procedures and orchestrates the rendering of UI matrices 
    or 3D spatial geometry depending on the active game state. Also handles physics integration steps.
    """
    _updated_density = current_fog_density
    glClearColor(0.25, 0.26, 0.30, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Manage mouse capture state (free mouse for UI, locked cursor for FPS gameplay)
    needs_mouse_visible = (menu.state in ['MENU', 'OPTIONS', 'GAME_OVER']) or safe_ui.active
    
    if getattr(camera, 'mouse_visible_state', None) != needs_mouse_visible:
        if needs_mouse_visible:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        else:
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
        camera.mouse_visible_state = needs_mouse_visible

    # Render Active Menu States
    if menu.state in ['MENU', 'OPTIONS', 'GAME_OVER']:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        menu.render()
    else:
        # Render Gameplay State
        if safe_ui.active:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        else:
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
        
        dx, dy = pygame.mouse.get_rel()
        
        # Apply mouse deltas to camera rotation or object inspection rotation
        if not safe_ui.active:
            if inspected_object:
                inspected_object.rot_y += dx * 0.5
                inspected_object.rot_x += dy * 0.5
            else:
                camera.process_mouse(dx, dy)
        
        # SPATIAL PARTITIONING: 3D GRID-BASED COLLISION CULLING
        CELL_SIZE = 2.0 

        # Identify the 3D grid cell currently occupied by the player
        cell_x = int(camera.pos_x // CELL_SIZE)
        cell_y = int(camera.pos_y // CELL_SIZE)
        cell_z = int(camera.pos_z // CELL_SIZE)

        nearby_triangles = set()

        # Query the current cell and the 26 surrounding 3D cells (27 cells total, 3x3x3 block)
        for x in range(cell_x - 1, cell_x + 2):
            for y in range(cell_y - 1, cell_y + 1):
                for z in range(cell_z - 1, cell_z + 2):
                    cell_key = (x, y, z)
                    if cell_key in house.grid:
                        nearby_triangles.update(house.grid[cell_key])

        frame_colliders = list(nearby_triangles)

        for door in setting_doors:
            frame_colliders.extend(door.get_transformed_triangles(house))

        # Dynamic fog transitions based on courtyard boundaries coordinates (outdoor vs indoor)
        if (camera.pos_z < -5.8) or (camera.pos_z > 4.0) or (camera.pos_x < -8.5) or (camera.pos_x > 3.8):
            # Player is standing in the outside courtyard (Thinner fog)
            target_density = 0.1
        else:
            # Player is inside the building geometry limits (Thicker fog)
            target_density = 0.17

        interpolation_speed = 1.8
        _updated_density = current_fog_density + (target_density - current_fog_density) * interpolation_speed * dt

        # Process movement keyboard layout
        keys = pygame.key.get_pressed()
        is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        
        # EXECUTE PHYSICS PASS EXCLUSIVELY ON LOCALIZED CULLED COLLIDERS
        if not inspected_object and not safe_ui.active:
            camera.process_keyboard(dt, frame_colliders)
        
        # Phase 1: Render Skybox (Requires depth test off so it draws infinitely far away)
        glDisable(GL_DEPTH_TEST)
        
        glEnable(GL_FOG)
        setup_fog(_updated_density)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(
            0.0, 0.0, 0.0,
            camera.front_x, camera.front_y, camera.front_z,
            0.0, 1.0, 0.0,
        )
        skybox.draw()

        # Phase 2: Render 3D World Geometry
        glEnable(GL_DEPTH_TEST)

        camera.update_view()
        update_doors(setting_doors, dt)

        # Process notifications
        if camera.key_message_timer > 0:
            camera.key_message_timer -= dt
            notification_text = "You have taken the key"
        else:
            notification_text = None

        # Track auditory pacing steps
        is_grounded = getattr(camera, 'is_grounded', True)
        audio.update_footsteps(dt, is_moving, is_grounded)

        # Calculate object inspection lookat rays
        action_text = None
        looked_obj = None
        
        if inspected_object:
            action_text = "Press [E] to Drop"
        else:
            # Scan inspectable items
            for obj in setting_inspectables:
                if obj.can_be_inspected(camera.pos_x, camera.pos_y, camera.pos_z, camera.front_x, camera.front_y, camera.front_z):
                    
                    # Block key text prompt if safe is closed
                    if getattr(obj, 'name', '') == 'Key':
                        safe_door = next((d for d in setting_doors if getattr(d, 'is_safe', False)), None)
                        if safe_door and not getattr(safe_door, 'is_open', False):
                            continue # Ignore the key and keep scanning
                            
                    looked_obj = obj
                    break
            
            if looked_obj:
                # Provide custom text string for the Key
                if getattr(looked_obj, 'name', '') == 'Key':
                    action_text = "Press [E] to take the key"
                else:
                    nombre = getattr(looked_obj, 'name', 'Object')
                    action_text = f"Press [E] to Inspect {nombre}"
            else:
                # If no object was looked at, scan nearby doors
                target_door = get_looked_at_door(setting_doors, house, camera)
                if target_door:
                    if getattr(target_door, 'requires_key', False) and not getattr(camera, 'has_key', False):
                        action_text = "Locked - Key required"
                    else:
                        is_open = getattr(target_door, 'is_open', False)
                        action_text = "Press [E] to Close" if is_open else "Press [E] to Open"

        # Suppress interaction text if Safe UI is blocking the view
        if safe_ui.active:
            action_text = None

        # Execute unified graphics world render pass
        try:
            # Render static mapped geometry from VRAM display list
            glCallList(house_display_list)
            # Render dynamic elements (inspectables, doors, UI popups)
            draw_inspectables_world(setting_inspectables, inspected_object, house, config_visual, looked_obj)
            draw_doors(setting_doors, house, config_visual)
            draw_inspected_hud(inspected_object, house, config_visual)
        except OpenGL.error.Error:
            pass 
        
        # Render 2D Orthographic Overlays on top of the 3D projection matrix scene viewport
        draw_crosshair(camera.width, camera.height)
        draw_game_ui(camera.width, camera.height, game_time, action_text, notification_text)

        # Render Diagnostics Graphics Visual Overlay (F1)
        if debug_state.overlay:
            draw_debug_visuals(camera, house, setting_doors, debug_state.wireframe)

        # Render Telemetry HUD Overlay (F2)
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
            glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING); glDisable(GL_FOG)
            
            draw_debug_text(10, 10, f"FPS  : {current_fps:.1f}", (255, 255, 0))
            draw_debug_text(10, 30, f"XYZ  : {camera.pos_x:.2f}, {camera.pos_y:.2f}, {camera.pos_z:.2f}", (0, 255, 255))
            draw_debug_text(10, 50, f"STATE: {state_str}", (0, 255, 0) if camera.is_grounded else (255, 100, 100))
            
            glEnable(GL_FOG); glEnable(GL_DEPTH_TEST); glMatrixMode(GL_PROJECTION); glPopMatrix(); glMatrixMode(GL_MODELVIEW); glPopMatrix()

        # Update and render the digital Safe Interface on top of everything
        safe_ui.update(dt)
        if safe_ui.active:
            safe_ui.draw(camera.width, camera.height)

    # Swap the display buffers
    pygame.display.flip()
    return _updated_density

def main():
    """
    Primary application entry point.
    Initializes subsystems (Pygame, OpenGL, Audio), preloads asset bundles into VRAM, 
    and handles the primary execution loop routing frames and game time logic.
    """
    screen_width, screen_height, saved_settings = setup_display()

    current_fog_density = 0.04

    # Initialize Audio Subsystem and preload sound effects
    audio = AudioManager()
    audio.set_volume(saved_settings["volume"])

    audio.load_sfx("door_open", "door_open.wav")    
    audio.load_sfx("door_close", "door_close.wav") 
    audio.load_sfx("inspect_paper", "paper_rustle.wav")
    audio.load_sfx("inspect_glass", "glass_clink.wav")
    
    audio.load_sfx("inspect_knife", "knife.wav")
    audio.load_sfx("ui_click", "click.wav")
    audio.load_sfx("footstep", "footstep.wav")
    
    audio.load_sfx("safe_open", "safe_open.wav")
    audio.load_sfx("safe_close", "safe_close.wav")
    audio.load_sfx("safe_error", "safe_error.wav")
    audio.load_sfx("safe_beep", "safe_beep.wav")
    
    audio.load_sfx("timer", "timer.wav")
    audio.load_sfx("you_lose", "you_lose.wav")
    audio.load_sfx("lost", "lost.mp3")
    
    # Start the ambient menu music loop
    audio.play_ambient_music("menu.mp3", loops=-1)
    
    # Initialize Core UI Interfaces
    menu = MainMenu(screen_width, screen_height)
    safe_ui = SafeInterface() 
    
    # Apply previously saved UI configurations
    menu.is_fullscreen = saved_settings["is_fullscreen"]
    menu.volume = saved_settings["volume"]
    
    camera = setup_camera(screen_width, screen_height)
    skybox = setup_skybox()
    
    debug_state = DebugState()
    game_time = 15 * 60  # 15 minutes detective exploration session timer limit
    
    # Render loading screen to cover map compilation hitches
    render_loading_screen(screen_width, screen_height, duration=1.5, start_progress=0.0, target_progress=0.85)

    glEnable(GL_DEPTH_TEST)
    setup_fog(current_fog_density)
    
    pygame.event.set_blocked(None)

    # Load 3D map data, material sets, and interactive entity states
    house, config_visual, setting_doors, door_materials, setting_inspectables, inspectable_materials = load_scene_assets()
    
    # Retain a baseline copy to restore upon level restart without hitting RAM/VRAM
    original_inspectables = list(setting_inspectables)
    static_colliders = list(house.colliders)
    
    # --- RENDER OPTIMIZATION: OPENGL DISPLAY LISTS ---
    # Compile the static geometry of the house directly into VRAM to drastically reduce draw calls
    house_display_list = glGenLists(1)
    glNewList(house_display_list, GL_COMPILE)
    draw_static_model(house, config_visual, door_materials, inspectable_materials)
    glEndList()
    
    # Complete loading sequence and flush queued up events
    render_loading_screen(screen_width, screen_height, duration=0.4, start_progress=0.85, target_progress=1.0)
    pygame.event.set_allowed(None) 
    pygame.event.clear() 
    
    clock = pygame.time.Clock()
    running = True
    inspected_object = None

    # Fetch reference to the specific door that ends the game condition
    basement_door = next((d for d in setting_doors if getattr(d, 'mat', '') == "matPuerta6"), None)
    
    # Execution state trackers
    game_over_timer = 0.0
    game_over_phase = 0
    tension_triggered = False
    timer_channel = None
    last_state = 'MENU'

    # --- MAIN EXECUTION LOOP ---
    while running:
        # Cap logic loop at ~60hz / Protect delta time during loading pauses
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05) 

        # Intercept and process game restarts from the UI
        if menu.state == 'RESTART':
            render_loading_screen(camera.width, camera.height, duration=0.8, start_progress=0.0, target_progress=0.85)
            
            # Reset gameplay variables
            game_time = 15 * 60  
            camera.has_key = False
            camera.key_message_timer = 0.0
            inspected_object = None
            
            # Flush safe UI
            safe_ui.active = False
            safe_ui.input_buffer = ""
            safe_ui.error_timer = 0.0
            
            # Restore inspectable items list from backup
            setting_inspectables = list(original_inspectables)
            
            # Close and manually relock all map doors
            for door in setting_doors:
                door.is_open = False
                if hasattr(door, 'current_angle'):
                    door.current_angle = 0.0 
                if getattr(door, 'is_safe', False):
                    door.is_locked = True
                if getattr(door, 'mat', '') == "matPuerta7":
                    door.requires_key = True
            
            render_loading_screen(camera.width, camera.height, duration=0.4, start_progress=0.85, target_progress=1.0)
            
            # Clear state switches
            menu.state = 'GAME'
            pygame.event.clear()
            
            # Revert tension music and initialize default environment audio
            pygame.mixer.music.stop() 
            if timer_channel:
                timer_channel.stop()
            audio.play_ambient_music("suspense_ambient.mp3", loops=-1)
            
            tension_triggered = False
            game_over_phase = 0
            game_over_timer = 0.0
            last_state = 'GAME'

        # Poll operating system window events
        pygame.event.pump()
        running, inspected_object = handle_events(menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui)
        
        # Audio state transitions based on menu activity
        if last_state != menu.state:
            # Entering menus
            if menu.state == 'MENU' and last_state == 'GAME':
                audio.play_ambient_music("menu.mp3", loops=-1)
                if timer_channel:
                    timer_channel.pause()
            # Returning to game
            elif menu.state == 'GAME' and last_state in ['MENU', 'OPTIONS']:
                if tension_triggered:
                    audio.play_ambient_music("few_time.mp3", loops=-1)
                    if timer_channel:
                        timer_channel.unpause()
                else:
                    audio.play_ambient_music("suspense_ambient.mp3", loops=-1)

        last_state = menu.state

        # Active gameplay physics and time progression logic
        if running and menu.state == 'GAME':
            # Stop the countdown if the win condition door is unlocked
            running_time = getattr(basement_door, 'requires_key', True) if basement_door else True
            
            if running_time:
                game_time -= dt
                
                # --- TENSION EVENT: 3 minutes left ---
                if game_time <= 180.0 and not tension_triggered:
                    tension_triggered = True
                    audio.play_ambient_music("few_time.mp3", loops=-1)
                    
                    try:
                        timer_snd = pygame.mixer.Sound("source/audio/sfx/timer.wav") 
                        timer_snd.set_volume(menu.volume / 100.0)
                        timer_channel = timer_snd.play(loops=-1)
                    except Exception as e:
                        print("Error al cargar timer:", e)

                # --- GAME OVER EVENT: Time depleted ---
                if game_time <= 0.0:
                    game_time = 0.0
                    menu.state = 'GAME_OVER'
                    menu.game_over_selection = 0 
                    
                    pygame.mixer.music.stop()
                    if timer_channel:
                        timer_channel.stop()
                        
                    audio.play_sfx("you_lose")
                    game_over_timer = 1.0 
                    game_over_phase = 1   
        
        # Asynchronous audio sequencer for the Game Over screen
        # Runs without blocking the main rendering loop
        if menu.state == 'GAME_OVER' and game_over_phase > 0:
            game_over_timer -= dt 
            
            if game_over_timer <= 0.0:
                if game_over_phase == 1:
                    audio.play_sfx("lost") 
                    game_over_timer = 2.5 
                    game_over_phase = 2
                    
                elif game_over_phase == 2:
                    game_over_phase = 0 

        # Fire unified render pass
        if running:
            current_fog_density = render_frame(
                menu, camera, skybox, house, config_visual, setting_doors, 
                door_materials, dt, clock, debug_state, game_time, 
                house_display_list, static_colliders, current_fog_density, audio,
                setting_inspectables, inspected_object, safe_ui
            )
        
        pygame.event.pump()

    # Triggered post-loop prior to closing handles
    save_settings(camera, menu)
    pygame.quit()

if __name__ == '__main__':
    main()