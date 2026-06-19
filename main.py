import os
import json
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

#PERSISTENCE ENGINE (SAVING)

SETTINGS_FILE = "settings.json"

def load_settings():
    """Loads previous settings. If no file is found, returns default values."""
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
    """Saves the exact state of the window and menu configuration before application exit."""
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
    def __init__(self):
        self.overlay = False   # F1: Bounding boxes and physics spheres
        self.hud = False       # F2: On-screen telemetry text overlay
        self.wireframe = False # F3: Global wireframe polygon rendering mode

_debug_font = None
_ui_font = None

def init_fonts():
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
    global _debug_font
    if _debug_font is None:
        pygame.font.init()
        try:
            _debug_font = pygame.font.SysFont("Courier New", 18, bold=True)
        except:
            _debug_font = pygame.font.Font(None, 24)

def draw_debug_text(x, y, text, color=(0, 255, 0)):
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
    
    timer_color = (255, 60, 60) if remaining_time < 60.0 else (240, 240, 240)
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
    
    t = 1.0  
    s = 8.0  
    g = 4.0  
    o = 1.5  
    
    def draw_rect(x1, x2, y1, y2):
        glBegin(GL_QUADS)
        glVertex2f(x1, y1); glVertex2f(x2, y1)
        glVertex2f(x2, y2); glVertex2f(x1, y2)
        glEnd()
    
    glColor4f(0.0, 0.0, 0.0, 0.85) 
    draw_rect(cx - g - s - o, cx - g + o, cy - t - o, cy + t + o)
    draw_rect(cx + g - o, cx + g + s + o, cy - t - o, cy + t + o)
    draw_rect(cx - t - o, cx + t + o, cy - g - s - o, cy - g + o)
    draw_rect(cx - t - o, cx + t + o, cy + g - o, cy + g + s + o)
    
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
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glDisable(GL_DEPTH_TEST) 

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(1.5)

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

    if is_wireframe_global:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_FOG)

