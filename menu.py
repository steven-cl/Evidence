import pygame
from OpenGL.GL import *

class MainMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        
        self.state = 'MENU' 
        
        self.options = ["Begin Investigation", "Field Adjustments", "Archive Case"]
        self.selected_index = 0
        
        self.volume = 80       
        # Display mode state initialization
        self.is_fullscreen = False
        self.options_selection = 0
        self.options_fields = ["Volume", "Display", "Return to Case File"]

        pygame.font.init()
        try:
            self.font_title = pygame.font.SysFont("Courier New", 48, bold=True)
            self.font_slogan = pygame.font.SysFont("Courier New", 16, italic=True)
            self.font_options = pygame.font.SysFont("Courier New", 28, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 54)
            self.font_slogan = pygame.font.Font(None, 24)
            self.font_options = pygame.font.Font(None, 32)
            
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.options_start_y = self.center_y + 20
        self.option_spacing = 50
        
        self.hitboxes = []

    def handle_input(self, event, camera=None):
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            for idx, rect in enumerate(self.hitboxes):
                if rect.collidepoint(mouse_x, mouse_y):
                    if self.state == 'MENU':
                        self.selected_index = idx
                    elif self.state == 'OPTIONS':
                        self.options_selection = idx
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            for idx, rect in enumerate(self.hitboxes):
                if rect.collidepoint(mouse_x, mouse_y):
                    if self.state == 'MENU' and event.button == 1:
                        self.execute_selection()
                    elif self.state == 'OPTIONS':
                        if self.options_selection == 2 and event.button == 1: 
                            self.state = 'MENU'
                        elif event.button == 1: 
                            self.adjust_option(1, camera)
                        elif event.button == 3: 
                            self.adjust_option(-1, camera)

        elif event.type == pygame.KEYDOWN:
            if self.state == 'MENU':
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self.execute_selection()
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'QUIT'
                    
            elif self.state == 'OPTIONS':
                if event.key == pygame.K_UP:
                    self.options_selection = (self.options_selection - 1) % len(self.options_fields)
                elif event.key == pygame.K_DOWN:
                    self.options_selection = (self.options_selection + 1) % len(self.options_fields)
                
                elif event.key == pygame.K_LEFT:
                    self.adjust_option(-1, camera)
                elif event.key == pygame.K_RIGHT:
                    self.adjust_option(1, camera)
                
                elif event.key == pygame.K_RETURN and self.options_selection == 2:
                    self.state = 'MENU'
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'MENU'

    def execute_selection(self):
        if self.selected_index == 0:
            self.state = 'GAME'
        elif self.selected_index == 1:
            self.state = 'OPTIONS'
            self.options_selection = 0
        elif self.selected_index == 2:
            self.state = 'QUIT'

    def adjust_option(self, direction, camera):
        if self.options_selection == 0: 
            self.volume = max(0, min(100, self.volume + (10 * direction)))
        elif self.options_selection == 1: 
            self.is_fullscreen = not self.is_fullscreen
            if camera: 
                self.apply_display_mode(camera)

    def apply_display_mode(self, camera):
        """
        Toggles between fullscreen and windowed display modes 
        while preserving the active OpenGL context and textures.
        """
        pygame.display.toggle_fullscreen()
        
        # Retrieve the dimensions of the resulting surface to account for window borders
        surface = pygame.display.get_surface()
        new_w, new_h = surface.get_width(), surface.get_height()
        
        # Update the OpenGL viewport and camera projection to the new resolution
        glViewport(0, 0, new_w, new_h)
        camera.width = new_w
        camera.height = new_h
        camera.configure_projection()
        
        self.width = new_w
        self.height = new_h
        self.center_x = new_w // 2
        self.center_y = new_h // 2
        self.options_start_y = self.center_y + 20

    def draw_text_gl(self, x, y, text, font, color):
        text_surface = font.render(text, True, color)
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
        
        draw_x = x - w // 2
        
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(draw_x, y)
        glTexCoord2f(1, 0); glVertex2f(draw_x + w, y)
        glTexCoord2f(1, 1); glVertex2f(draw_x + w, y + h)
        glTexCoord2f(0, 1); glVertex2f(draw_x, y + h)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_BLEND)
        glDeleteTextures([tex_id])
        
        return pygame.Rect(draw_x, y, w, h)

    def render(self):
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_LIGHTING)
        glDisable(GL_FOG)
        
        glColor3f(0.04, 0.04, 0.04) 
        glBegin(GL_QUADS)
        glVertex2f(0, 0); glVertex2f(self.width, 0)
        glVertex2f(self.width, self.height); glVertex2f(0, self.height)
        glEnd()
        
        self.hitboxes.clear()
        
        if self.state == 'MENU':
            self._render_main_menu()
        elif self.state == 'OPTIONS':
            self._render_options_menu()
            
        glEnable(GL_FOG)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _render_main_menu(self):
        self.draw_text_gl(self.center_x, self.center_y - 120, "E V I D E N C E", self.font_title, (139, 0, 0))
        self.draw_text_gl(self.center_x, self.center_y - 60, "Resolve the Mystery", self.font_slogan, (200, 200, 200))
        
        for i, option in enumerate(self.options):
            y_pos = self.options_start_y + (i * self.option_spacing)
            
            if i == self.selected_index:
                display_text = f"> {option} <"
                color = (180, 0, 0)
            else:
                display_text = f"  {option}  "
                color = (130, 130, 130)
                
            rect = self.draw_text_gl(self.center_x, y_pos, display_text, self.font_options, color)
            self.hitboxes.append(rect)

    def _render_options_menu(self):
        self.draw_text_gl(self.center_x, self.center_y - 120, "FIELD ADJUSTMENTS", self.font_title, (139, 0, 0))

        # Dynamic text rendering for the current display mode
        display_str = "Full Screen" if self.is_fullscreen else "Windowed"

        opt_text = [
            f"Audio Volume:  {self.volume}%",
            f"Display:       {display_str}",
            "Return to Case File"
        ]

        for i, text in enumerate(opt_text):
            y_pos = self.options_start_y + (i * self.option_spacing)
            
            if i == self.options_selection:
                display_text = f"> {text} <"
                color = (180, 0, 0)
            else:
                display_text = f"  {text}  "
                color = (130, 130, 130)
            
            rect = self.draw_text_gl(self.center_x, y_pos, display_text, self.font_options, color)
            self.hitboxes.append(rect)