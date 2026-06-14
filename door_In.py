import math
from OpenGL.GL import *
from obj_loader import Triangle
from pared import Texture 
import glm

class Door:
    # Defines the opening direction (1 or -1) and the rotation axis for the knob ('z' or 'x')
    def __init__(self, mat_puerta, px, py, pz, mat_perilla, kx, ky, kz, dir_apertura=1.0, eje_perilla='z'):
        self.mat = mat_puerta
        self.px = px
        self.py = py
        self.pz = pz
        
        self.mat_perilla = mat_perilla
        self.kx = kx
        self.ky = ky
        self.kz = kz
        
        self.dir_apertura = dir_apertura
        self.eje_perilla = eje_perilla.lower()
        
        self.is_open = False
        self.angle = 0.0
        self.target = 0.0
        self.speed = 200.0 
        self.knob_angle = 0.0
        
        
    def get_distance(self, player_x, player_z):
        # Calculate the center point of the door
        cPoint_x = (self.px + self.kx) / 2
        cPoint_z = (self.pz + self.kz) / 2
        return math.hypot(cPoint_x - player_x, cPoint_z - player_z)
    
    
    def doorAction(self, player_x, player_z, cam_dir_x, cam_dir_z):
        # Calculate the center point of the door
        cPoint_x = (self.px + self.kx) / 2
        cPoint_z = (self.pz + self.kz) / 2
        
        # Measure the distance between the player and the door center
        dist = math.hypot(cPoint_x - player_x, cPoint_z - player_z)
        if dist > 2.0:
            return False
            
        # Calculate the directional vector from the player to the door
        if dist == 0: 
            return False
        vec_x = (cPoint_x - player_x) / dist
        vec_z = (cPoint_z - player_z) / dist
        
        # Normalize the camera direction vector
        cam_length = math.hypot(cam_dir_x, cam_dir_z)
        if cam_length == 0:
            return False
        cam_dir_x /= cam_length
        cam_dir_z /= cam_length
        
        # Compute the dot product between the view vector and the door vector
        dot_product = (vec_x * cam_dir_x) + (vec_z * cam_dir_z)
        
        # Return True if the door is within the player's field of view
        return dot_product > 0.85
    
    
    def toggle(self):
        self.is_open = not self.is_open
        # Set the target rotation angle based on the designated opening direction
        self.target = (90.0 * self.dir_apertura) if self.is_open else 0.0


    def update(self, dt):
        # Interpolate the current angle towards the target angle based on delta time
        if self.angle < self.target:
            self.angle = min(self.angle + self.speed * dt, self.target)
        elif self.angle > self.target:
            self.angle = max(self.angle - self.speed * dt, self.target)


    def _aplicar_material(self, mat_name, cfg):
        if mat_name in cfg:
            val = cfg[mat_name]
            if isinstance(val, Texture):
                glEnable(GL_TEXTURE_2D)
                glColor3f(1.0, 1.0, 1.0)
                val.bind()
            else:
                glDisable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, 0)
                glColor3f(val[0], val[1], val[2])
        else:
            glDisable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
            glColor3f(0.5, 0.5, 0.5)


    def draw(self, house_model, cfg):
        glPushMatrix()
        
        # Apply transformations and render the main door geometry
        glTranslatef(self.px, self.py, self.pz)
        glRotatef(self.angle, 0, 1, 0)
        glTranslatef(-self.px, -self.py, -self.pz)
        
        self._aplicar_material(self.mat, cfg)
        house_model.draw_material(self.mat)
        
        # Apply transformations and render the door knob geometry
        glTranslatef(self.kx, self.ky, self.kz)
        glTranslatef(-self.kx, -self.ky, -self.kz)
        self._aplicar_material(self.mat_perilla, cfg)
        house_model.draw_material(self.mat_perilla)
        
        glPopMatrix()
        
    def get_transformed_triangles(self, house_model):
        """
        Transforms the door's original triangles using PyGLM matrices 
        to match its active rotation angle in real-time.
        """
        transformed_list = []
        if self.mat not in house_model.door_source_triangles:
            return transformed_list
            
        # Replicate the exact transform sequence from the draw() method using PyGLM
        matrix = glm.mat4(1.0)
        matrix = glm.translate(matrix, glm.vec3(self.px, self.py, self.pz))
        matrix = glm.rotate(matrix, glm.radians(self.angle), glm.vec3(0, 1, 0))
        matrix = glm.translate(matrix, glm.vec3(-self.px, -self.py, -self.pz))
        
        # Ensure proper type hinting for the triangle object during iteration
        for tri in house_model.door_source_triangles[self.mat]:
            tri_obj: Triangle = tri 
            
            t_a = glm.vec3(matrix * glm.vec4(tri_obj.a, 1.0))
            t_b = glm.vec3(matrix * glm.vec4(tri_obj.b, 1.0))
            t_c = glm.vec3(matrix * glm.vec4(tri_obj.c, 1.0))
            
            transformed_list.append(Triangle(t_a, t_b, t_c))
            
        return transformed_list