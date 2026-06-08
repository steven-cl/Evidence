import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from menu import MainMenu

# Import internal gameplay modules
from camera import CameraFPS
from skybox import Skybox
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
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")
    return screen_width, screen_height


def setup_camera(screen_width, screen_height):
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    camera.pos_x = 0.0
    camera.pos_y = 1.5
    camera.pos_z = 8.0
    camera.pitch = 0.0
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


def process_game_event(event, menu, camera, setting_doors):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            menu.state = 'MENU'
        elif event.key == pygame.K_e:
            toggle_nearest_visible_door(setting_doors, camera)

    elif event.type == pygame.MOUSEMOTION:
        camera.process_mouse(event.rel[0], event.rel[1])


def handle_events(menu, camera, setting_doors):
    running = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False

        if menu.state in ['MENU', 'OPTIONS']:
            menu.handle_input(event, camera)
            if menu.state == 'QUIT':
                return False
        elif menu.state == 'GAME':
            process_game_event(event, menu, camera, setting_doors)

    return running


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
        camera.process_keyboard(dt)
        render_game_world(camera, skybox, house, config_visual, setting_doors, door_materials, dt)

    pygame.display.flip()

def main():
    screen_width, screen_height = setup_display()

    menu = MainMenu(screen_width, screen_height)
    camera = setup_camera(screen_width, screen_height)
    skybox = setup_skybox()

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # Initialize the fog
    setup_fog()

    house, config_visual, setting_doors, door_materials = load_scene_assets()

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    while running:
        dt = clock.tick(60) / 1000.0

        running = handle_events(menu, camera, setting_doors)
        render_frame(menu, camera, skybox, house, config_visual, setting_doors, door_materials, dt)

    pygame.quit()

if __name__ == '__main__':
    main()