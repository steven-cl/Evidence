import pygame
from pygame.locals import *
from OpenGL.GL import *

# Importar módulos del proyecto
from obj_loader import Model3D
from camera import CameraFPS
from pared import Texture 

def main():
    # 1. Window setup
    pygame.init()
    screen_width, screen_height = 800, 600
    pygame.display.set_mode((screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Evidence - Resolve the Mystery")

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # 2. Instantiate and configure the Camera
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    camera.pos_x = 0.0 
    camera.pos_y = 1.5  
    camera.pos_z = 8.0   
    camera.pitch = 0.0  
    camera.yaw = -90.0   
    camera.update_camera_vectors()

    # 3. Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # 4. Instantiate the house model
    house = Model3D('source/models/RenewHouse.obj')

    # Desde aqui se cargan las texturas, no toquen esta vaina por lo que mas quieran
    
    config_visual = {

        #Texturizado Principal
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




        #sala
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
      
        #Decoraciones
        "matDeco": Texture('source/textures/texture_deco.jpg'),
        "matDeco2": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco3": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco4": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco5": Texture('source/textures/texture_Deco2.jpg'),
        #Cocina
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
        #aqui empiezo a texturizar las camas
        "matBaseCama": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama2": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama3": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama4": Texture('source/textures/texture_wood.jpg'),
        "matColchon": Texture('source/textures/texture_tela.jpg'),
        "matColchon2": Texture('source/textures/texture_tela.jpg'),
        "matColchon3": Texture('source/textures/texture_tela.jpg'),
        "matColchon4": Texture('source/textures/texture_tela.jpg'),
        
        #Relojes
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

    # 6. Main loop
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        camera.process_mouse()
        camera.process_keyboard(dt)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # 7. Update camera before drawing the world
        camera.update_view()
        
        # 8. Draw the house model
        glPushMatrix()
        
        # Iterar por cada material que compone la casa de forma rápida
        for nombre_mat in house.materiales.keys():
            
            if nombre_mat in config_visual:
                asignacion = config_visual[nombre_mat]
                
                # Detectar si le asignamos una clase Texture o una tupla de color
                if isinstance(asignacion, Texture):
                    glEnable(GL_TEXTURE_2D)
                    glColor3f(1.0, 1.0, 1.0) # Forzar blanco para que la textura no se pinte de otro color
                    asignacion.bind()
                else:
                    glDisable(GL_TEXTURE_2D)
                    glBindTexture(GL_TEXTURE_2D, 0)
                    glColor3f(asignacion[0], asignacion[1], asignacion[2]) # Aplicar color RGB
            else:
                # En dado caso se me pasa o agrego un modelo sin un UV MAP simplementa se pinta de gris creo
                
                glDisable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, 0)
                glColor3f(0.6, 0.6, 0.6)
                
            # Dibujar la geometría de este material específico
            house.draw_material(nombre_mat)
            
        glPopMatrix()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()