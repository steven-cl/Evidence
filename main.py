import pygame
from pygame.locals import *
from OpenGL.GL import *

# Import our own modules
from obj_loader import Model3D
from camera import CameraFPS

def main():
    # 1. Window setup
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    # 2. Instanceate and configure the Camera
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    camera.pos_y = 20.0
    camera.pos_x = 0.0 
    camera.pos_z = 0.0   
    camera.pitch = 90.0 

    #3. Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # 4. Instantiate the house model
    house = Model3D('source/models/HouseForGame.obj')

    clock = pygame.time.Clock()
    running = True

    # 5. Main loop
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clean buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 6. Update camera before drawing the world
        # If we change camera.yaw or camera.pos_z here, the player would move
        camera.yaw += 0.5 # Small automatic rotation for testing
        camera.update_view()
        
        # 7. Draw the house model (scaled up for better visibility)
        glPushMatrix()
        glScalef(3.0, 3.0, 3.0)
        house.draw()
        glPopMatrix()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()