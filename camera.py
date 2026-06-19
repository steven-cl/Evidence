from OpenGL.GL import * # pyright: ignore[reportMissingImports]
from OpenGL.GLU import * # pyright: ignore[reportMissingImports]
import pygame # pyright: ignore[reportMissingImports]
import math
import glm

class CameraFPS:
    def __init__(self, width, height):
        """
        Initializes the first-person camera parameters, spatial vectors, 
        physics thresholds, and movement state variables.
        """
        self.width = width
        self.height = height

        # Camera spatial coordinates
        self.pos_x = 0.0
        self.pos_y = 1.5 
        self.pos_z = 5.0
        
        # Rotational state in degrees
        self.pitch = 0.0   
        self.yaw = -90.0   

        # Directional vectors
        self.front_x = 0.0
        self.front_y = 0.0
        self.front_z = -1.0

        self.right_x = 1.0
        self.right_z = 0.0

        # Input and physics parameters
        self.sensitivity = 0.1  
        self.jump_force = 2.5
        
        self.velocity_y = 0.0
        self.gravity = 9.8
        self.radius = 0.32        
        self.eye_height = 1.60    
        self.speed = 4.0          
        
        # Stance modifiers
        self.crouch_speed = 2.0 
        self.crouch_height = 1.0  
        
        # Stance tracker to anchor the feet during height transitions
        self.current_stance = self.eye_height

        self.update_camera_vectors()

    def configure_projection(self):
        """
        Configures the perspective matrix rendering parameters.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def update_camera_vectors(self):
        """
        Computes the Front and Right directional vectors via spherical coordinates.
        """
        yaw_rad = math.radians(self.yaw)
        pitch_rad = math.radians(self.pitch)

        self.front_x = math.cos(yaw_rad) * math.cos(pitch_rad)
        self.front_y = math.sin(pitch_rad)
        self.front_z = math.sin(yaw_rad) * math.cos(pitch_rad)

        length = math.sqrt(self.front_x**2 + self.front_y**2 + self.front_z**2)
        self.front_x /= length
        self.front_y /= length
        self.front_z /= length

        r_length = math.sqrt(self.front_z**2 + (-self.front_x)**2)
        self.right_x = self.front_z / r_length
        self.right_z = -self.front_x / r_length

    def process_mouse(self, dx, dy):
        """
        Applies mouse deltas to camera rotation values with axis clamping.
        """
        self.yaw += dx * self.sensitivity
        self.pitch -= dy * self.sensitivity  

        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0

        self.update_camera_vectors()
        
    def check_sphere_triangle(self, sphere_center, tri, sphere_type):
        """
        Executes collision detection via bounding spheres and barycentric projection.
        """
        if (sphere_center.x < tri.min_x or sphere_center.x > tri.max_x or
            sphere_center.y < tri.min_y or sphere_center.y > tri.max_y or
            sphere_center.z < tri.min_z or sphere_center.z > tri.max_z):
            return None

        dist = glm.dot(sphere_center - tri.a, tri.normal)
        
        is_wall = abs(tri.normal.y) < 0.5
        is_floor = tri.normal.y >= 0.5
        is_ceiling = tri.normal.y <= -0.5
        
        has_double_sided = getattr(tri, 'is_double_sided', True)
        is_climbable = getattr(tri, 'is_climbable', False) 

        if is_wall:
            if has_double_sided:
                if abs(dist) > self.radius:
                    return None
            else:
                if dist > self.radius or dist < 0.0:
                    return None
        else:
            if is_floor:
                if sphere_type != 'feet':
                    return None
                
                if has_double_sided:
                    if dist > self.radius or dist < -0.1:
                        return None
                else:
                    if is_climbable:
                        if dist > self.radius or dist < -0.4:
                            return None
                    else:
                        if dist > self.radius or dist < -0.1:
                            return None
            elif is_ceiling:
                if sphere_type != 'head':
                    return None
                if dist > self.radius or dist < 0:
                    return None
                
        projected = sphere_center - (tri.normal * dist)
        
        edge0 = tri.b - tri.a
        edge1 = tri.c - tri.b
        edge2 = tri.a - tri.c
        
        c0 = projected - tri.a
        c1 = projected - tri.b
        c2 = projected - tri.c
        
        if (glm.dot(tri.normal, glm.cross(edge0, c0)) >= 0 and
            glm.dot(tri.normal, glm.cross(edge1, c1)) >= 0 and
            glm.dot(tri.normal, glm.cross(edge2, c2)) >= 0):
            
            if is_wall:
                if has_double_sided and dist < 0:
                    penetration = self.radius - abs(dist)
                    push = -tri.normal * penetration
                else:
                    penetration = self.radius - dist
                    push = tri.normal * penetration
                
                push.y = 0.0 
                return push
            else:
                penetration = self.radius - dist
                return tri.normal * penetration
                
        return None

    def process_keyboard(self, dt, colliders):
        """
        Parses keyboard states into velocity matrices and executes dynamic 
        bounding box relaxation against world colliders.
        """
        keys = pygame.key.get_pressed()

        # Determine target stance based on input
        target_stance = self.crouch_height if keys[pygame.K_LSHIFT] else self.eye_height

        # Instantly shift camera Y to keep the physical feet anchored to the ground.
        # This prevents the feet from teleporting upwards and artificially triggering a fall through objects.
        if target_stance != getattr(self, 'current_stance', self.eye_height):
            self.pos_y += (target_stance - self.current_stance)
            self.current_stance = target_stance

        # Crouching reduces base speed
        if keys[pygame.K_LSHIFT]:
            self.speed = self.crouch_speed
        else:
            self.speed = 4.0
        
        velocity = self.speed * dt
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
            
        if keys[pygame.K_SPACE] and self.is_grounded:
            self.velocity_y = self.jump_force
            self.is_grounded = False 

        self.velocity_y -= self.gravity * dt
        next_y = self.pos_y + (self.velocity_y * dt)

        # 2. Define stacked bounding spheres based on the anchored stance
        self.feet_pos = glm.vec3(next_x, next_y - self.current_stance + self.radius, next_z)
        self.torso_pos = glm.vec3(next_x, next_y - (self.current_stance / 2), next_z)
        self.head_pos = glm.vec3(next_x, next_y, next_z)

        self.is_grounded = False
        
        # 3. Multi-pass relaxation loop to prevent corner-clipping
        for _ in range(2): 
            for tri in colliders:
                push_feet = self.check_sphere_triangle(self.feet_pos, tri, 'feet')
                if push_feet is not None:
                    self.feet_pos += push_feet
                    self.torso_pos += push_feet
                    self.head_pos += push_feet
                    if tri.normal.y > 0.5:
                        self.is_grounded = True
                        self.velocity_y = 0.0

                push_torso = self.check_sphere_triangle(self.torso_pos, tri, 'torso')
                if push_torso is not None:
                    self.feet_pos += push_torso
                    self.torso_pos += push_torso
                    self.head_pos += push_torso

                push_head = self.check_sphere_triangle(self.head_pos, tri, 'head')
                if push_head is not None:
                    self.feet_pos += push_head
                    self.torso_pos += push_head
                    self.head_pos += push_head

        # 4. Apply the finalized and validated relaxation vectors relative to feet location
        self.pos_x = self.feet_pos.x
        self.pos_z = self.feet_pos.z
        self.pos_y = self.feet_pos.y + self.current_stance - self.radius

    def update_view(self):
        """
        Executes rendering transformations via LookAt matrix projection.
        """
        glLoadIdentity()
        
        target_x = self.pos_x + self.front_x
        target_y = self.pos_y + self.front_y
        target_z = self.pos_z + self.front_z

        gluLookAt(
            self.pos_x, self.pos_y, self.pos_z,
            target_x, target_y, target_z,
            0.0, 1.0, 0.0
        )