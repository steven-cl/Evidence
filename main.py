import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Import project modules
from obj_loader import Model3D
from camera import CameraFPS
from pared import Texture 
from skybox import Skybox

def setup_fog():
    """Configure the global fog parameters in OpenGL"""
    glEnable(GL_FOG)  # Enable fog rendering
    glFogf(GL_FOG_START, 5.0)   # The fog starts at 5 meters from the camera
    glFogf(GL_FOG_END, 18.0)    # The fog fully obscures objects at 18 meters or more, creating a sense of depth and mystery
    
    # Define the fog mode (GL_EXP2 provides a subtle exponential fog)
    glFogi(GL_FOG_MODE, GL_EXP2)

    # Define the density (Values between 0.01 and 0.1 control how fast the fog thickens)
    glFogf(GL_FOG_DENSITY, 0.03)

    # Define the fog color (R, G, B, A)
    # Use a dark grayish-blue to maintain a nocturnal, mysterious atmosphere
    fog_color = [0.1, 0.1, 0.15, 1.0]
    glFogfv(GL_FOG_COLOR, fog_color)
    
    # Set calculation quality (GL_NICEST evaluates the fog per-pixel)
    glHint(GL_FOG_HINT, GL_NICEST)

def main():
    # Window setup
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    # Mouse control settings: hide cursor and capture it in the window
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # Camera setup
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

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # Initialize the fog
    setup_fog()

    # Load house model
    house = Model3D('source/models/RenewHouse.obj')

    # Textures are loaded below — do not modify this section
    
    config_visual = {

        # Main texturing
        "matParedPrincipal": Texture('source/textures/texture_wall.jpg'),
        "matPared": Texture('source/textures/texture_wall.jpg'),
        "matPared2": Texture('source/textures/texture_wall.jpg'),
        "matPared3": Texture('source/textures/texture_wall.jpg'),
        "matPared4": Texture('source/textures/texture_wall.jpg'),
        "matPared5": Texture('source/textures/texture_wall.jpg'),
        "matPared6": Texture('source/textures/texture_wall.jpg'),
        "matMarcoPuerta": (0.45, 0.24, 0.1),
        "matPuerta": Texture('source/textures/texture_wood.jpg'),
        "matPerillaFron": (0.05, 0.05, 0.05),
        "matMarcoPuerta2": (0.45, 0.24, 0.1),
        "matPuerta2": Texture('source/textures/texture_wood.jpg'),
        "matPerillaFron2": (0.05, 0.05, 0.05),
        "matMarcoPuerta3": (0.45, 0.24, 0.1),
        "matPuerta3": Texture('source/textures/texture_wood.jpg'),
        "matPerillaFron3": (0.05, 0.05, 0.05),
        "matMarcoPuerta4": (0.45, 0.24, 0.1),
        "matPuerta4": Texture('source/textures/texture_wood.jpg'),
        "matPerillaFron4": (0.05, 0.05, 0.05),
        "matMarcoPuerta5": (0.45, 0.24, 0.1),
        "matPuerta5": Texture('source/textures/texture_wood.jpg'),
        "matPerillaFron5": (0.05, 0.05, 0.05),
        "matMarcoPuerta6": (0.45, 0.24, 0.1),
        "matPuerta6": Texture('source/textures/texture_wood.jpg'),
        "matPerillaFron6": (0.05, 0.05, 0.05),
        "matPerillaback": (0.05, 0.05, 0.05),
        "matPerillaback2": (0.05, 0.05, 0.05),
        "matPerillaback3": (0.05, 0.05, 0.05),
        "matPerillaback4": (0.05, 0.05, 0.05),
        "matPerillaback5": (0.05, 0.05, 0.05),
        "matPerillaback6": (0.05, 0.05, 0.05),




        # Living room
        "matSofa": Texture('source/textures/texture_tela.jpg'),
        "matSillon": Texture('source/textures/texture_tela.jpg'),
        "matMesaTV": Texture('source/textures/texture_muebles.jpg'),
        "matLamp": Texture('source/textures/texture_blood.jpg'),
        "matLamp2": Texture('source/textures/texture_blood.jpg'),
        "matLamp3": Texture('source/textures/texture_blood.jpg'),
        "matLamp4": Texture('source/textures/texture_blood.jpg'),
        "matLamp5": Texture('source/textures/texture_blood.jpg'),
        "matTV":   (0.05, 0.05, 0.05),
        "matJarron": (0.55, 0.27, 0.08),
        "matBotella":   (0.05, 0.05, 0.05),
        "matBotella2":   (0.05, 0.05, 0.05),
        "matBotella3":   (0.05, 0.05, 0.05),
        "matBotella4":   (0.05, 0.05, 0.05),
        "matMesaSala": Texture('source/textures/texture_muebles.jpg'),
        "matLuz": (0.05, 0.05, 0.05),
        "matLuz2": (0.05, 0.05, 0.05),
        "matLuz3": (0.05, 0.05, 0.05),
        "matLuz4": (0.05, 0.05, 0.05),
        "matLuz5": (0.05, 0.05, 0.05),
        "matLuz6": (0.05, 0.05, 0.05),
        "matLuz7": (0.05, 0.05, 0.05),
        "matLuz8": (0.05, 0.05, 0.05),
      
        # Decorations
        "matDeco": Texture('source/textures/texture_deco.jpg'),
        "matDeco2": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco3": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco4": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco5": Texture('source/textures/texture_Deco2.jpg'),
        # Kitchen
        "matCocina": Texture('source/textures/texture_base_kitchen.jpg'),
        "matGabinete": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete2": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete3": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete4": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete5": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete6": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete7": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete8": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete9": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete10": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete11": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete12": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete13": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete14": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete15": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete16": Texture('source/textures/texture_kitchen.jpg'),
        "matManivela": Texture('source/textures/texture_metal.jpg'),
        "matManivela2": Texture('source/textures/texture_metal.jpg'),
        "matManivela3": Texture('source/textures/texture_metal.jpg'),
        "matManivela4": Texture('source/textures/texture_metal.jpg'),
        "matManivela5": Texture('source/textures/texture_metal.jpg'),
        "matManivela6": Texture('source/textures/texture_metal.jpg'),
        "matManivela7": Texture('source/textures/texture_metal.jpg'),
        "matManivela8": Texture('source/textures/texture_metal.jpg'),
        "matManivela9": Texture('source/textures/texture_metal.jpg'),
        "matManivela10": Texture('source/textures/texture_metal.jpg'),
        "matManivela11": Texture('source/textures/texture_metal.jpg'),
        "matManivela12": Texture('source/textures/texture_metal.jpg'),
        "matManivela13": Texture('source/textures/texture_metal.jpg'),
        "matManivela14": Texture('source/textures/texture_metal.jpg'),
        "matManivela15": Texture('source/textures/texture_metal.jpg'),
        "matManivela16": Texture('source/textures/texture_metal.jpg'),
        "matPerillaCocina": Texture('source/textures/texture_metal.jpg'),
        "matPerillaCocina2": Texture('source/textures/texture_metal.jpg'),
        "matQuemadores": Texture('source/textures/texture_metal.jpg'),
        "matComedor": Texture('source/textures/texture_wood.jpg'),
        "matSilla": Texture('source/textures/texture_wood.jpg'),
        "matSilla2": Texture('source/textures/texture_wood.jpg'),
        "matSilla3": Texture('source/textures/texture_wood.jpg'),
        "matSilla4": Texture('source/textures/texture_wood.jpg'),
        "matHorno": Texture('source/textures/texture_horno.jpg'),
        # Bedroom textures start here
        "matBaseCama": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama2": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama3": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama4": Texture('source/textures/texture_wood.jpg'),
        "matColchon": Texture('source/textures/texture_tela.jpg'),
        "matColchon2": Texture('source/textures/texture_tela.jpg'),
        "matColchon3": Texture('source/textures/texture_tela.jpg'),
        "matColchon4": Texture('source/textures/texture_tela.jpg'),
        
        # Clocks
        "matReloj": Texture('source/textures/texture_shining.jpg'),
        "matRelojHoras": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora2": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora3": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora4": Texture('source/textures/texture_watch.jpg'),
        


        
        "matTecho": Texture('source/textures/texture_techo.jpg'),
        "matPiso": Texture('source/textures/texture_floor.jpg'),
        
        
        
                                            
    }

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    glClearColor(0.1, 0.1, 0.15, 1.0)

    # Main loop
    while running:
        # Calculate Delta Time in seconds (example. at 60 FPS, dt will be ~0.0166)
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Exit the game if the user presses the ESC key
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Capture and integrate mouse and keyboard movement
        camera.process_mouse()
        camera.process_keyboard(dt)

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

        # Update camera before drawing the world
        camera.update_view()
        
        # Draw the house model
        glPushMatrix()
        
        # Iterate over each material composing the house
        for nombre_mat in house.materiales.keys():
            
            if nombre_mat in config_visual:
                asignacion = config_visual[nombre_mat]
                
                # Detect whether the assignment is a Texture instance or an RGB color tuple
                if isinstance(asignacion, Texture):
                    glEnable(GL_TEXTURE_2D)
                    glColor3f(1.0, 1.0, 1.0) # Force white so the texture's colors are not altered
                    asignacion.bind()
                else:
                    glDisable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, 0)
                    glColor3f(asignacion[0], asignacion[1], asignacion[2]) # Apply RGB color
            else:
                # If a material is missing or the model lacks UVs, render it in gray
                glDisable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, 0)
                glColor3f(0.6, 0.6, 0.6)
                
            # Draw the geometry for this specific material
            house.draw_material(nombre_mat)
            
        glPopMatrix()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()