import os
import json
from time import sleep
import pygame
import math
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
from portfolio_interface import PortfolioInterface 
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
# --- INTERNATIONALIZATION (i18n) SYSTEM ---
# =============================================================================

def load_language():
    lang_code = "en"
    if os.path.exists("settings.json"):
        try:
            with open("settings.json", "r") as f:
                lang_code = json.load(f).get("language", "en")
        except: pass
    try:
        with open(f"source/locales/{lang_code}.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {}

LANG = load_language()

TUTORIAL_TEXTS = [
    LANG.get("tut_1", ""), LANG.get("tut_2", ""), LANG.get("tut_3", ""), LANG.get("tut_4", ""),
    LANG.get("tut_5", ""), LANG.get("tut_6", ""), LANG.get("tut_7", ""), LANG.get("tut_8", "")
]

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
        "width": 0,          
        "height": 0,
        "is_fullscreen": False,
        "volume": 80,
        "language": "en"
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
        "volume": getattr(menu, 'volume', 80),
        "language": getattr(menu, 'language', 'en')
    }
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except Exception as e:
        print(f"Error saving settings: {e}")
        

class CinematicState:
    def __init__(self):
        self.active = False
        self.text_index = 0
        self.current_lerp = 0.0
        self.started_game = False

# =============================================================================
# --- TACTICAL DEBUG & UI SYSTEM ---
# =============================================================================

