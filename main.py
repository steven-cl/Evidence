import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from menu import MainMenu

# Import internal gameplay modules
from obj_loader import Model3D
from camera import CameraFPS
from skybox import Skybox

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

def setup_fog():
    """Configures global OpenGL exponential fog parameters for atmospheric mystery effect"""
    glEnable(GL_FOG)
    
    # Use GL_EXP2 for a more realistic and dense volumetric fog accumulation over distance
    glFogi(GL_FOG_MODE, GL_EXP2)
    glFogf(GL_FOG_DENSITY, 0.03)
    
    # Set fog color to a dark grayish-blue to match the nighttime atmosphere
    fog_color = [0.1, 0.1, 0.15, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    
    # GL_NICEST forces per-pixel fog evaluation instead of per-vertex for maximum quality
    glHint(GL_FOG_HINT, GL_NICEST)

def main():
    # 1. Window setup
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    # Mouse control configuration: hide cursor and lock it within the game window boundaries
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Initialize Menu UI instance after Pygame display setup
    menu = MainMenu(screen_width, screen_height)

    # 2. Instantiate and configure the Gameplay Camera
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

    # Initialize the fog
    setup_fog()

    # 4. Instantiate the house model
    house = Model3D('source/models/RenewHouse.obj')

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    # 5. Main loop
    while running:
        # Calculate Delta Time in seconds (example. at 60 FPS, dt will be ~0.0166)
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # =================================================================
            # CASE A: CURRENT APPLICATION STATE IS INTERACTIVE UI MENU
            # =================================================================
            if menu.state in ['MENU', 'OPTIONS']:
                menu.handle_input(event, camera)
                if menu.state == 'QUIT':
                    running = False
            
            # =================================================================
            # CASE B: CURRENT APPLICATION STATE IS ACTIVE 3D GAMEPLAY WORLD
            # =================================================================
            elif menu.state == 'GAME':
                if event.type == pygame.KEYDOWN:
                    # Pressing ESCAPE pauses exploration and returns detective back to main workspace
                    if event.key == pygame.K_ESCAPE:
                        menu.state = 'MENU'
                        # Restore hardware mouse cursor visibility for UI menu selection navigation
                        pygame.mouse.set_visible(True)
                
                # Event-driven mouse delta tracking processor for seamless FPS camera rotation
                elif event.type == pygame.MOUSEMOTION:
                    camera.process_mouse(event.rel[0], event.rel[1])
            elif event.type == pygame.KEYDOWN:
                # Exit the game if the user presses the ESC key
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Capture and integrate mouse and keyboard movement
        #camera.process_mouse()
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
        
        # =================================================================
        # RENDER ENGINE PIPELINE EXECUTION PIPELINE
        # =================================================================
        if menu.state in ['MENU', 'OPTIONS']:
            # Release mouse capture so user can interact with system if needed
            pygame.event.set_grab(False)
            pygame.mouse.set_visible(True)
            
            # Render isolated 2D user interface workspace overlay
            menu.render()
        else:
            # Re-engage mouse lock and hide cursor exclusively during active gameplay
            pygame.event.set_grab(True)
            pygame.mouse.set_visible(False)
            
            # Continuously process ongoing keyboard layout input polling states using delta time
            camera.process_keyboard(dt)

            # Reset back-buffer clear color to match atmospheric dark fog boundaries color
            glClearColor(0.1, 0.1, 0.15, 1.0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            # Re-enable environmental volumetric fog shader state pipeline for 3D simulation space
            glEnable(GL_FOG)

            # Synchronize view transformations matrices before drawing spatial objects geometry assets
            camera.update_view()
            
            # Draw architectural asset spatial model structure instance
            glPushMatrix()
            house.draw()
            glPopMatrix()

        # Swap front and back buffer frame drawing blocks context
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()