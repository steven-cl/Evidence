from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
import math
import glm

class CameraFPS:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Detective position in the world (X, Y, Z)
        self.pos_x = 0.0
        self.pos_y = 1.5  # Eye height
        self.pos_z = 5.0
        
        # Head rotation (in degrees)
        self.pitch = 0.0   # Up / Down
        self.yaw = -90.0   # Left / Right (Starts facing center)

        # Camera direction vectors
        self.front_x = 0.0
        self.front_y = 0.0
        self.front_z = -1.0

        self.right_x = 1.0
        self.right_z = 0.0

        # Adjustable control parameters
        self.speed = 4.0        # Detective walking speed
        self.sensitivity = 0.1  # Mouse sensitivity
        
        # --- NUEVOS PARÁMETROS DE FÍSICA ---
        self.velocity_y = 0.0
        self.gravity = 9.8
        self.radius = 0.32 * 3.0        # Grosor del detective
        self.eye_height = 1.65 * 3.0    # Altura de los ojos
        self.speed = 4.0 * 3.0        # Ahora caminamos más rápido (12.0)

        # Update initial view vectors
        self.update_camera_vectors()

    def configure_projection(self):
        """
        Configures the camera perspective. Called at startup.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def update_camera_vectors(self):
        """
        Mathematically computes where the camera is looking based on Yaw and Pitch.
        """
        # Convert angles to radians for Python trigonometric functions
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        # Calculate the new Front vector (forward view)
        self.front_x = math.cos(yaw_rad) * math.cos(pitch_rad)
        self.front_y = math.sin(pitch_rad)
        self.front_z = math.sin(yaw_rad) * math.cos(pitch_rad)

        # Normalize the Front vector to keep speed constant
        length = math.sqrt(self.front_x**2 + self.front_y**2 + self.front_z**2)
        self.front_x /= length
        self.front_y /= length
        self.front_z /= length

        # Calculate the Right vector (camera right) using a planar cross product (without changing Y axis)
        # This prevents the detective from floating or sinking when moving while looking up/down
        r_length = math.sqrt(self.front_z**2 + (-self.front_x)**2)
        self.right_x = self.front_z / r_length
        self.right_z = -self.front_x / r_length

    def process_mouse(self):
        """
        Captures relative mouse movement and rotates the camera.
        """
        # Capture how much the mouse moved since the previous frame
        dx, dy = pygame.mouse.get_rel()

        # Apply sensitivity
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity  # Inverted for standard camera behavior

        # Clamp vertical look angle to avoid flipping upside down
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        # Recalculate vectors after changing rotation
        self.update_camera_vectors()
        
    def check_sphere_triangle(self, sphere_center, tri, sphere_type):
        # 1. EARLY OUT (Optimización para no perder FPS)
        if (sphere_center.x < tri.min_x or sphere_center.x > tri.max_x or
            sphere_center.y < tri.min_y or sphere_center.y > tri.max_y or
            sphere_center.z < tri.min_z or sphere_center.z > tri.max_z):
            return None

        # 2. Distancia al plano (con signo)
        dist = glm.dot(sphere_center - tri.a, tri.normal)
        
        # Detectamos si es pared (vertical) o piso/techo (horizontal)
        is_wall = abs(tri.normal.y) < 0.5
        is_floor = tri.normal.y >= 0.5
        is_ceiling = tri.normal.y <= -0.5
        
        if is_wall:
            # SI ES PARED: Colisión de DOBLE CARA
            if abs(dist) > self.radius:
                return None
        else:
            # --- LA CURA CONTRA LAS EXPLOSIONES FÍSICAS ---
            if is_floor:
                # Solo los PIES interactúan con los pisos.
                # Evita que tu cintura o cabeza te "aspiren" hacia arriba de la mesa.
                if sphere_type != 'feet':
                    return None
                
                # Tolerancia para caídas (lag)
                if dist > self.radius or dist < -0.6:
                    return None
            
            elif is_ceiling:
                # Solo la CABEZA interactúa con los techos.
                if sphere_type != 'head':
                    return None
                
                # No interactuar si estamos por encima del techo
                if dist > self.radius or dist < 0:
                    return None
                
        # 3. Proyectar el centro sobre el plano
        projected = sphere_center - (tri.normal * dist)
        
        # 4. Comprobación Baricéntrica (Dentro de los bordes del triángulo)
        edge0 = tri.b - tri.a
        edge1 = tri.c - tri.b
        edge2 = tri.a - tri.c
        
        c0 = projected - tri.a
        c1 = projected - tri.b
        c2 = projected - tri.c
        
        if (glm.dot(tri.normal, glm.cross(edge0, c0)) >= 0 and
            glm.dot(tri.normal, glm.cross(edge1, c1)) >= 0 and
            glm.dot(tri.normal, glm.cross(edge2, c2)) >= 0):
            
            # 5. EMPUJE FÍSICO
            if is_wall and dist < 0:
                # Si chocamos contra la espalda de una pared, empujamos hacia afuera
                penetration = self.radius - abs(dist)
                return -tri.normal * penetration
            else:
                # Chocamos de frente (o es piso/techo)
                penetration = self.radius - dist
                return tri.normal * penetration
                
        return None

    def process_keyboard(self, dt, colliders):
        keys = pygame.key.get_pressed()
        velocity = self.speed * dt

        # 1. Movimiento Predictivo
        next_x = self.pos_x
        next_z = self.pos_z

        if keys[pygame.K_w]:
            next_x += self.front_x * velocity
            next_z += self.front_z * velocity
        if keys[pygame.K_s]:
            next_x -= self.front_x * velocity
            next_z -= self.front_z * velocity
        if keys[pygame.K_a]:
            next_x += self.right_x * velocity
            next_z += self.right_z * velocity
        if keys[pygame.K_d]:
            next_x -= self.right_x * velocity
            next_z -= self.right_z * velocity

        self.velocity_y -= self.gravity * dt
        next_y = self.pos_y + (self.velocity_y * dt)

        # ---------------------------------------------------------
        # 2. EL MUÑECO DE NIEVE COMPLETO (3 Esferas)
        # ---------------------------------------------------------
        feet_pos = glm.vec3(next_x, next_y - self.eye_height + self.radius, next_z)
        torso_pos = glm.vec3(next_x, next_y - (self.eye_height / 2), next_z)
        head_pos = glm.vec3(next_x, next_y, next_z)

        # 3. Calculamos la física pasando el "Rol" de cada esfera
        is_grounded = False
        
        for tri in colliders:
            # Evaluar Pies (Pasamos 'feet')
            push_feet = self.check_sphere_triangle(feet_pos, tri, 'feet')
            if push_feet is not None:
                feet_pos += push_feet
                torso_pos += push_feet
                head_pos += push_feet
                if tri.normal.y > 0.5:
                    is_grounded = True
                    self.velocity_y = 0.0

            # Evaluar Torso (Pasamos 'torso')
            push_torso = self.check_sphere_triangle(torso_pos, tri, 'torso')
            if push_torso is not None:
                feet_pos += push_torso
                torso_pos += push_torso
                head_pos += push_torso

            # Evaluar Cabeza (Pasamos 'head')
            push_head = self.check_sphere_triangle(head_pos, tri, 'head')
            if push_head is not None:
                feet_pos += push_head
                torso_pos += push_head
                head_pos += push_head

        # 4. APLICAMOS el movimiento
        self.pos_x = feet_pos.x
        self.pos_z = feet_pos.z
        self.pos_y = feet_pos.y + self.eye_height - self.radius

    def update_view(self):
        """
        Applies final OpenGL transformations using the LookAt matrix.
        Runs on each cycle of the main game loop.
        """
        glLoadIdentity()
        
        # Point in 3D space where the detective is looking
        target_x = self.pos_x + self.front_x
        target_y = self.pos_y + self.front_y
        target_z = self.pos_z + self.front_z

        # Define camera: Current position, target point, up vector (Y=1)
        gluLookAt(
            self.pos_x, self.pos_y, self.pos_z,
            target_x, target_y, target_z,
            0.0, 1.0, 0.0
        )