class DebugState:
    """
    Manages the toggle states for various on-screen debugging tools.
    """
    def __init__(self):
        self.overlay = False   
        self.hud = False       
        self.wireframe = False 

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
    """
    Creates an OpenGL texture from a Pygame surface containing text with a drop shadow effect.
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

def draw_game_ui(width, height, remaining_time, action_text=None, notification_text=None, portfolio_ui=None, menu=None, cinematic=None):
    """
    Renders the main gameplay heads-up display (HUD).
    Draws the pause reminder, countdown timer, central crosshair interaction text, 
    and system notifications using Orthographic projection.
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
    
    # CINEMATIC TUTORIAL OVERLAY
    if menu and menu.state == 'CINEMATIC' and cinematic:
        glDisable(GL_TEXTURE_2D)
        glColor4f(0.0, 0.0, 0.0, 1.0)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(width, 0)
        glVertex2f(width, 100); glVertex2f(0, 100)
        glVertex2f(0, height - 150); glVertex2f(width, height - 150)
        glVertex2f(width, height); glVertex2f(0, height)
        glEnd()
        glEnable(GL_TEXTURE_2D)
        
        glColor4f(1.0, 1.0, 1.0, 1.0)
        
        if cinematic.text_index < len(TUTORIAL_TEXTS):
            text_to_show = TUTORIAL_TEXTS[cinematic.text_index]
            words = text_to_show.split(' ')
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                w, _ = _ui_font.size(' '.join(current_line))
                if w > width * 0.8: 
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            if current_line:
                lines.append(' '.join(current_line))
                
            y_offset = height - 110
            for line in lines:
                tex_tut, w_tut, h_tut = create_shadowed_text_texture(line, _ui_font, (255, 255, 255))
                x_tut = (width - w_tut) // 2
                glBindTexture(GL_TEXTURE_2D, tex_tut)
                glBegin(GL_QUADS)
                glTexCoord2f(0, 0); glVertex2f(x_tut, y_offset)
                glTexCoord2f(1, 0); glVertex2f(x_tut + w_tut, y_offset)
                glTexCoord2f(1, 1); glVertex2f(x_tut + w_tut, y_offset + h_tut)
                glTexCoord2f(0, 1); glVertex2f(x_tut, y_offset + h_tut)
                glEnd()
                glDeleteTextures([tex_tut])
                y_offset += h_tut + 5
                
            tex_skip, w_skip, h_skip = create_shadowed_text_texture(LANG.get("cinematic_next", "Next [ENTER]"), _debug_font, (150, 150, 150))
            x_skip = width - w_skip - 25
            y_skip = height - h_skip - 25
            glBindTexture(GL_TEXTURE_2D, tex_skip)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x_skip, y_skip)
            glTexCoord2f(1, 0); glVertex2f(x_skip + w_skip, y_skip)
            glTexCoord2f(1, 1); glVertex2f(x_skip + w_skip, y_skip + h_skip)
            glTexCoord2f(0, 1); glVertex2f(x_skip, y_skip + h_skip)
            glEnd()
            glDeleteTextures([tex_skip])
            
        else:
            tex_skip, w_skip, h_skip = create_shadowed_text_texture(LANG.get("cinematic_skip", "Skip [ENTER]"), _debug_font, (150, 150, 150))
            x_skip = width - w_skip - 25
            y_skip = height - h_skip - 25
            glBindTexture(GL_TEXTURE_2D, tex_skip)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 0); glVertex2f(x_skip, y_skip)
            glTexCoord2f(1, 0); glVertex2f(x_skip + w_skip, y_skip)
            glTexCoord2f(1, 1); glVertex2f(x_skip + w_skip, y_skip + h_skip)
            glTexCoord2f(0, 1); glVertex2f(x_skip, y_skip + h_skip)
            glEnd()
            glDeleteTextures([tex_skip])
            
        glDisable(GL_TEXTURE_2D); glDisable(GL_BLEND); glEnable(GL_FOG); glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION); glPopMatrix()
        glMatrixMode(GL_MODELVIEW); glPopMatrix()
        return
    
    # 1. PAUSE INDICATOR 
    pause_text = LANG.get("hud_pause", "[ESC] Pause")
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

    # 4. NOTIFICATION INDICATOR
    if notification_text:
        tex_n, w_n, h_n = create_shadowed_text_texture(notification_text, _ui_font, (255, 255, 100))
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

    # 5. PORTFOLIO INDICATOR (Bottom Right)
    if portfolio_ui and portfolio_ui.tex_portfolio is not None:
        icon_w, icon_h = 130, 110
        icon_x = width - icon_w - 25
        icon_y = height - icon_h - 25
        
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, portfolio_ui.tex_portfolio)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(icon_x, icon_y)
        glTexCoord2f(1, 1); glVertex2f(icon_x + icon_w, icon_y)
        glTexCoord2f(1, 0); glVertex2f(icon_x + icon_w, icon_y + icon_h)
        glTexCoord2f(0, 0); glVertex2f(icon_x, icon_y + icon_h)
        glEnd()
        
        try:
            q_font = pygame.font.SysFont("times new roman, georgia, serif", 26, bold=True)
        except:
            q_font = _ui_font
            
        q_surf = q_font.render("[Q]", True, (15, 15, 15)) 
        w_q, h_q = q_surf.get_size()
        q_data = pygame.image.tobytes(q_surf, "RGBA", False)
        
        tex_q = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_q)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w_q, h_q, 0, GL_RGBA, GL_UNSIGNED_BYTE, q_data)
        
        q_x = icon_x + (icon_w - w_q) // 2
        q_y = icon_y + (icon_h - h_q) // 2
        
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBindTexture(GL_TEXTURE_2D, tex_q)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(q_x, q_y)
        glTexCoord2f(1, 0); glVertex2f(q_x + w_q, q_y)
        glTexCoord2f(1, 1); glVertex2f(q_x + w_q, q_y + h_q)
        glTexCoord2f(0, 1); glVertex2f(q_x, q_y + h_q)
        glEnd()
        glDeleteTextures([tex_q])
    
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
    Renders a stylized crosshair in the center of the screen.
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
    """
    Renders physical bounds, collision spheres, and wireframes when debug mode is active.
    """
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
    """
    Configures global OpenGL exponential fog parameters to create an atmospheric mystery effect.
    """
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, density)
    fog_color = [0.25, 0.26, 0.30, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    glHint(GL_FOG_HINT, GL_NICEST)
    
def setup_advanced_lighting():
    """
    Initializes advanced OpenGL lighting with custom attenuation parameters 
    to prevent light from bleeding through walls in adjacent rooms.
    """
    glEnable(GL_LIGHTING)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glShadeModel(GL_SMOOTH)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.15, 0.15, 0.15, 1.0])
    
    # Lamp1
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.9, 0.8, 1.0]) 
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.22)      
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.20)   

    # Lamp2
    glEnable(GL_LIGHT1)
    dim_diffuse = [0.2, 0.10, 0.12, 1.0]
    dim_specular = [0.3, 0.3, 0.3, 1.0]
    glLightfv(GL_LIGHT1, GL_DIFFUSE, dim_diffuse) 
    glLightfv(GL_LIGHT1, GL_SPECULAR, dim_specular)
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, 0.22)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, 0.20)

    # Lamp3
    glEnable(GL_LIGHT2)
    glLightfv(GL_LIGHT2, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
    glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)
    glLightf(GL_LIGHT2, GL_LINEAR_ATTENUATION, 0.22)
    glLightf(GL_LIGHT2, GL_QUADRATIC_ATTENUATION, 0.20)

