import os
import time
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

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

def draw_crosshair(width, height):
    """
    Dibuja una mirilla (crosshair) minimalista en el centro exacto de la pantalla.
    Utiliza mezcla matemática de inversión para contrastar contra cualquier fondo.
    """
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, height, 0, -1, 1)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Apagamos las físicas visuales del 3D para dibujar una UI plana
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_FOG)
    
    # Calculamos el centro matemático de tu monitor
    center_x = width // 2
    center_y = height // 2
    
    # Parámetros estéticos de la mirilla
    size = 8  # Longitud de cada línea de la cruz
    gap = 4   # Espacio hueco en el centro para no tapar objetos
    
    # --- LA MAGIA DE LA INVERSIÓN ---
    # Usamos blanco puro (1.0) como base matemática para la resta
    glColor3f(1.0, 1.0, 1.0)
    glEnable(GL_BLEND)
    # Le decimos a la GPU: "Réstale el color de los píxeles del juego a la mirilla"
    glBlendFunc(GL_ONE_MINUS_DST_COLOR, GL_ZERO)
    
    glLineWidth(2.0)
    glBegin(GL_LINES)
    # Línea Horizontal (Segmento izquierdo y segmento derecho)
    glVertex2f(center_x - size - gap, center_y)
    glVertex2f(center_x - gap, center_y)
    glVertex2f(center_x + gap, center_y)
    glVertex2f(center_x + size + gap, center_y)
    
    # Línea Vertical (Segmento superior y segmento inferior)
    glVertex2f(center_x, center_y - size - gap)
    glVertex2f(center_x, center_y - gap)
    glVertex2f(center_x, center_y + gap)
    glVertex2f(center_x, center_y + size + gap)
    glEnd()
    
    # --- RESTAURACIÓN DE SEGURIDAD ---
    # Devolvemos el motor de transparencia a su estado normal para que 
    # los textos del F2 no se rompan ni se dibujen de colores extraños
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
    glDisable(GL_BLEND)
    glEnable(GL_FOG)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

# ==========================================
# --- SISTEMA DE DEBUG TÁCTICO (F1, F2, F3) ---
# ==========================================
class DebugState:
    def __init__(self):
        self.overlay = False   # F1: Bounding boxes y esferas
        self.hud = False       # F2: Texto en pantalla
        self.wireframe = False # F3: Modo líneas global

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
    Dibuja el overlay de físicas (Cajas y Jugador) encima del juego.
    """
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)
    glDisable(GL_DEPTH_TEST) # Rayos X

    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(1.5)

    # 1. Colliders
    glColor3f(0.0, 1.0, 0.0) # Verde
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

    # 2. Muñeco de Nieve (Detective)
    if hasattr(camera, 'feet_pos'):
        glColor3f(1.0, 0.0, 0.0) # Rojo
        quadric = gluNewQuadric()
        gluQuadricDrawStyle(quadric, GLU_LINE)

        '''
        glPushMatrix()
        glTranslatef(camera.head_pos.x, camera.head_pos.y, camera.head_pos.z)
        gluSphere(quadric, camera.radius, 10, 10)
        glPopMatrix()
        '''

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

    # --- RESTAURACIÓN INTELIGENTE ---
    # Respetamos el modo F3. Si estaba encendido, regresamos a LINE, si no, a FILL.
    if is_wireframe_global:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_FOG)
# ==========================================

def setup_fog():
    glEnable(GL_FOG)
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.03)
    fog_color = [0.1, 0.1, 0.15, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    glHint(GL_FOG_HINT, GL_NICEST)

def setup_display():
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
    skybox_paths = {
        'posz': 'source/textures/posz.jpg',
        'posx': 'source/textures/posx.jpg',
        'negz': 'source/textures/negz.jpg',
        'posy': 'source/textures/posy.jpg',
        'negx': 'source/textures/negx.jpg',
        'negy': 'source/textures/negy.jpg',
    }
    return Skybox(skybox_paths)

def process_game_event(event, menu, camera, setting_doors, house, debug_state):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            menu.state = 'MENU'
        elif event.key == pygame.K_e:
            toggle_nearest_visible_door(setting_doors, house, camera)
            
        # [F1] OVERLAY DE FÍSICAS (Cajas y Rayos X)
        elif event.key == pygame.K_F1:
            debug_state.overlay = not debug_state.overlay
            
        # [F2] HUD DE TEXTO (FPS y Coordenadas)
        elif event.key == pygame.K_F2:
            debug_state.hud = not debug_state.hud
            
        # [F3] MODO WIREFRAME GLOBAL
        elif event.key == pygame.K_F3:
            debug_state.wireframe = not debug_state.wireframe
            if debug_state.wireframe:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

def handle_events(menu, camera, setting_doors, house, debug_state):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if menu.state in ['MENU', 'OPTIONS']:
            menu.handle_input(event, camera)
            if menu.state == 'QUIT':
                return False
        elif menu.state == 'GAME':
            process_game_event(event, menu, camera, setting_doors, house, debug_state)

    return True

def render_game_world(camera, skybox, house, config_visual, setting_doors, door_materials, dt):
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

def render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt, clock, debug_state):
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
        
        camera.process_keyboard(dt, frame_colliders)
        render_game_world(camera, skybox, house, config_visual, setting_doors, door_materials, dt)
        
        draw_crosshair(camera.width, camera.height)

        # 1. Overlay Visual (F1: Cajas y Jugador)
        # Le pasamos el estado de F3 (debug_state.wireframe) para que no lo arruine al terminar
        if debug_state.overlay:
            draw_debug_visuals(camera, house, setting_doors, debug_state.wireframe)

        # 2. Overlay HUD (F2: Textos)
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
    screen_width, screen_height = setup_display()

    menu = MainMenu(screen_width, screen_height)
    camera = setup_camera(screen_width, screen_height)
    skybox = setup_skybox()
    
    debug_state = DebugState()
    
    render_loading_screen(screen_width, screen_height, duration=1.5, start_progress=0.0, target_progress=0.85)

    glEnable(GL_DEPTH_TEST)
    setup_fog()

    house, config_visual, setting_doors, door_materials = load_scene_assets()
    
    render_loading_screen(screen_width, screen_height, duration=0.4, start_progress=0.85, target_progress=1.0)

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        running = handle_events(menu, camera, setting_doors, house, debug_state)
        
        if running:
            render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt, clock, debug_state)

    pygame.quit()

if __name__ == '__main__':
    main()