import pygame
from pygame.locals import *
from OpenGL.GL import *

# Import our own modules
from obj_loader import Model3D
from camera import CameraFPS

def setup_fog():
    """Configure the global fog parameters in OpenGL"""
    glEnable(GL_FOG)  # Enable fog rendering
    glFogf(GL_FOG_START, 5.0)   # The fog starts at 5 meters from the camera
    glFogf(GL_FOG_END, 18.0)    # The fog fully obscures objects at 18 meters or more, creating a sense of depth and mystery
    
    # 1. Define the mathematical mode (GL_EXP2 gives an excellent atmosphere of mystery)
    glFogi(GL_FOG_MODE, GL_EXP2)
    
    # 2. Define the density (Values between 0.01 and 0.1 control how fast the fog thickens)
    glFogf(GL_FOG_DENSITY, 0.03)
    
    # 3. Define the fog color (R, G, B, A)
    # We will use a dark grayish-blue to maintain the nocturnal and mysterious atmosphere
    fog_color = [0.1, 0.1, 0.15, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    
    # 4. Quality of the calculation (GL_NICEST evaluates the fog by pixel, not by vertex)
    glHint(GL_FOG_HINT, GL_NICEST)

def main():
    # 1. Window setup
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    # Configuration of the mouse control: hide cursor and grab it in the window
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # 2. Instantiate and configure the Camera
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    
    camera.pos_x = 0.0 
    camera.pos_y = 1.5  # Initial viewing height
    camera.pos_z = 8.0   
    camera.pitch = 0.0  # Looking down initially
    camera.yaw = -90.0   # Standard front orientation
    
    # Synchronize the internal mathematical vectors with the manual values ​​above
    camera.update_camera_vectors()

    # 3. Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # Initialize the fog
    setup_fog()

    # 4. Instantiate the house model
    house = Model3D('source/models/RenewHouse.obj')

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    # 5. Main loop
    while running:
        # Calculate Delta Time in seconds (e.g., at 60 FPS, dt will be ~0.0166)
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Exit the game if the user presses the ESC key
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Capture and integrate the mouse and keyboard movement
        camera.process_mouse()
        camera.process_keyboard(dt)

        # Clean buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

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