def setup_display():
    os.environ['SDL_VIDEO_CENTERED'] = "mouse"
    pygame.init()
    
    try:
        icon_img = pygame.image.load("source/icons/icon.jpg").convert()
        pygame.display.set_icon(icon_img)
    except Exception as e:
        print("window icon error:", e)
    
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
    pygame.display.set_caption(LANG.get("window_title", "Evidence - Resolve the Mystery"))
    
    return screen_width, screen_height, settings

def setup_camera(screen_width, screen_height):
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    camera.pos_x = 2.37 
    camera.pos_y = 1.65
    camera.pos_z = -8.48   
    camera.pitch = 0.0 
    camera.yaw = 90.0

    # Variables for inventory and notifications
    camera.has_key = False
    camera.notification_timer = 0.0
    camera.notification_message = ""

    camera.update_camera_vectors()
    return camera

def setup_skybox():
    skybox_paths = {
        'posz': 'source/textures/posz.jpg',
        'posx': 'source/textures/posx.jpg',
        'negz': 'source/textures/negz.jpg',
        'posy': 'source/textures/posy.jpg',
        'negx': 'source/textures/negx.jpg',
        'negy': 'source/textures/negy.jpg',
    }
    return Skybox(skybox_paths)

def process_game_event(event, menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui, portfolio_ui):
    """
    Handles core gameplay input events, specifically object inspection, note collection, 
    door interaction, and triggering of debug modes. Returns the currently inspected object.
    """
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
                        
                        if getattr(obj, 'name', '') == 'Key':
                            safe_door = next((d for d in setting_doors if getattr(d, 'is_safe', False)), None)
                            if safe_door and not getattr(safe_door, 'is_open', False):
                                continue 
                                
                        looked_obj = obj

                        obj_name = getattr(obj, 'name', '').lower()
                        obj_mats = "".join(getattr(obj, 'mat_names', [])).lower()

                        if "botella" in obj_name or "glass" in obj_name or "botella" in obj_mats:
                            audio.play_sfx("inspect_glass")
                        elif "papel" in obj_name or "paper" in obj_name or "nota" in obj_name or "nota" in obj_mats:
                            audio.play_sfx("inspect_paper")
                        elif "machete" in obj_name or "knife" in obj_name or "machete" in obj_mats:
                            audio.play_sfx("inspect_knife")
                        else:
                            audio.play_sfx("ui_click") 
                        break
                
                if looked_obj:
                    if getattr(looked_obj, 'name', '') == 'Key':
                        camera.has_key = True
                        camera.notification_timer = 3.0
                        camera.notification_message = LANG.get("hud_key_taken", "")
                        setting_inspectables.remove(looked_obj) 
                        grabbed = True
                    else:
                        obj_name = getattr(looked_obj, 'name', '').lower()
                        obj_mats = [m.lower() for m in getattr(looked_obj, 'mat_names', [])]
                        
                        # Note recognition logic
                        is_note = False
                        note_id = "matnota" 
                        
                        if "nota" in obj_name:
                            is_note = True
                            
                        for m in obj_mats:
                            if "nota" in m:
                                is_note = True
                                note_id = m
                                break
                                
                        if is_note:
                            # Transfer to portfolio array and remove from world
                            portfolio_ui.add_note(f"note_{note_id}")
                            audio.play_sfx("inspect_paper")
                            camera.notification_timer = 3.0
                            camera.notification_message = LANG.get("hud_note_added", "")
                            setting_inspectables.remove(looked_obj)
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

