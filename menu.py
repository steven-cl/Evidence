from OpenGL.GL import *
import pygame

class MainMenu:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        
        # Game states: 'MENU', 'OPTIONS', 'GAME', 'QUIT'
        self.state = 'MENU' 
        
        # Menu navigation
        self.main_options = ["Begin Investigation", "Field Adjustments", "Archive Case"]
        self.current_selection = 0
        
        # Options sub-menu states
        self.volume = 80       # 0% to 100%
        #self.brightness = 100   # 0% to 150%
        self.window_sizes = [(800, 600), (1280, 720), (1920, 1080)]
        self.current_size_idx = 0
        self.options_selection = 0
        self.options_fields = ["Volume", "Brightness", "Screen Size", "Back"]

        # Initialize Pygame Font System
        pygame.font.init()
        # A classic serif or monospaced font fits a detective/noir theme perfectly
        self.font = pygame.font.SysFont("Courier New", 32, bold=True)
        self.title_font = pygame.font.SysFont("Courier New", 48, bold=True)

    def draw_text(self, text, x, y, color=(200, 200, 200)):
        """Converts Pygame text into an OpenGL texture and draws it in 2D space"""
        text_surface = self.font.render(text, True, color)
        text_surface = pygame.transform.flip(text_surface, False, True)
        text_data = pygame.image.tostring(text_surface, "RGBA", True)
        tex_width, tex_height = text_surface.get_width(), text_surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, tex_width, tex_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # --- CRUCIAL FIX: Reset global color state to clear stale 3D shading/fog tints ---
        glColor4f(1.0, 1.0, 1.0, 1.0)

        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex2f(x, y)
        glTexCoord2f(1, 0); glVertex2f(x + tex_width, y)
        glTexCoord2f(1, 1); glVertex2f(x + tex_width, y + tex_height)
        glTexCoord2f(0, 1); glVertex2f(x, y + tex_height)
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        glDeleteTextures([tex_id])

    def render(self):
        """Switches to 2D Orthographic view and draws the active menu screen"""
        # 1. Clear texturing context and set strict dark background for menu
        glClearColor(0.05, 0.05, 0.05, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # 2. Save current matrices and switch to 2D Orthographic view
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, self.width, self.height, 0, -1, 1)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        # 3. Disable 3D features and enable strict 2D blending/texturing
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_FOG)
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D) # CRUCIAL: Enable textures globally for font rendering
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # 4. Render menu views based on active state
        if self.state == 'MENU':
            self._render_main_menu()
        elif self.state == 'OPTIONS':
            self._render_options_menu()

        # 5. Restore original 3D engine state matrices
        glDisable(GL_TEXTURE_2D)
        glEnable(GL_DEPTH_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _render_main_menu(self):
        # Title - Atmospheric red/crimson stain effect
        self.draw_text("E V I D E N C E", self.width // 2 - 180, 100, color=(139, 0, 0))
        self.draw_text("Resolve the Mystery", self.width // 2 - 160, 150, color=(120, 120, 120))

        # Render main options
        start_y = 300
        for i, option in enumerate(self.main_options):
            if i == self.current_selection:
                # Highlighted option: Dark blood red text with an indicator bracket
                text = f"> {option} <"
                color = (180, 0, 0)
            else:
                text = option
                color = (170, 170, 170)
            
            self.draw_text(text, self.width // 2 - 140, start_y + (i * 60), color)

    def _render_options_menu(self):
        self.draw_text("FIELD ADJUSTMENTS", self.width // 2 - 160, 100, color=(139, 0, 0))

        # Dynamic string generation to show live updates of variables
        opt_text = [
            f"Audio Volume:  {self.volume}%",
            #f"Lens Exposure: {self.brightness}%",
            f"Resolution:    {self.window_sizes[self.current_size_idx][0]}x{self.window_sizes[self.current_size_idx][1]}",
            "Return to Case File"
        ]

        start_y = 260
        for i, text in enumerate(opt_text):
            if i == self.options_selection:
                display_text = f"> {text}"
                color = (180, 0, 0)
            else:
                display_text = f"  {text}"
                color = (170, 170, 170)
            
            self.draw_text(display_text, self.width // 2 - 200, start_y + (i * 50), color)

    def handle_input(self, event, camera=None):
        """Processes keyboard inputs specifically tailored for menu control"""
        if event.type != pygame.KEYDOWN:
            return

        if self.state == 'MENU':
            if event.key == pygame.K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.main_options)
            elif event.key == pygame.K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.main_options)
            elif event.key == pygame.K_RETURN:
                if self.current_selection == 0:
                    self.state = 'GAME'  # Triggers the 3D world render loop
                elif self.current_selection == 1:
                    self.state = 'OPTIONS'
                    self.options_selection = 0
                elif self.current_selection == 2:
                    self.state = 'QUIT'

        elif self.state == 'OPTIONS':
            if event.key == pygame.K_UP:
                self.options_selection = (self.options_selection - 1) % len(self.options_fields)
            elif event.key == pygame.K_DOWN:
                self.options_selection = (self.options_selection + 1) % len(self.options_fields)
            
            # Adjust values using Left and Right arrows
            elif event.key == pygame.K_LEFT:
                if self.options_selection == 0: self.volume = max(0, self.volume - 10)
                #elif self.options_selection == 1: self.brightness = max(10, self.brightness - 10)
                elif self.options_selection == 1: self.current_size_idx = (self.current_size_idx - 1) % len(self.window_sizes)
                #Apply the window change immediately
                if camera: self.apply_window_resize(camera)
            elif event.key == pygame.K_RIGHT:
                if self.options_selection == 0: self.volume = min(100, self.volume + 10)
                #elif self.options_selection == 1: self.brightness = min(150, self.brightness + 10)
                elif self.options_selection == 1: self.current_size_idx = (self.current_size_idx + 1) % len(self.window_sizes)
                #Apply the window change immediately
                if camera: self.apply_window_resize(camera)
            
            elif event.key == pygame.K_RETURN and self.options_selection == 2:
                self.state = 'MENU'

    def apply_window_resize(self, camera):
        """Resizes the Pygame window and updates OpenGL projection matrices to prevent stretching"""
        new_width, new_height = self.window_sizes[self.current_size_idx]
        self.width = new_width
        self.height = new_height
        
        # 1. Re-initialize the video display mode with the new size
        pygame.display.set_mode((new_width, new_height), pygame.DOUBLEBUF | pygame.OPENGL)
        
        # 2. Tell OpenGL to map drawings to the new pixel dimensions
        glViewport(0, 0, new_width, new_height)
        
        # 3. Update the camera configuration values so it recalculates the new aspect ratio
        camera.width = new_width
        camera.height = new_height
        camera.configure_projection()
        
        # 4. Re-enable depth testing as set_mode can flush previous OpenGL context states
        glEnable(GL_DEPTH_TEST)

