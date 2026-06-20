import pygame # pyright: ignore[reportMissingImports]
from OpenGL.GL import * # pyright: ignore[reportMissingImports]
import os
import json
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# =============================================================================
# --- INTERNATIONALIZATION (i18n) SYSTEM ---
# =============================================================================

def load_language(lang_code="en"):
    """
    Loads the text dictionary from the specified JSON locale file.
    """
    try:
        with open(resource_path(f"source/locales/{lang_code}.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading language {lang_code}: {e}")
        return {}

LANG = load_language("en")

class PortfolioInterface:
    def __init__(self):
        """
        Initializes the Portfolio UI overlay, loads the textures for the clipboard
        and the notes, and prepares the data array for collected lore.
        """
        self.active = False
        self.collected_notes = []
        self.current_page = 0
        
        # Load both textures 
        self.tex_portfolio, self.port_w, self.port_h = self.load_texture(resource_path("source/interfaces/portfolio.png"))
        self.tex_note, self.note_w, self.note_h = self.load_texture(resource_path("source/interfaces/nota.png"))
        
        # Hitboxes for interactive navigation
        self.left_btn_rect = None
        self.right_btn_rect = None
        
        pygame.font.init()
        # Fonts for UI and handwriting
        self.font_title = pygame.font.SysFont("Courier New", 32, bold=True)
        self.font_nav = pygame.font.SysFont("Courier New", 24, bold=True)
        self.font_handwriting = pygame.font.SysFont("Georgia", 28, italic=True) 
        
        self.font_counter = pygame.font.SysFont("Courier New", 28, bold=True)

    def load_texture(self, image_path):
        """
        Loads the UI image into VRAM as an OpenGL texture.
        Returns the texture ID alongside its original width and height.
        """
        if not os.path.exists(image_path):
            print(f"Error: Could not find {image_path}")
            return None, 600, 800
            
        surface = pygame.image.load(image_path).convert_alpha()
        data = pygame.image.tobytes(surface, "RGBA", True)
        w = surface.get_width()
        h = surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        return tex_id, w, h

    def add_note(self, text):
        """
        Appends a newly found note to the portfolio array and jumps to that page.
        """
        if text not in self.collected_notes:
            self.collected_notes.append(text)
        self.current_page = len(self.collected_notes) - 1

    def handle_event(self, event, audio=None):
        """
        Processes keyboard and precise mouse inputs for cyclical page navigation.
        """
        if not self.active:
            return False
            
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                self.active = False
                if audio: audio.play_sfx("inspect_paper")
                return True
                
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                if self.collected_notes:
                    self.current_page = (self.current_page - 1) % len(self.collected_notes)
                    if audio: audio.play_sfx("inspect_paper")
                return True
                
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                if self.collected_notes:
                    self.current_page = (self.current_page + 1) % len(self.collected_notes)
                    if audio: audio.play_sfx("inspect_paper")
                return True
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            
            # Check Left Button Click
            if self.left_btn_rect:
                lx, ly, lw, lh = self.left_btn_rect
                if lx <= mx <= lx + lw and ly <= my <= ly + lh:
                    if self.collected_notes:
                        self.current_page = (self.current_page - 1) % len(self.collected_notes)
                        if audio: audio.play_sfx("inspect_paper")
                    return True
                    
            # Check Right Button Click
            if self.right_btn_rect:
                rx, ry, rw, rh = self.right_btn_rect
                if rx <= mx <= rx + rw and ry <= my <= ry + rh:
                    if self.collected_notes:
                        self.current_page = (self.current_page + 1) % len(self.collected_notes)
                        if audio: audio.play_sfx("inspect_paper")
                    return True

        return False

    def wrap_text(self, text, font, max_width):
        """
        Splits a long string into multiple lines based on maximum pixel width.
        """
        words = text.split(' ')
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            width, _ = font.size(' '.join(current_line))
            if width > max_width:
                current_line.pop()
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def draw_text_block(self, text, x, y, max_width, color=(40, 20, 20)):
        """
        Renders a multi-line paragraph onto a single OpenGL texture.
        """
        lines = self.wrap_text(text, self.font_handwriting, max_width)
        line_height = self.font_handwriting.get_linesize() + 8
        total_height = line_height * len(lines)
        
        surf = pygame.Surface((int(max_width), total_height), pygame.SRCALPHA)
        
        for i, line in enumerate(lines):
            line_surf = self.font_handwriting.render(line, True, color)
            surf.blit(line_surf, (0, i * line_height))
            
        w, h = surf.get_size()
        data = pygame.image.tobytes(surf, "RGBA", True)
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        glDeleteTextures([tex_id])
        glDisable(GL_TEXTURE_2D)

    def draw_single_line(self, text, x, y, font, color=(255, 255, 255), center=False):
        """
        Renders a standard single line of text. 
        Returns its bounding box for click detection.
        """
        if not text: return None
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tobytes(text_surface, "RGBA", True)
        w, h = text_surface.get_size()
        
        if center:
            x = x - (w / 2)
            y = y - (h / 2)
            
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        glDeleteTextures([tex_id])
        glDisable(GL_TEXTURE_2D)
        
        return (x, y, w, h)

    def draw(self, screen_width, screen_height):
        """
        Renders the entire portfolio interface with layered textures and stacked notes.
        """
        if not self.active:
            return

        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, screen_width, screen_height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_FOG)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # 1. Dark background overlay
        glColor4f(0.0, 0.0, 0.0, 0.85)
        glDisable(GL_TEXTURE_2D)
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(screen_width, 0)
        glVertex2f(screen_width, screen_height); glVertex2f(0, screen_height)
        glEnd()

        # 2. Draw Portfolio Clipboard
        port_scale = min(screen_width * 0.7 / self.port_w, screen_height * 0.95 / self.port_h)
        draw_port_w = self.port_w * port_scale
        draw_port_h = self.port_h * port_scale
        port_x = (screen_width - draw_port_w) / 2
        port_y = (screen_height - draw_port_h) / 2
        
        if self.tex_portfolio is not None:
            glEnable(GL_TEXTURE_2D)
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glBindTexture(GL_TEXTURE_2D, self.tex_portfolio)
            glBegin(GL_QUADS)
            glTexCoord2f(0, 1); glVertex2f(port_x, port_y)
            glTexCoord2f(1, 1); glVertex2f(port_x + draw_port_w, port_y)
            glTexCoord2f(1, 0); glVertex2f(port_x + draw_port_w, port_y + draw_port_h)
            glTexCoord2f(0, 0); glVertex2f(port_x, port_y + draw_port_h)
            glEnd()
            glDisable(GL_TEXTURE_2D)

        # 3. Hover Logic variables
        mx, my = pygame.mouse.get_pos()
        left_color = (200, 200, 200)
        right_color = (200, 200, 200)

        # 4. Draw Content on top of Clipboard
        if not self.collected_notes:
            # EMPTY PORTFOLIO
            empty_text = LANG.get("port_empty", "Portfolio is Empty")
            self.draw_single_line(empty_text, screen_width/2, screen_height/2, self.font_title, (70, 50, 40), center=True)
            self.left_btn_rect = None
            self.right_btn_rect = None
        else:
            num_stacked = min(3, len(self.collected_notes))
            
            note_scale = min((draw_port_w * 0.85) / self.note_w, (draw_port_h * 0.8) / self.note_h)
            draw_note_w = self.note_w * note_scale
            draw_note_h = self.note_h * note_scale
            
            for i in range(num_stacked - 1, -1, -1):
                nx = ((screen_width - draw_note_w) / 2) + (i * 12)
                ny = port_y + (draw_port_h * 0.12) - (i * 10) 
                
                if self.tex_note is not None:
                    glEnable(GL_TEXTURE_2D)
                    shade = 1.0 - (i * 0.15)
                    glColor4f(shade, shade, shade, 1.0)
                    glBindTexture(GL_TEXTURE_2D, self.tex_note)
                    glBegin(GL_QUADS)
                    glTexCoord2f(0, 1); glVertex2f(nx, ny)
                    glTexCoord2f(1, 1); glVertex2f(nx + draw_note_w, ny)
                    glTexCoord2f(1, 0); glVertex2f(nx + draw_note_w, ny + draw_note_h)
                    glTexCoord2f(0, 0); glVertex2f(nx, ny + draw_note_h)
                    glEnd()
                    glDisable(GL_TEXTURE_2D)
                
                if i == 0:
                    note_key = self.collected_notes[self.current_page]
                    # Real time translation lookup for the note's text content
                    text = LANG.get(note_key, "Illegible text...") 
                    text_x = nx + (draw_note_w * 0.15)
                    text_y = ny + (draw_note_h * 0.15)
                    max_w = draw_note_w * 0.7
                    self.draw_text_block(text, text_x, text_y, max_w, color=(50, 20, 20))
            
            page_text = LANG.get("port_page", "Case File {page} / {total}").replace("{page}", str(self.current_page + 1)).replace("{total}", str(len(self.collected_notes)))
            self.draw_single_line(page_text, screen_width/2, port_y + draw_port_h - 10, self.font_counter, (240, 240, 240), center=True)
            
            if self.left_btn_rect:
                lx, ly, lw, lh = self.left_btn_rect
                if lx <= mx <= lx + lw and ly <= my <= ly + lh:
                    left_color = (220, 50, 50)
                    
            if self.right_btn_rect:
                rx, ry, rw, rh = self.right_btn_rect
                if rx <= mx <= rx + rw and ry <= my <= ry + rh:
                    right_color = (220, 50, 50)

            left_x = port_x + (draw_port_w * 0.15)
            right_x = port_x + (draw_port_w * 0.85)
            
            if self.current_page > 0:
                self.left_btn_rect = self.draw_single_line(LANG.get("port_prev", "< PREV"), left_x, screen_height/2, self.font_title, left_color, center=True)
            else:
                self.left_btn_rect = None
                
            if self.current_page < len(self.collected_notes) - 1:
                self.right_btn_rect = self.draw_single_line(LANG.get("port_next", "NEXT >"), right_x, screen_height/2, self.font_title, right_color, center=True)
            else:
                self.right_btn_rect = None

        self.draw_single_line(LANG.get("port_close", "Press [Q] or [ESC] to Close"), 25, 25, self.font_nav, (200, 200, 200), center=False)
        
        glEnable(GL_FOG)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        
    def update_language(self, new_lang_dict):
        global LANG
        LANG.clear()
        LANG.update(new_lang_dict)