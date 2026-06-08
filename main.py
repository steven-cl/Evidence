import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Import our own modules
from obj_loader import Model3D
from camera import CameraFPS
from pared import Texture 
from skybox import Skybox
from menu import MainMenu
from door_In import Door

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
    # Window setup
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    # Initialize Menu UI instance after Pygame display setup
    menu = MainMenu(screen_width, screen_height)

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

    # Initialize skybox
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
        "matPerilla": (0.05, 0.05, 0.05),
        "matMarcoPuerta2": (0.45, 0.24, 0.1),
        "matPuerta2": Texture('source/textures/texture_wood.jpg'),
        "matP2": (0.05, 0.05, 0.05),
        "matMarcoPuerta3": (0.45, 0.24, 0.1),
        "matPuerta3": Texture('source/textures/texture_wood.jpg'),
        "matP3": (0.05, 0.05, 0.05),
        "matMarcoPuerta4": (0.45, 0.24, 0.1),
        "matPuerta4": Texture('source/textures/texture_wood.jpg'),
        "matP4": (0.05, 0.05, 0.05),
        "matMarcoPuerta5": (0.45, 0.24, 0.1),
        "matPuerta5": Texture('source/textures/texture_wood.jpg'),
        "matP5": (0.05, 0.05, 0.05),
        "matMarcoPuerta6": (0.45, 0.24, 0.1),
        "matPuerta6": Texture('source/textures/texture_wood.jpg'),
        "matP6": (0.05, 0.05, 0.05),
        "matMarcoPuerta7": (0.45, 0.24, 0.1),
        "matPuerta7": Texture('source/textures/texture_wood.jpg'),
        "matP7": (0.05, 0.05, 0.05),
        




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

    # the doors and knobs, why? well they are separate objects, that is how I made them in Blender
    
    settingDoors = [
        Door("matPuerta", -2.9858, 1.379, 0.37832, "matPerilla", -3.7616, 1.0498, 0.45044),
        Door("matPuerta2", 0.96918, 1.379, -1.5806, "matP2", 0.95666, 1.05, -0.80633),
        Door("matPuerta3", 3.6967, 1.379, 1.5812, "matP3", 3.7112, 1.05, 0.81052),
        Door("matPuerta4", 3.6952, 1.379, -0.70732, "matP4", 3.7136, 1.05, -1.4746),
        Door("matPuerta5", 3.6953, 1.379, -3.466, "matP5", 3.7113, 1.05, -4.2389),
        Door("matPuerta7", 2.8285, 1.379, -5.9659, "matP7", 2.0526, 1.05, -5.9807),# This is our principal door
        #Door("matPuerta6", -2.9858, 1.379, 0.37832, "matP6", -3.7616, 1.0498, 0.45044), Do not activate this one, it will only work with a key
    ]

    # setting the filter
    mat_doors = set()
    for p in settingDoors:
        mat_doors.add(p.mat)
        mat_doors.add(p.mat_perilla)

    clock = pygame.time.Clock()
    running = True

    glClearColor(0.1, 0.1, 0.15, 1.0)

    # 5. Main loop
    while running:
        # Calculate Delta Time in seconds
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

        # Swap front and back buffer frame drawing blocks context
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()