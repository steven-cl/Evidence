from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import math

class CameraFPS:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Posición del detective en el mundo (X, Y, Z)
        self.pos_x = 0.0
        self.pos_y = 1.5  # Altura de los ojos
        self.pos_z = 5.0
        
        # Rotación de la cabeza (en grados)
        self.pitch = 0.0   # Arriba / Abajo
        self.yaw = -90.0   # Izquierda / Derecha (Inicia mirando al centro)

        # Vectores de dirección de la cámara
        self.front_x = 0.0
        self.front_y = 0.0
        self.front_z = -1.0

        self.right_x = 1.0
        self.right_z = 0.0

        # Parámetros de control ajustables
        self.speed = 4.0        # Velocidad de caminata del detective
        self.sensitivity = 0.1  # Sensibilidad del mouse

        # Actualiza los vectores iniciales de la mirada
        self.update_camera_vectors()

    def configure_projection(self):
        """
        Configura la perspectiva de la cámara. Se llama al inicio.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def update_camera_vectors(self):
        """
        Calcula matemáticamente hacia dónde está mirando la cámara basándose en Yaw y Pitch.
        """
        # Convertir ángulos a radianes para las funciones trigonométricas de Python
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        # Calcular el nuevo vector Front (Mirada hacia adelante)
        self.front_x = math.cos(yaw_rad) * math.cos(pitch_rad)
        self.front_y = math.sin(pitch_rad)
        self.front_z = math.sin(yaw_rad) * math.cos(pitch_rad)

        # Normalizar el vector Front para mantener velocidad constante
        length = math.sqrt(self.front_x**2 + self.front_y**2 + self.front_z**2)
        self.front_x /= length
        self.front_y /= length
        self.front_z /= length

        # Calcular el vector Right (Derecha de la cámara) mediante Producto Cruz plano (sin alterar eje Y)
        # Esto evita que el detective flote o se hunda al avanzar mirando hacia arriba/abajo
        r_length = math.sqrt(self.front_z**2 + (-self.front_x)**2)
        self.right_x = self.front_z / r_length
        self.right_z = -self.front_x / r_length

    def process_mouse(self):
        """
        Captura el movimiento relativo del mouse y rota la cámara.
        """
        # Captura cuánto se movió el mouse desde el fotograma anterior
        dx, dy = pygame.mouse.get_rel()

        # Aplicar sensibilidad
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity  # Invertido para comportamiento estándar de cámara

        # Restringir el ángulo de mirada vertical para evitar que se ponga de cabeza
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # Recalcular vectores tras cambiar la rotación
        self.update_camera_vectors()

    def process_keyboard(self, dt):
        """
        Mueve la posición del detective según las teclas presionadas.
        dt: Delta Time (tiempo transcurrido por fotograma) para asegurar movimiento homogéneo.
        """
        keys = pygame.key.get_pressed()
        velocity = self.speed * dt

        # Movimiento hacia Adelante / Atrás en el plano horizontal (X, Z)
        if keys[pygame.K_w]:
            self.pos_x += self.front_x * velocity
            self.pos_z += self.front_z * velocity
        if keys[pygame.K_s]:
            self.pos_x -= self.front_x * velocity
            self.pos_z -= self.front_z * velocity

        # Desplazamiento lateral (Strafe) Izquierda / Derecha
        if keys[pygame.K_a]:
            self.pos_x += self.right_x * velocity
            self.pos_z += self.right_z * velocity
        if keys[pygame.K_d]:
            self.pos_x -= self.right_x * velocity
            self.pos_z -= self.right_z * velocity

    def update_view(self):
        """
        Aplica las transformaciones finales a OpenGL usando la matriz LookAt.
        Se ejecuta en cada ciclo del bucle principal del juego.
        """
        glLoadIdentity()
        
        # Punto en el espacio 3D hacia donde mira el detective
        target_x = self.pos_x + self.front_x
        target_y = self.pos_y + self.front_y
        target_z = self.pos_z + self.front_z

        # Define la cámara: Posición actual, Punto de mira, Vector arriba (Y=1)
        gluLookAt(
            self.pos_x, self.pos_y, self.pos_z,
            target_x, target_y, target_z,
            0.0, 1.0, 0.0
        )