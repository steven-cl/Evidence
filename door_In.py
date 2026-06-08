import math
from OpenGL.GL import *
from pared import Texture 

class Door:
    # Added open_direction (1 or -1) and knob_axis ('z' or 'x')
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
        
        cPoint_x = (self.px + self.kx) / 2
        cPoint_z = (self.pz + self.kz) / 2
        return math.hypot(cPoint_x - player_x, cPoint_z - player_z)
    
   
    def doorAction(self, player_x, player_z, cam_dir_x, cam_dir_z):

        #we calculate the center of the door
        cPoint_x = (self.px + self.kx) / 2
        cPoint_z = (self.pz + self.kz) / 2
        
        # Distance is measured
        dist = math.hypot(cPoint_x - player_x, cPoint_z - player_z)
        if dist > 2.0:
            return False
            
        #vector form player to the doors
        if dist == 0: 
            return False
        vec_x = (cPoint_x - player_x) / dist
        vec_z = (cPoint_z - player_z) / dist
        
        # we normalize the camera view
        cam_length = math.hypot(cam_dir_x, cam_dir_z)
        if cam_length == 0:
            return False
        cam_dir_x /= cam_length
        cam_dir_z /= cam_length
        
        #Dot Product
        dot_product = (vec_x * cam_dir_x) + (vec_z * cam_dir_z)
        #if > 0.85 it is within your fov
        return dot_product > 0.85
    


    def toggle(self):
        self.is_open = not self.is_open
        # just to know if we are in or out
        self.target = (90.0 * self.dir_apertura) if self.is_open else 0.0

    def update(self, dt):
        #animation
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
        
        #door
        glTranslatef(self.px, self.py, self.pz)
        glRotatef(self.angle, 0, 1, 0)
        glTranslatef(-self.px, -self.py, -self.pz)
        
        self._aplicar_material(self.mat, cfg)
        house_model.draw_material(self.mat)
        
        # door object
        glTranslatef(self.kx, self.ky, self.kz)
        glTranslatef(-self.kx, -self.ky, -self.kz)
        self._aplicar_material(self.mat_perilla, cfg)
        house_model.draw_material(self.mat_perilla)
        
        glPopMatrix()