import pygame
import time
import json
import os
from OpenGL.GL import *

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

_font_title = None
_font_slogan = None

def init_fonts():
    global _font_title, _font_slogan
    if _font_title is None:
        pygame.font.init()
        try:
            _font_title = pygame.font.SysFont("Courier New", 42, bold=True)
            _font_slogan = pygame.font.SysFont("Courier New", 16, italic=True)
        except:
            _font_title = pygame.font.Font(None, 54)
            _font_slogan = pygame.font.Font(None, 24)

def draw_text_gl(x, y, text, font, color):
    text_surface = font.render(text, True, color)
    w, h = text_surface.get_size()
    
    # Disable surface flipping during byte conversion to maintain Pygame's natural byte order.
    # The texture coordinates applied later correctly map this data to render the text upright.
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
    glTexCoord2f(0, 0); glVertex2f(x - w // 2, y)
    glTexCoord2f(1, 0); glVertex2f(x + w // 2, y)
    glTexCoord2f(1, 1); glVertex2f(x + w // 2, y + h)
    glTexCoord2f(0, 1); glVertex2f(x - w // 2, y + h)
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glDeleteTextures([tex_id])

def render_loading_screen(width, height, duration=1.5, start_progress=0.0, target_progress=1.0):
    """
    Animates the loading bar from a starting progress value to a target progress value 
    over the specified duration.
    """
    init_fonts()
    start_time = time.time()
    
    while True:
        # Keep the window responsive to prevent the OS from throwing "Not Responding" warnings
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
                
        elapsed = time.time() - start_time
        t = elapsed / duration if duration > 0 else 1.0
        
        if t > 1.0:
            t = 1.0
            
        # Linearly interpolate the loading progress
        progress = start_progress + (target_progress - start_progress) * t
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, width, height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        
        glColor3f(0.04, 0.04, 0.04) 
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(width, 0)
        glVertex2f(width, height); glVertex2f(0, height)
        glEnd()
        
        center_x = width // 2
        center_y = height // 2
        
        draw_text_gl(center_x, center_y - 110, LANG.get("load_title", "E V I D E N C E"), _font_title, (180, 20, 20))
        draw_text_gl(center_x, center_y - 50, LANG.get("load_slogan", "Resolve the Mystery"), _font_slogan, (200, 200, 200))
        
        bar_width = 400
        bar_height = 14
        
        glColor3f(0.2, 0.2, 0.2) 
        glLineWidth(2)
        glBegin(GL_LINE_LOOP)
        glVertex2f(center_x - bar_width // 2, center_y + 10)
        glVertex2f(center_x + bar_width // 2, center_y + 10)
        glVertex2f(center_x + bar_width // 2, center_y + 10 + bar_height)
        glVertex2f(center_x - bar_width // 2, center_y + 10 + bar_height)
        glEnd()
        
        current_fill_width = int((bar_width - 8) * progress)
        if current_fill_width > 0:
            glColor3f(0.7, 0.1, 0.1) 
            glBegin(GL_QUADS)
            glVertex2f(center_x - bar_width // 2 + 4, center_y + 14)
            glVertex2f(center_x - bar_width // 2 + 4 + current_fill_width, center_y + 14)
            glVertex2f(center_x - bar_width // 2 + 4 + current_fill_width, center_y + 6 + bar_height)
            glVertex2f(center_x - bar_width // 2 + 4, center_y + 6 + bar_height)
            glEnd()
        
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
        pygame.display.flip()
        
        if t >= 1.0:
            break