def setup_fog(density):
    """Configures global OpenGL exponential fog parameters for atmospheric mystery effect"""
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, density)
    fog_color = [0.25, 0.26, 0.30, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    glHint(GL_FOG_HINT, GL_NICEST)

def setup_display():
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
    """Instantiates the standard FPS interaction camera with initial transform look parameters"""
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

def process_game_event(event, menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            menu.state = 'MENU'
            audio.play_sfx("ui_click")
        elif event.key == pygame.K_e:
            if inspected_object:
                inspected_object.reset_rotation()
                inspected_object = None
            else:
                grabbed = False
                looked_obj = None
                for obj in setting_inspectables:
                    if obj.can_be_inspected(camera.pos_x, camera.pos_y, camera.pos_z, camera.front_x, camera.front_y, camera.front_z):
                        
                        # Block key interaction if safe is closed ---
                        if getattr(obj, 'name', '') == 'Key':
                            safe_door = next((d for d in setting_doors if getattr(d, 'is_safe', False)), None)
                            if safe_door and not getattr(safe_door, 'is_open', False):
                                continue # Pretend the key is not there and keep scanning
                                
                        looked_obj = obj

                        obj_name = getattr(obj, 'name', '').lower()
                        # Join all materials in a single string to easily scan them (e.g., ['matBotella4'] -> "matbotella4")
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
                    # If the object is the key, collect it instead of inspecting
                    if getattr(looked_obj, 'name', '') == 'Key':
                        camera.has_key = True
                        camera.key_message_timer = 3.0 # Show text for 3 seconds
                        setting_inspectables.remove(looked_obj) # Make it disappear from the world
                        grabbed = True
                    else:
                        inspected_object = looked_obj
                        grabbed = True
                
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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False, inspected_object

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

        if menu.state in ['MENU', 'OPTIONS']:
            menu.handle_input(event, camera, audio)
            
            if menu.state == 'QUIT':
                return False, inspected_object
                
        elif menu.state == 'GAME':
            # Route input to Safe UI if active
            if safe_ui.active:
                unlocked = safe_ui.handle_event(event, audio)
                if unlocked:
                    for door in setting_doors:
                        if getattr(door, 'is_safe', False):
                            door.is_locked = False
                            door.toggle() 
                            audio.play_sfx("safe_open")
            else:
                inspected_object = process_game_event(event, menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui)
        
    # RE-MIXER OPTIMIZATION: Instant dynamic volume tracking during adjustments
    if menu.state == 'OPTIONS':
        audio.set_volume(menu.volume)

    return True, inspected_object

def render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt, clock, debug_state, game_time, house_display_list, static_colliders, current_fog_density, audio, setting_inspectables, inspected_object, safe_ui):
    """Executes specific clear procedures and decides whether to paint UI or 3D spaces matrices"""

    _updated_density = current_fog_density
    glClearColor(0.25, 0.26, 0.30, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    needs_mouse_visible = (menu.state in ['MENU', 'OPTIONS']) or safe_ui.active
    
    if getattr(camera, 'mouse_visible_state', None) != needs_mouse_visible:
        if needs_mouse_visible:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        else:
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
        camera.mouse_visible_state = needs_mouse_visible

    if menu.state in ['MENU', 'OPTIONS']:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        menu.render()
    else:
        if safe_ui.active:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        else:
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
        
        dx, dy = pygame.mouse.get_rel()
        
        # Halt camera movement while interacting with the safe UI
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

        # Dynamic fog transitions based on courtyard boundaries coordinates
        if (camera.pos_z < -5.8) or (camera.pos_z > 4.0) or (camera.pos_x < -8.5) or (camera.pos_x > 3.8):
            # Player is standing in the outside courtyard (Increased density to 0.12 for visibility visibility)
            target_density = 0.1
        else:
            # Player is inside the building geometry limits
            target_density = 0.17

        interpolation_speed = 1.8
        _updated_density = current_fog_density + (target_density - current_fog_density) * interpolation_speed * dt

        # Process movement keyboard layout
        keys = pygame.key.get_pressed()
        is_moving = keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]
        
        # EXECUTE PHYSICS PASS EXCLUSIVELY ON LOCALIZED COLLIDERS
        if not inspected_object and not safe_ui.active:
            camera.process_keyboard(dt, frame_colliders)
        
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
        
        setup_fog(_updated_density)

        camera.update_view()
        update_doors(setting_doors, dt)

        # Determine notifications
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
            for obj in setting_inspectables:
                if obj.can_be_inspected(camera.pos_x, camera.pos_y, camera.pos_z, camera.front_x, camera.front_y, camera.front_z):
                    
                    # --- NEW LOGIC: Block key text prompt if safe is closed ---
                    if getattr(obj, 'name', '') == 'Key':
                        safe_door = next((d for d in setting_doors if getattr(d, 'is_safe', False)), None)
                        if safe_door and not getattr(safe_door, 'is_open', False):
                            continue # Ignore the key and keep scanning
                            
                    looked_obj = obj
                    break
            
            if looked_obj:
                # Custom text for the Key
                if getattr(looked_obj, 'name', '') == 'Key':
                    action_text = "Press [E] to take the key"
                else:
                    nombre = getattr(looked_obj, 'name', 'Object')
                    action_text = f"Press [E] to Inspect {nombre}"
            else:
                target_door = get_looked_at_door(setting_doors, house, camera)
                if target_door:
                    if getattr(target_door, 'requires_key', False) and not getattr(camera, 'has_key', False):
                        action_text = "Locked - Key required"
                    else:
                        is_open = getattr(target_door, 'is_open', False)
                        action_text = "Press [E] to Close" if is_open else "Press [E] to Open"

        # Suppress interaction text if UI is blocking the view
        if safe_ui.active:
            action_text = None

        # 3D RENDERING
        try:
            glCallList(house_display_list)
            draw_inspectables_world(setting_inspectables, inspected_object, house, config_visual, looked_obj)
            draw_doors(setting_doors, house, config_visual)
            draw_inspected_hud(inspected_object, house, config_visual)
        except OpenGL.error.Error:
            pass 
        
        # Render 2D Overlays on top of the 3D projection matrix scene viewport
        draw_crosshair(camera.width, camera.height)
        
        # ADD NOTIFICATION TEXT TO DRAW CALL
        draw_game_ui(camera.width, camera.height, game_time, action_text, notification_text)

        # 1. Diagnostics Graphics Visual Overlay (F1)
        if debug_state.overlay:
            draw_debug_visuals(camera, house, setting_doors, debug_state.wireframe)

        # 2. Telemetry HUD Overlay (F2)
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

        # UPDATE AND DRAW SAFE INTERFACE ON TOP OF EVERYTHING
        safe_ui.update(dt)
        if safe_ui.active:
            safe_ui.draw(camera.width, camera.height)

    pygame.display.flip()
    return _updated_density

def main():
    screen_width, screen_height, saved_settings = setup_display()

    current_fog_density = 0.04

    # Initialize AudioManager
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
    
    audio.play_ambient_music("suspense_ambient.mp3", loops=-1)

    # Initialize Core interface
    menu = MainMenu(screen_width, screen_height)
    safe_ui = SafeInterface() # INITIALIZE SAFE UI
    
    menu.is_fullscreen = saved_settings["is_fullscreen"]
    menu.volume = saved_settings["volume"]
    
    camera = setup_camera(screen_width, screen_height)
    skybox = setup_skybox()
    
    debug_state = DebugState()
    game_time = 15 * 60  # 15 minutes detective exploration session timer limit
    
    render_loading_screen(screen_width, screen_height, duration=1.5, start_progress=0.0, target_progress=0.85)

    glEnable(GL_DEPTH_TEST)
    setup_fog(current_fog_density)
    
    pygame.event.set_blocked(None)

    house, config_visual, setting_doors, door_materials, setting_inspectables, inspectable_materials = load_scene_assets()
    
    static_colliders = list(house.colliders)
    
    # --- RENDER OPTIMIZATION: OPENGL DISPLAY LISTS ---
    # Compile the static geometry of the house directly into VRAM to drastically reduce draw calls
    house_display_list = glGenLists(1)
    glNewList(house_display_list, GL_COMPILE)
    draw_static_model(house, config_visual, door_materials, inspectable_materials)
    glEndList()
    
    render_loading_screen(screen_width, screen_height, duration=0.4, start_progress=0.85, target_progress=1.0)
    
    pygame.event.set_allowed(None) 
    pygame.event.clear() 
    
    clock = pygame.time.Clock()
    running = True
    
    inspected_object = None

    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05) 

        pygame.event.pump()
        running, inspected_object = handle_events(menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui)
        
        if running and menu.state == 'GAME':
            game_time -= dt
            if game_time <= 0.0:
                game_time = 0.0
                running = False 
        
        if running:
            current_fog_density = render_frame(
                menu, camera, skybox, house, config_visual, setting_doors, 
                door_materials, dt, clock, debug_state, game_time, 
                house_display_list, static_colliders, current_fog_density, audio,
                setting_inspectables, inspected_object, safe_ui
            )
        
        pygame.event.pump()

    save_settings(camera, menu)
    pygame.quit()

if __name__ == '__main__':
    main()