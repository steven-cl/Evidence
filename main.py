import pygame
from pygame.locals import * # pyright: ignore[reportMissingImports]
from OpenGL.GL import * # pyright: ignore[reportMissingImports]
from menu import MainMenu

# Import internal gameplay modules
from obj_loader import Model3D
from camera import CameraFPS

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
    
    # Initial transform configuration values set by development team
    camera.pos_x = 0.0 
    camera.pos_y = 1.5  # Standard eye-level visual height
    camera.pos_z = 8.0   
    camera.pitch = 0.0  # Initially looking straight ahead horizontally
    camera.yaw = -90.0  # Standard frontal world orientation face
    
    # Synchronize internal mathematical target vectors with manually defined coordinates
    camera.update_camera_vectors()

    # 3. Enable standard hardware z-buffer depth testing
    glEnable(GL_DEPTH_TEST)

    # 4. Initialize global environmental volumetric fog
    setup_fog()

    # 5. Instantiate the environment house assets model
    house = Model3D('source/models/RenewHouse.obj')

    clock = pygame.time.Clock()
    running = True

    # 6. Main application engine frame loop
    while running:
        # Calculate Delta Time in seconds (e.g., at 60 FPS, dt yields approx. 0.0166s)
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