def handle_events(menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui, portfolio_ui, cinematic):
    """
    Main event routing function. Dispatches Pygame window inputs to the active UI state
    (Menu, Safe interface, Portfolio UI, or Gameplay physics).
    """
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

        if menu.state in ['MENU', 'OPTIONS', 'GAME_OVER', 'CREDITS']:
            if menu.state == 'MENU' and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                menu.state = 'GAME'
                if audio: audio.play_sfx("ui_click")
                continue
                
            menu.handle_input(event, camera, audio)
            
            if menu.state == 'QUIT':
                return False, inspected_object
                
        elif menu.state == 'CINEMATIC':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                if audio: audio.play_sfx("ui_click") 
                
                if cinematic.text_index < len(TUTORIAL_TEXTS):
                    cinematic.text_index += 1
                else:
                    cinematic.current_lerp = 1.0
                    
        elif menu.state == 'GAME':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                if not safe_ui.active: 
                    portfolio_ui.active = not portfolio_ui.active
                    if portfolio_ui.active:
                        audio.play_sfx("inspect_paper")
                    continue 

            if safe_ui.active:
                unlocked = safe_ui.handle_event(event, audio)
                if unlocked:
                    for door in setting_doors:
                        if getattr(door, 'is_safe', False):
                            door.is_locked = False
                            door.toggle() 
                            audio.play_sfx("safe_open")
            elif portfolio_ui.active:
                portfolio_ui.handle_event(event, audio)
            else:
                inspected_object = process_game_event(event, menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui, portfolio_ui)
        
    if menu.state == 'OPTIONS':
        audio.set_volume(menu.volume)

    return True, inspected_object

