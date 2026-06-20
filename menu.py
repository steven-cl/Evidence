import pygame
import os
import json
from OpenGL.GL import *

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

class MainMenu:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.state = 'MENU' 
        self.selected_index = 0
        
        self.volume = 80       
        self.is_fullscreen = False
        self.options_selection = 0
        
        self.language = "en"
        if os.path.exists("settings.json"):
            try:
                with open("settings.json", "r") as f:
                    self.language = json.load(f).get("language", "en")
            except: pass
            
        self.language_changed = False
        self.refresh_texts()

        self.game_over_selection = 0

        pygame.font.init()
        try:
            self.font_title = pygame.font.SysFont("Courier New", 48, bold=True)
            self.font_slogan = pygame.font.SysFont("Courier New", 16, italic=True)
            self.font_options = pygame.font.SysFont("Courier New", 28, bold=True)
            self.font_narrative = pygame.font.SysFont("Courier New", 18, bold=False) 
        except:
            self.font_title = pygame.font.Font(None, 54)
            self.font_slogan = pygame.font.Font(None, 24)
            self.font_options = pygame.font.Font(None, 32)
            self.font_narrative = pygame.font.Font(None, 22)
            
        self.center_x = self.width // 2
        self.center_y = self.height // 2
        self.options_start_y = self.center_y + 20
        self.option_spacing = 50
        self.hitboxes = []

    def refresh_texts(self):
        """Rebuild options if language changes"""
        self.options = [
            LANG.get("menu_opt_begin", "Begin Investigation"), 
            LANG.get("menu_opt_adjust", "Field Adjustments"), 
            LANG.get("menu_opt_credits", "Case Credits"), 
            LANG.get("menu_opt_archive", "Archive Case")
        ]
        self.game_over_options = [
            LANG.get("menu_go_opt_restart", "Restart Investigation"), 
            LANG.get("menu_opt_archive", "Archive Case")
        ]

    def _get_options_fields(self):
        disp_str = LANG.get("menu_adj_disp_full", "Full Screen") if self.is_fullscreen else LANG.get("menu_adj_disp_win", "Windowed")
        vol_str = LANG.get("menu_adj_vol", "Audio Volume:  {vol}%").replace("{vol}", str(self.volume))
        disp_field = LANG.get("menu_adj_disp", "Display:       {disp}").replace("{disp}", disp_str)
        
        lang_val = LANG.get("lang_en", "English") if self.language == "en" else LANG.get("lang_es", "Spanish")
        lang_field = LANG.get("menu_adj_lang", "Language:      {lang}").replace("{lang}", lang_val)

        return [
            vol_str,
            disp_field,
            lang_field,
            LANG.get("menu_adj_return", "Return to Case File")
        ]

    def handle_input(self, event, camera=None, audio=None):
        if event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            for idx, rect in enumerate(self.hitboxes):
                if rect.collidepoint(mouse_x, mouse_y):
                    if self.state == 'MENU':
                        if self.selected_index != idx:
                            self.selected_index = idx
                            if audio: audio.play_sfx("ui_click")
                    elif self.state == 'OPTIONS':
                        if self.options_selection != idx:
                            self.options_selection = idx
                            if audio: audio.play_sfx("ui_click")
                    elif self.state == 'GAME_OVER':
                        if self.game_over_selection != idx:
                            self.game_over_selection = idx
                            if audio: audio.play_sfx("ui_click")
                    
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Use absolute mouse position to prevent SDL2 Linux ungrab desync bugs
            mouse_x, mouse_y = pygame.mouse.get_pos()
            
            if self.state == 'CREDITS' and event.button == 1:
                self.state = 'MENU'
                if audio: audio.play_sfx("ui_click")
                return

            for idx, rect in enumerate(self.hitboxes):
                if rect.collidepoint(mouse_x, mouse_y):
                    if self.state == 'MENU' and event.button == 1:
                        self.selected_index = idx 
                        if audio: audio.play_sfx("ui_click")
                        self.execute_selection()
                        
                    elif self.state == 'GAME_OVER' and event.button == 1:
                        self.game_over_selection = idx 
                        if audio: audio.play_sfx("ui_click")
                        if self.game_over_selection == 0:
                            self.state = 'RESTART'
                        else:
                            self.state = 'QUIT'
                            
                    elif self.state == 'OPTIONS':
                        self.options_selection = idx 
                        if self.options_selection == 3 and event.button == 1: 
                            if audio: audio.play_sfx("ui_click")
                            self.state = 'MENU'
                        elif event.button == 1: 
                            if audio: audio.play_sfx("ui_click")
                            self.adjust_option(1, camera)
                        elif event.button == 3: 
                            if audio: audio.play_sfx("ui_click")
                            self.adjust_option(-1, camera)

        elif event.type == pygame.KEYDOWN:
            if self.state == 'MENU':
                if event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.options)
                    if audio: audio.play_sfx("ui_click")
                elif event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.options)
                    if audio: audio.play_sfx("ui_click")
                elif event.key == pygame.K_RETURN:
                    if audio: audio.play_sfx("ui_click")
                    self.execute_selection()
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'QUIT'
                    
            elif self.state == 'OPTIONS':
                current_fields_len = len(self._get_options_fields())
                if event.key == pygame.K_UP:
                    self.options_selection = (self.options_selection - 1) % current_fields_len
                    if audio: audio.play_sfx("ui_click")
                elif event.key == pygame.K_DOWN:
                    self.options_selection = (self.options_selection + 1) % current_fields_len
                    if audio: audio.play_sfx("ui_click")
                elif event.key == pygame.K_LEFT:
                    if audio: audio.play_sfx("ui_click")
                    self.adjust_option(-1, camera)
                elif event.key == pygame.K_RIGHT:
                    if audio: audio.play_sfx("ui_click")
                    self.adjust_option(1, camera)
                elif event.key == pygame.K_RETURN and self.options_selection == 3:
                    if audio: audio.play_sfx("ui_click")
                    self.state = 'MENU'
                elif event.key == pygame.K_ESCAPE:
                    self.state = 'MENU'
                    
            elif self.state == 'CREDITS':
                if event.key in [pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE]:
                    self.state = 'MENU'
                    if audio: audio.play_sfx("ui_click")
                    
            elif self.state == 'GAME_OVER':
                if event.key == pygame.K_UP:
                    self.game_over_selection = (self.game_over_selection - 1) % len(self.game_over_options)
                    if audio: audio.play_sfx("ui_click")
                elif event.key == pygame.K_DOWN:
                    self.game_over_selection = (self.game_over_selection + 1) % len(self.game_over_options)
                    if audio: audio.play_sfx("ui_click")
                elif event.key == pygame.K_RETURN:
                    if audio: audio.play_sfx("ui_click")
                    if self.game_over_selection == 0:
                        self.state = 'RESTART'
                    else:
                        self.state = 'QUIT'
                elif event.key == pygame.K_ESCAPE:
                    if audio: audio.play_sfx("ui_click")
                    self.state = 'QUIT'

    def execute_selection(self):
        if self.selected_index == 0:
            self.state = 'GAME'
        elif self.selected_index == 1:
            self.state = 'OPTIONS'
            self.options_selection = 0
        elif self.selected_index == 2:
            self.state = 'CREDITS'
        elif self.selected_index == 3:
            self.state = 'QUIT'

    def adjust_option(self, direction, camera):
        if self.options_selection == 0: 
            self.volume = max(0, min(100, self.volume + (10 * direction)))
        elif self.options_selection == 1: 
            self.is_fullscreen = not self.is_fullscreen
            if camera: 
                self.apply_display_mode(camera)
        elif self.options_selection == 2: 
            # --- HOT RELOAD LOGIC ---
            self.language = "es" if self.language == "en" else "en"
            global LANG
            try:
                with open(f"source/locales/{self.language}.json", "r", encoding="utf-8") as f:
                    new_lang = json.load(f)
                    LANG.clear()
                    LANG.update(new_lang)
            except: pass
            
            self.refresh_texts()
            self.language_changed = True

    def apply_display_mode(self, camera):
        pygame.display.toggle_fullscreen()
        surface = pygame.display.get_surface()
        new_w, new_h = surface.get_width(), surface.get_height()
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
        elif self.state == 'CREDITS':
            self._render_credits()
        elif self.state == 'GAME_OVER':
            self._render_game_over()
            
        glEnable(GL_FOG)
        glEnable(GL_DEPTH_TEST)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

    def _render_main_menu(self):
        self.draw_text_gl(self.center_x, self.center_y - 120, LANG.get("menu_title", "E V I D E N C E"), self.font_title, (139, 0, 0))
        self.draw_text_gl(self.center_x, self.center_y - 60, LANG.get("menu_slogan", "Resolve the Mystery"), self.font_slogan, (200, 200, 200))
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
        self.draw_text_gl(self.center_x, self.center_y - 120, LANG.get("menu_adj_title", "FIELD ADJUSTMENTS"), self.font_title, (139, 0, 0))
        opt_text = self._get_options_fields()
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

    def _render_credits(self):
        y_offset = self.center_y - 260
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_title", "E V I D E N C E"), self.font_title, (139, 0, 0))
        y_offset += 45
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_slogan", "Resolve the Mystery"), self.font_slogan, (200, 200, 200))
        y_offset += 60
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_cred_role_3d", "LEAD 3D ENVIRONMENT ARTIST & MODELER"), self.font_narrative, (180, 0, 0))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, "Osman Aaron Mejias Rios", self.font_narrative, (200, 200, 200))
        y_offset += 40
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_cred_role_core", "CORE PROGRAMMING & MECHANICS"), self.font_narrative, (180, 0, 0))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, "Steven Castillo Lopez (@steven-cl)", self.font_narrative, (200, 200, 200))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, "Manuel Ortega (@maox51)", self.font_narrative, (200, 200, 200))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, "Osman Aaron Mejias Rios (@justBtterThanU)", self.font_narrative, (200, 200, 200))
        y_offset += 40
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_cred_role_design", "GAME DESIGN & NARRATIVE"), self.font_narrative, (180, 0, 0))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, "Steven Castillo Lopez", self.font_narrative, (200, 200, 200))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, "Manuel Ortega", self.font_narrative, (200, 200, 200))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, "Osman Aaron Mejias Rios", self.font_narrative, (200, 200, 200))
        y_offset += 40
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_cred_role_sound", "SOUND DESIGN & ASSETS"), self.font_narrative, (180, 0, 0))
        y_offset += 25
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_cred_sound_val", "Community Open Source & Self Created"), self.font_narrative, (200, 200, 200))
        y_offset += 60
        self.draw_text_gl(self.center_x, y_offset, LANG.get("menu_cred_return", "> Press [ESC] to Return <"), self.font_options, (110, 110, 110))

    def _render_game_over(self):
        self.draw_text_gl(self.center_x, self.center_y - 180, LANG.get("menu_go_title", "Y O U   L O S E"), self.font_title, (180, 0, 0))
        story_lines = [
            LANG.get("menu_go_story_1", "The serial killer returned home and found you inside."),
            LANG.get("menu_go_story_2", "He entered, massacred you, and tore you to pieces."),
            LANG.get("menu_go_story_3", "You became just another one of his victims,"),
            LANG.get("menu_go_story_4", "and nobody ever heard from you again."),
            LANG.get("menu_go_story_5", ""),
            LANG.get("menu_go_story_6", "For Freddy, you were his favorite toy because you dared"),
            LANG.get("menu_go_story_7", "to take the risk of entering his house to investigate him.")
        ]
        y_offset = self.center_y - 110
        for line in story_lines:
            self.draw_text_gl(self.center_x, y_offset, line, self.font_narrative, (170, 170, 170))
            y_offset += 25
        options_y = y_offset + 30
        for i, option in enumerate(self.game_over_options):
            y_pos = options_y + (i * self.option_spacing)
            if i == self.game_over_selection:
                display_text = f"> {option} <"
                color = (180, 0, 0)
            else:
                display_text = f"  {option}  "
                color = (130, 130, 130)
            rect = self.draw_text_gl(self.center_x, y_pos, display_text, self.font_options, color)
            self.hitboxes.append(rect)