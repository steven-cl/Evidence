import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Import our own modules
from obj_loader import Model3D
from camera import CameraFPS
from skybox import Skybox

def main():
    # 1. Window setup
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    # Mouse control settings: hide cursor and capture it in the window
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # 2. Instantiate and configure the Camera
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    # Set initial position and orientation manually for a better starting view of the house
    camera.pos_x = 0.0 
    camera.pos_y = 1.5  # Initial viewing height
    camera.pos_z = 8.0   
    camera.pitch = 0.0  # Initially looking down
    camera.yaw = -90.0   # Standard front orientation
    
    # Update the camera's internal vectors based on the initial pitch and yaw
    camera.update_camera_vectors()

    # initialize skybox
    skybox_paths = {
        'posz': 'source/textures/posz.jpg', 'posx': 'source/textures/posx.jpg',
        'negz': 'source/textures/negz.jpg',   'posy': 'source/textures/posy.jpg',
        'negx': 'source/textures/negx.jpg',     'negy': 'source/textures/negy.jpg'
    }
    skybox = Skybox(skybox_paths)

    # 3. Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # 4. Instantiate the house model
    house = Model3D('source/models/HouseForGame.obj')

    clock = pygame.time.Clock()
    running = True

    # 5. Main loop
    while running:
        # Calculate Delta Time in seconds (example. at 60 FPS, dt will be ~0.0166)
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Allows you to release the mouse or quickly close the game with the ESCAPE key
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Capture and integrate mouse and keyboard movement
        camera.process_mouse()
        camera.process_keyboard(dt)

        # Clean buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #Draw skybox
        glDisable(GL_DEPTH_TEST)  # Temporarily disable depth
        glLoadIdentity()
        
        # Forced LookAt on (0,0,0) using your camera's lookat vectors
        gluLookAt(
            0.0, 0.0, 0.0,
            camera.front_x, camera.front_y, camera.front_z,
            0.0, 1.0, 0.0
        )
        skybox.draw()

        glEnable(GL_DEPTH_TEST)   # Reactivate depth for the rest of the objects

        # 6. Update camera before drawing the world
        camera.update_view()
        
        # 7. Draw the house model (scaled up for better visibility)
        glPushMatrix()
        #glScalef(3.0, 3.0, 3.0)
        house.draw()
        glPopMatrix()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()