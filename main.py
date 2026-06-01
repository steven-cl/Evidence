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

    # Configuración del control del mouse: ocultar cursor y capturarlo en la ventana
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)

    # 2. Instantiate and configure the Camera
    camera = CameraFPS(screen_width, screen_height)
    camera.configure_projection()
    
    # Valores iniciales fijados por el equipo
    camera.pos_x = 0.0 
    camera.pos_y = 1.5  # Altura de visualización inicial
    camera.pos_z = 8.0   
    camera.pitch = 0.0  # Mirando hacia abajo inicialmente
    camera.yaw = -90.0   # Orientación frontal estándar
    
    # Sincronizar los vectores matemáticos internos con los valores manuales de arriba
    camera.update_camera_vectors()

    # 3. Enable depth testing
    glEnable(GL_DEPTH_TEST)

    # 4. Instantiate the house model
    house = Model3D('source/models/RenewHouse.obj')

    clock = pygame.time.Clock()
    running = True

    # 5. Main loop
    while running:
        # Calcular Delta Time en segundos (ej. a 60 FPS, dt valdrá ~0.0166)
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Permitir liberar el mouse o cerrar el juego rápido con la tecla ESCAPE
                if event.key == pygame.K_ESCAPE:
                    running = False

        # Capturar e integrar el movimiento del mouse y del teclado
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