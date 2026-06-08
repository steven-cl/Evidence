import os
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

def setup_fog():
    """Configures global OpenGL exponential fog parameters for atmospheric mystery effect"""
    glEnable(GL_FOG)
    # Use GL_EXP2 for a more realistic and dense volumetric fog accumulation over distance
    glFogi(GL_FOG_MODE, GL_EXP2)
    # Define the density (Values between 0.01 and 0.1 control how fast the fog thickens)
    glFogf(GL_FOG_DENSITY, 0.03)

    # Define the fog color (R, G, B, A)
    # Use a dark grayish-blue to maintain a nocturnal, mysterious atmosphere
    fog_color = [0.1, 0.1, 0.15, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    # Set calculation quality (GL_NICEST evaluates the fog per-pixel)
    glHint(GL_FOG_HINT, GL_NICEST)


def setup_display():
    # 1. FORCE SDL to position the window box where the mouse cursor is located
    os.environ['SDL_VIDEO_WINDOW_POS'] = "mouse"
    
    pygame.init()
    
    # 2. To prevent Linux from forcing exclusive fullscreen onto the primary monitor,
    # we initialize a Borderless Window (NOFRAME) matching the target monitor's size.
    monitor_info = pygame.display.Info()
    screen_width = monitor_info.current_w
    screen_height = monitor_info.current_h
    
    # NOFRAME spans perfectly across the active screen boundary without title bars
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL | NOFRAME)
    pygame.display.set_caption("Evidence - Resolve the Mystery")
    
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    return screen_width, screen_height

def setup_camera(screen_width, screen_height):
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    # Standard scale 1.0 setup placement values
    camera.pos_x = 0.0 
    camera.pos_y = 1.65  # Realigned initial viewing height to match eye_height perfectly
    camera.pos_z = 0.0   
    camera.pitch = -45.0 
    camera.yaw = -90.0   

    # Synchronize internal math vectors with the manual values above
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


def process_game_event(event, menu, camera, setting_doors):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            menu.state = 'MENU'
        elif event.key == pygame.K_e:
            toggle_nearest_visible_door(setting_doors, camera)


def handle_events(menu, camera, setting_doors):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if menu.state in ['MENU', 'OPTIONS']:
            menu.handle_input(event, camera)
            if menu.state == 'QUIT':
                return False
        elif menu.state == 'GAME':
            process_game_event(event, menu, camera, setting_doors)

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


def render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt):
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
        
        # GENERATE LIVE COLLIDERS FOR THIS FRAME ---
        frame_colliders = list(house.colliders) # Start with static house walls
        for door in setting_doors:
            # Inject dynamically rotated door triangles into the collision check
            frame_colliders.extend(door.get_transformed_triangles(house))
        
        # Pass the unified active list to the camera
        camera.process_keyboard(dt, frame_colliders)
        
        render_game_world(camera, skybox, house, config_visual, setting_doors, door_materials, dt)

    pygame.display.flip()

def main():
    screen_width, screen_height = setup_display()

    menu = MainMenu(screen_width, screen_height)
    camera = setup_camera(screen_width, screen_height)
    skybox = setup_skybox()
    
    render_loading_screen(screen_width, screen_height, duration=1.5, start_progress=0.0, target_progress=0.85)

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    # Initialize the fog
    setup_fog()

    house, config_visual, setting_doors, door_materials = load_scene_assets()
    
    render_loading_screen(screen_width, screen_height, duration=0.4, start_progress=0.85, target_progress=1.0)

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    # Main game loop
    while running:
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        running = handle_events(menu, camera, setting_doors)
        
        if running:
            render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt)

    pygame.quit()

if __name__ == '__main__':
    main()