import pygame # pyright: ignore[reportMissingImports]
from OpenGL.GL import * # pyright: ignore[reportMissingImports]
import os

class SafeInterface:
    def __init__(self):
        """
        Initializes the Safe UI overlay, loads the texture, and sets up
        the internal state machine for password validation and visual feedback.
        """
        self.active = False
        self.password = "361012"
        self.input_buffer = ""
        
        self.error_timer = 0.0
        self.flash_timer = 0.0
        self.flashing_key = None
        
        self.texture_id = self.load_texture("source/interfaces/caja.jpg")
        
        # Grid keys bounding boxes (X, Y, Width, Height)
        self.key_rects = {
            '1': (0.40, 0.25, 0.11, 0.11), '2': (0.533, 0.25, 0.11, 0.11), '3': (0.667, 0.25, 0.11, 0.11),
            '4': (0.40, 0.38, 0.11, 0.11), '5': (0.533, 0.38, 0.11, 0.11), '6': (0.667, 0.38, 0.11, 0.11),
            '7': (0.40, 0.51, 0.11, 0.11), '8': (0.533, 0.51, 0.11, 0.11), '9': (0.667, 0.51, 0.11, 0.11),
            '*': (0.40, 0.64, 0.11, 0.11), '0': (0.533, 0.64, 0.11, 0.11), '#': (0.667, 0.64, 0.11, 0.11)
        }
        
        # Physical circular knob mapped as the ENTER button
        self.enter_btn_rect = (0.215, 0.56, 0.14, 0.16)
        
        # Error LED crystal bounding box
        self.error_led_rect = (0.325, 0.48, 0.02, 0.025)
        
        pygame.font.init()
        # Main font for the digital display
        self.font = pygame.font.SysFont("Courier New", 36, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 24, bold=True)

    def load_texture(self, image_path):
        """
        Loads the UI image into VRAM as an OpenGL texture.
        """
        if not os.path.exists(image_path):
            print(f"Error: Could not find {image_path}")
            return None
            
        surface = pygame.image.load(image_path).convert_alpha()
        data = pygame.image.tobytes(surface, "RGBA", True)
        self.img_width = surface.get_width()
        self.img_height = surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.img_width, self.img_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, data)
        return tex_id

    def handle_event(self, event, audio=None):
        """
        Processes keyboard and mouse inputs when the safe UI is active.
        Returns True if the correct password was entered, unlocking the safe.
        """
        if not self.active:
            return False
            
        # --- KEYBOARD INPUT HANDLING ---
        if event.type == pygame.KEYDOWN:
            
            # 1. Siempre permitir salir con ESC, incluso si hay error
            if event.key == pygame.K_ESCAPE:
                self.active = False
                self.input_buffer = ""
                self.error_timer = 0.0 # Resetea el error al salir
                return False
                
            # --- NUEVO: BLOQUEO POR ERROR ---
            # Si el LED de error está encendido, ignorar cualquier otra tecla
            if self.error_timer > 0:
                return False
                
            if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                self.flashing_key = 'ENTER'
                self.flash_timer = 0.15
                if self.input_buffer == self.password:
                    self.active = False
                    self.input_buffer = ""
                    if audio: audio.play_sfx("safe_unlock")
                    return True 
                else:
                    self.input_buffer = ""
                    self.error_timer = 2.0 
                    if audio: audio.play_sfx("safe_error")
                return False

            if event.key == pygame.K_BACKSPACE:
                self.input_buffer = self.input_buffer[:-1]
                if audio: audio.play_sfx("safe_beep")
                return False

            char = event.unicode
            if char in self.key_rects:
                if len(self.input_buffer) < 20: 
                    self.input_buffer += char
                self.flashing_key = char
                self.flash_timer = 0.15 
                if audio: audio.play_sfx("safe_beep")
                
        # --- MOUSE INPUT HANDLING ---
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            
            if self.error_timer > 0:
                return False

            screen_width, screen_height = pygame.display.get_surface().get_size()
            scale = min(screen_width * 0.8 / self.img_width, screen_height * 0.8 / self.img_height)
            draw_w = self.img_width * scale
            draw_h = self.img_height * scale
            x_offset = (screen_width - draw_w) / 2
            y_offset = (screen_height - draw_h) / 2
            
            mx, my = event.pos
            
            # Evaluate grid interactions
            for char, (rx, ry, rw, rh) in self.key_rects.items():
                kx = x_offset + (rx * draw_w)
                ky = y_offset + (ry * draw_h)
                kw = rw * draw_w
                kh = rh * draw_h
                
                if kx <= mx <= kx + kw and ky <= my <= ky + kh:
                    if len(self.input_buffer) < 20:
                        self.input_buffer += char
                    self.flashing_key = char
                    self.flash_timer = 0.15 
                    if audio: audio.play_sfx("safe_beep")
                    return False
            
            # Evaluate physical circular knob interaction (ENTER)
            ex, ey, ew, eh = self.enter_btn_rect
            bx = x_offset + (ex * draw_w)
            by = y_offset + (ey * draw_h)
            bw = ew * draw_w
            bh = eh * draw_h
            
            if bx <= mx <= bx + bw and by <= my <= by + bh:
                self.flashing_key = 'ENTER'
                self.flash_timer = 0.15
                if self.input_buffer == self.password:
                    self.active = False
                    self.input_buffer = ""
                    if audio: audio.play_sfx("safe_unlock")
                    return True
                else:
                    self.input_buffer = ""
                    self.error_timer = 2.0
                    if audio: audio.play_sfx("safe_error")
                return False

        return False

    def update(self, dt):
        """
        Updates visual feedback timers.
        """
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if self.error_timer > 0:
            self.error_timer -= dt

    def draw_text(self, text, x, y, font, color=(255, 50, 50)):
        """
        Renders dynamic text on the screen.
        """
        if not text:
            return
            
        text_surface = font.render(text, True, color)
        text_data = pygame.image.tobytes(text_surface, "RGBA", True)
        w, h = text_surface.get_size()
        
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glEnable(GL_TEXTURE_2D)
        
        # --- FIX: Limpiar el color de OpenGL para que la textura brille al 100% ---
        glColor4f(1.0, 1.0, 1.0, 1.0)
        # --------------------------------------------------------------------------
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x, y)
        glTexCoord2f(1, 1); glVertex2f(x + w, y)
        glTexCoord2f(1, 0); glVertex2f(x + w, y + h)
        glTexCoord2f(0, 0); glVertex2f(x, y + h)
        glEnd()
        glDeleteTextures([tex_id])
        glDisable(GL_TEXTURE_2D)

    def draw(self, screen_width, screen_height):
        """
        Renders the safe interface, button flashes, digital screen, and error indicators.
        """
        if not self.active or self.texture_id is None:
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

        # Scale and offset math
        scale = min(screen_width * 0.8 / self.img_width, screen_height * 0.8 / self.img_height)
        draw_w = self.img_width * scale
        draw_h = self.img_height * scale
        x_offset = (screen_width - draw_w) / 2
        y_offset = (screen_height - draw_h) / 2

        # 2. Draw Main Texture
        glEnable(GL_TEXTURE_2D)
        glColor4f(1.0, 1.0, 1.0, 1.0)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex2f(x_offset, y_offset)
        glTexCoord2f(1, 1); glVertex2f(x_offset + draw_w, y_offset)
        glTexCoord2f(1, 0); glVertex2f(x_offset + draw_w, y_offset + draw_h)
        glTexCoord2f(0, 0); glVertex2f(x_offset, y_offset + draw_h)
        glEnd()
        
        # 3. Draw Digital Screen (LCD)
        disp_x = x_offset + (0.39 * draw_w)
        disp_y = y_offset + (0.09 * draw_h)
        disp_w = 0.38 * draw_w
        disp_h = 0.12 * draw_h

        glDisable(GL_TEXTURE_2D)
        # LCD Dark Background
        glColor4f(0.05, 0.08, 0.05, 1.0) 
        glBegin(GL_QUADS)
        glVertex2f(disp_x, disp_y); glVertex2f(disp_x + disp_w, disp_y)
        glVertex2f(disp_x + disp_w, disp_y + disp_h); glVertex2f(disp_x, disp_y + disp_h)
        glEnd()

        # LCD Border
        glColor4f(0.15, 0.15, 0.15, 1.0)
        glLineWidth(3.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glBegin(GL_QUADS)
        glVertex2f(disp_x, disp_y); glVertex2f(disp_x + disp_w, disp_y)
        glVertex2f(disp_x + disp_w, disp_y + disp_h); glVertex2f(disp_x, disp_y + disp_h)
        glEnd()
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # 4. Highlight logic for interactive bounds
        if self.flash_timer > 0:
            glColor4f(1.0, 1.0, 1.0, 0.25) 
            if self.flashing_key in self.key_rects:
                rx, ry, rw, rh = self.key_rects[self.flashing_key]
                kx = x_offset + (rx * draw_w)
                ky = y_offset + (ry * draw_h)
                kw = rw * draw_w
                kh = rh * draw_h
                
                glBegin(GL_QUADS)
                glVertex2f(kx, ky); glVertex2f(kx + kw, ky)
                glVertex2f(kx + kw, ky + kh); glVertex2f(kx, ky + kh)
                glEnd()
                
            elif self.flashing_key == 'ENTER':
                rx, ry, rw, rh = self.enter_btn_rect
                bx = x_offset + (rx * draw_w)
                by = y_offset + (ry * draw_h)
                bw = rw * draw_w
                bh = rh * draw_h
                
                glBegin(GL_QUADS)
                glVertex2f(bx, by); glVertex2f(bx + bw, by)
                glVertex2f(bx + bw, by + bh); glVertex2f(bx, by + bh)
                glEnd()

        # 5. Render error indicator physical LED
        if self.error_timer > 0:
            rx, ry, rw, rh = self.error_led_rect
            lx = x_offset + (rx * draw_w)
            ly = y_offset + (ry * draw_h)
            lw = rw * draw_w
            lh = rh * draw_h
            
            glColor4f(1.0, 0.1, 0.1, 0.8) 
            glBegin(GL_QUADS)
            glVertex2f(lx, ly); glVertex2f(lx + lw, ly)
            glVertex2f(lx + lw, ly + lh); glVertex2f(lx, ly + lh)
            glEnd()

        # 6. Render Text on Digital LCD Screen
        text_y_center = disp_y + (disp_h / 2) - 18
        if self.error_timer > 0:
            self.draw_text("ERROR", disp_x + 15, text_y_center, self.font, (255, 50, 50))
        elif len(self.input_buffer) > 0:
            # Show only the last 8 characters so it scrolls left like a real calculator
            display_str = self.input_buffer[-8:]
            self.draw_text(display_str, disp_x + 15, text_y_center, self.font, (0, 255, 0)) # Verde Brillante Puro
        else:
            # Idle cursor
            self.draw_text("_", disp_x + 15, text_y_center, self.font, (0, 255, 0)) # Mismo verde brillante puro

        # Instructions
        self.draw_text("Press [ESC] to Exit", 25, 25, self.font_small, (200, 200, 200)) # Este ya no desaparecerá
        
        glEnable(GL_FOG)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()