def render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt, clock, debug_state, game_time, house_display_list, static_colliders, current_fog_density, audio, setting_inspectables, inspected_object, safe_ui, portfolio_ui, cinematic):
    """
    Executes specific screen clear procedures and orchestrates the rendering of UI matrices 
    or 3D spatial geometry depending on the active game state.
    """
    _updated_density = current_fog_density
    glClearColor(0.25, 0.26, 0.30, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    needs_mouse_visible = (menu.state in ['MENU', 'OPTIONS', 'GAME_OVER', 'CREDITS']) or safe_ui.active or portfolio_ui.active
    
    if getattr(camera, 'mouse_visible_state', None) != needs_mouse_visible:
        if needs_mouse_visible:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        else:
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
        camera.mouse_visible_state = needs_mouse_visible

    if menu.state in ['MENU', 'OPTIONS', 'GAME_OVER', 'CREDITS']:
        pygame.event.set_grab(False)
        pygame.mouse.set_visible(True)
        menu.render()
    else:
        if safe_ui.active or portfolio_ui.active:
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
        else:
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
        
        dx, dy = pygame.mouse.get_rel()
        
        if not safe_ui.active and not portfolio_ui.active and menu.state != 'CINEMATIC':
            if inspected_object:
                inspected_object.rot_y += dx * 0.5
                inspected_object.rot_x += dy * 0.5
            else:
                camera.process_mouse(dx, dy)
        
        # SPATIAL PARTITIONING
        CELL_SIZE = 2.0 

        cell_x = int(camera.pos_x // CELL_SIZE)
        cell_y = int(camera.pos_y // CELL_SIZE)
        cell_z = int(camera.pos_z // CELL_SIZE)

        nearby_triangles = set()

        for x in range(cell_x - 1, cell_x + 2):
            for y in range(cell_y - 1, cell_y + 1):
                for z in range(cell_z - 1, cell_z + 2):
                    cell_key = (x, y, z)
                    if cell_key in house.grid:
                        nearby_triangles.update(house.grid[cell_key])

        frame_colliders = list(nearby_triangles)

        for door in setting_doors:
            frame_colliders.extend(door.get_transformed_triangles(house))

        if (camera.pos_z < -5.8) or (camera.pos_z > 4.0) or (camera.pos_x < -8.5) or (camera.pos_x > 3.8):
            target_density = 0.1
        else:
            target_density = 0.17

        interpolation_speed = 1.8
        _updated_density = current_fog_density + (target_density - current_fog_density) * interpolation_speed * dt

        keys = pygame.key.get_pressed()
        
        is_moving = (keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or keys[pygame.K_d]) and menu.state != 'CINEMATIC'
        
        if not inspected_object and not safe_ui.active and not portfolio_ui.active and menu.state != 'CINEMATIC':
            camera.process_keyboard(dt, frame_colliders)
        
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
        
        glDisable(GL_LIGHTING) 
        skybox.draw()

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        camera.update_view()
        
        lamp_position_1 = [-0.351, 2.6602, 2.1109, 1.0] 
        glLightfv(GL_LIGHT0, GL_POSITION, lamp_position_1)
        
        lamp_position_2 = [-6.6994, 2.6715, 2.1109, 1.0] 
        glLightfv(GL_LIGHT1, GL_POSITION, lamp_position_2)

        lamp_position_3 = [2.8231, -0.031169, -2.6032, 1.0]
        glLightfv(GL_LIGHT2, GL_POSITION, lamp_position_3)

        update_doors(setting_doors, dt)

        if camera.notification_timer > 0:
            camera.notification_timer -= dt
            notification_text = camera.notification_message
        else:
            notification_text = None

        is_grounded = getattr(camera, 'is_grounded', True)
        audio.update_footsteps(dt, is_moving, is_grounded)

        action_text = None
        looked_obj = None
        
        if inspected_object:
            action_text = LANG.get("hud_press_drop", "")
        else:
            for obj in setting_inspectables:
                if obj.can_be_inspected(camera.pos_x, camera.pos_y, camera.pos_z, camera.front_x, camera.front_y, camera.front_z):
                    
                    if getattr(obj, 'name', '') == 'Key':
                        safe_door = next((d for d in setting_doors if getattr(d, 'is_safe', False)), None)
                        if safe_door and not getattr(safe_door, 'is_open', False):
                            continue 
                            
                    looked_obj = obj
                    break
            
            if looked_obj:
                if getattr(looked_obj, 'name', '') == 'Key':
                    action_text = LANG.get("hud_press_take_key", "")
                else:
                    nombre = getattr(looked_obj, 'name', 'Object')
                    action_text = f"{LANG.get('hud_press_inspect', '')} {nombre}"
            else:
                target_door = get_looked_at_door(setting_doors, house, camera)
                if target_door:
                    if getattr(target_door, 'requires_key', False) and not getattr(camera, 'has_key', False):
                        action_text = LANG.get("hud_locked", "")
                    else:
                        is_open = getattr(target_door, 'is_open', False)
                        action_text = LANG.get("hud_press_close", "") if is_open else LANG.get("hud_press_open", "")

        if safe_ui.active or portfolio_ui.active:
            action_text = None

        try:
            glCallList(house_display_list)
            draw_inspectables_world(setting_inspectables, inspected_object, house, config_visual, looked_obj)
            draw_doors(setting_doors, house, config_visual)
            draw_inspected_hud(inspected_object, house, config_visual)
        except OpenGL.error.Error:
            pass 
        
        if menu.state != 'CINEMATIC':
            draw_crosshair(camera.width, camera.height)
        
        draw_game_ui(camera.width, camera.height, game_time, action_text, notification_text, portfolio_ui, menu, cinematic)

        if debug_state.overlay:
            draw_debug_visuals(camera, house, setting_doors, debug_state.wireframe)

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

        safe_ui.update(dt)
        if safe_ui.active:
            safe_ui.draw(camera.width, camera.height)
            
        if portfolio_ui.active:
            portfolio_ui.draw(camera.width, camera.height)

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
    
    try:
        tension_timer_snd = pygame.mixer.Sound("source/audio/sfx/timer.wav")
    except Exception as e:
        tension_timer_snd = None
        print("Error al pre-cargar timer:", e)
        
    audio.play_ambient_music("menu.mp3", loops=-1)
    
    # UI Component Registration
    menu = MainMenu(screen_width, screen_height)
    safe_ui = SafeInterface() 
    portfolio_ui = PortfolioInterface()
    
    # Initialize language settings for UI components
    safe_ui.update_language(LANG)
    portfolio_ui.update_language(LANG)
    
    menu.is_fullscreen = saved_settings["is_fullscreen"]
    menu.volume = saved_settings["volume"]
    
    camera = setup_camera(screen_width, screen_height)
    skybox = setup_skybox()
    
    debug_state = DebugState()
    game_time = 15 * 60  
    
    render_loading_screen(screen_width, screen_height, duration=1.5, start_progress=0.0, target_progress=0.85)

    glEnable(GL_DEPTH_TEST)
    setup_fog(current_fog_density)
    setup_advanced_lighting()
    
    pygame.event.set_blocked(None)

    house, config_visual, setting_doors, door_materials, setting_inspectables, inspectable_materials = load_scene_assets()
    
    original_inspectables = list(setting_inspectables)
    static_colliders = list(house.colliders)
    
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

    basement_door = next((d for d in setting_doors if getattr(d, 'mat', '') == "matPuerta6"), None)
    
    game_over_timer = 0.0
    game_over_phase = 0
    tension_triggered = False
    timer_channel = None
    last_state = 'MENU'
    
    cinematic = CinematicState()

    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05) 
        
        if getattr(menu, 'language_changed', False):
            lang_code = getattr(menu, 'language', 'en')
            try:
                with open(f"source/locales/{lang_code}.json", "r", encoding="utf-8") as f:
                    new_lang_dict = json.load(f)
            except Exception as e:
                print(f"Error en hot-reload: {e}")
                new_lang_dict = LANG
                
            LANG.clear()
            LANG.update(new_lang_dict)
            
            TUTORIAL_TEXTS.clear()
            TUTORIAL_TEXTS.extend([
                LANG.get("tut_1", ""), LANG.get("tut_2", ""), LANG.get("tut_3", ""), LANG.get("tut_4", ""),
                LANG.get("tut_5", ""), LANG.get("tut_6", ""), LANG.get("tut_7", ""), LANG.get("tut_8", "")
            ])
            safe_ui.update_language(new_lang_dict)
            portfolio_ui.update_language(new_lang_dict)
            pygame.display.set_caption(LANG.get("window_title", "Evidence - Resolve the Mystery"))
            menu.language_changed = False

        if menu.state == 'RESTART':
            render_loading_screen(camera.width, camera.height, duration=0.8, start_progress=0.0, target_progress=0.85)
            
            game_time = 15 * 60  
            camera.has_key = False
            camera.notification_timer = 0.0
            inspected_object = None
            
            cinematic.started_game = False
            
            safe_ui.active = False
            safe_ui.input_buffer = ""
            safe_ui.error_timer = 0.0
            
            portfolio_ui.active = False
            portfolio_ui.collected_notes.clear()
            portfolio_ui.current_page = 0
            
            setting_inspectables = list(original_inspectables)
            
            for door in setting_doors:
                door.is_open = False
                
                door.angle = 0.0 
                door.target = 0.0
                
                if getattr(door, 'is_safe', False): 
                    door.is_locked = True
                
                if getattr(door, 'mat', '') == "matPuerta6": 
                    door.requires_key = True
            
            render_loading_screen(camera.width, camera.height, duration=0.4, start_progress=0.85, target_progress=1.0)
            
            menu.state = 'GAME'
            pygame.event.clear()
            
            pygame.mixer.music.stop() 
            if timer_channel:
                timer_channel.stop()
            audio.play_ambient_music("suspense_ambient.mp3", loops=-1)
            
            tension_triggered = False
            game_over_phase = 0
            game_over_timer = 0.0
            last_state = 'GAME'

        pygame.event.pump()
        
        running, inspected_object = handle_events(menu, camera, setting_doors, house, debug_state, setting_inspectables, inspected_object, audio, safe_ui, portfolio_ui, cinematic)
        
        
        if menu.state == 'GAME' and not cinematic.started_game:
            menu.state = 'CINEMATIC'
            cinematic.started_game = True
            cinematic.active = True
            cinematic.current_lerp = 0.0
            cinematic.text_index = 0
            
            camera.pos_x = 0.0
            camera.pos_y = 15.0
            camera.pos_z = 25.0
            camera.pitch = -30.0
            camera.yaw = -90.0
            camera.update_camera_vectors()
            
        if menu.state == 'CINEMATIC':
            cinematic.current_lerp += dt * 0.027  
            
            if cinematic.current_lerp > 1.0:
                cinematic.current_lerp = 1.0
                
            smooth_t = cinematic.current_lerp
            
            if smooth_t < 0.35:
                local_t = smooth_t / 0.35
                camera.pos_x = -2.0 + (4.0 * local_t)  
                camera.pos_y = 1.65
                camera.pos_z = -12.0 
                camera.pitch = 0.0
                camera.yaw = 45.0 + (45.0 * local_t)  
                
            else:
                local_t = (smooth_t - 0.35) / 0.65
                
                camera.pos_x = 2.37
                
                if local_t < 1.0:
                    walk_bob = math.sin(local_t * math.pi * 18) * 0.12
                else:
                    walk_bob = 0.0
                    
                camera.pos_y = 1.65 + walk_bob
                camera.pos_z = 12.0 + (-8.48 - 12.0) * local_t
                camera.pitch = 0.0
                camera.yaw = 90.0 
                
            camera.update_camera_vectors()

            if cinematic.current_lerp >= 1.0 and cinematic.text_index >= len(TUTORIAL_TEXTS):
                menu.state = 'GAME'
                cinematic.active = False
                camera.yaw = 90.0
                camera.update_camera_vectors()

        if last_state != menu.state:
            if menu.state == 'MENU' and last_state in ['GAME', 'CINEMATIC']:
                audio.play_ambient_music("menu.mp3", loops=-1)
                if timer_channel:
                    timer_channel.pause()
            elif menu.state == 'CINEMATIC' and last_state in ['MENU', 'OPTIONS']:
                audio.play_ambient_music("suspense_ambient.mp3", loops=-1)
            elif menu.state == 'GAME' and last_state in ['MENU', 'OPTIONS']:
                if tension_triggered:
                    audio.play_ambient_music("few_time.mp3", loops=-1)
                    if timer_channel:
                        timer_channel.unpause()
                else:
                    audio.play_ambient_music("suspense_ambient.mp3", loops=-1)

        last_state = menu.state

        if running and menu.state == 'GAME':
            running_time = getattr(basement_door, 'requires_key', True) if basement_door else True
            
            if running_time:
                game_time -= dt
                
                if game_time <= 180.0 and not tension_triggered:
                    tension_triggered = True
                    audio.play_ambient_music("few_time.mp3", loops=-1)
                    
                    if tension_timer_snd:
                        tension_timer_snd.set_volume(menu.volume / 100.0)
                        timer_channel = tension_timer_snd.play(loops=-1)

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
        
        if menu.state == 'GAME_OVER' and game_over_phase > 0:
            game_over_timer -= dt 
            
            if game_over_timer <= 0.0:
                if game_over_phase == 1:
                    audio.play_sfx("lost") 
                    game_over_timer = 2.5 
                    game_over_phase = 2
                    
                elif game_over_phase == 2:
                    game_over_phase = 0 

        if running:
            current_fog_density = render_frame(
                menu, camera, skybox, house, config_visual, setting_doors, 
                door_materials, dt, clock, debug_state, game_time, 
                house_display_list, static_colliders, current_fog_density, audio,
                setting_inspectables, inspected_object, safe_ui, portfolio_ui, cinematic
            )
        
        pygame.event.pump()

    save_settings(camera, menu)
    pygame.quit()

if __name__ == '__main__':
    main()