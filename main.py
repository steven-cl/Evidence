import pygame
from pygame.locals import *
from OpenGL.GL import *

# Import our own modules
from obj_loader import Model3D
from camera import CameraFPS

def main():
    # 1. Window setup
    pygame.init()
    screen_width, screen_height = 1920, 1080
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    # Mouse control settings: hide the cursor and grab it inside the window
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # 2. Instantiate and configure the Camera
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    # Initial values set by the team
    camera.pos_x = 0.0 
    camera.pos_y = 5.0  # Initial viewing height
    camera.pos_z = 1.0   
    camera.pitch = -45.0  # Looking down initially
    camera.yaw = -90.0   # Standard forward-facing orientation

    # Synchronize internal math vectors with the manual values above
    camera.update_camera_vectors()

    # 3. Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # 4. Instantiate the house model
    house = Model3D('source/models/RenewHouse.obj', scale=3.0, texture_filename='house_wall.jpg')

    clock = pygame.time.Clock()
    running = True

    # 5. Main loop
    while running:
        # Compute Delta Time in seconds (e.g., at 60 FPS, dt ~= 0.0166)
        # Calculamos dt, pero si el juego se congela (ej. dt > 0.05 segs), 
        # obligamos al dt a ser como máximo 0.05 para que la física no se rompa.
        dt = clock.tick(60) / 1000.0
        dt = min(dt, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Allow releasing the mouse or quickly quitting the game with the ESCAPE key
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Capture and integrate mouse and keyboard movement
        camera.process_mouse()
        camera.process_keyboard(dt, house.colliders)  # Pass colliders for collision detection

        # Clean buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 6. Update camera before drawing the world
        camera.update_view()
        
        house.draw()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()