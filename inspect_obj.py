import math
from OpenGL.GL import *

class InspectableObject:
    def __init__(self, mat_name, px, py, pz, name="Object"):
        self.mat_name = mat_name
        self.px = px  # X position in Blender
        self.py = py  # Y position in Blender
        self.pz = pz  # Z position in Blender
        self.name = name
        
        # we can rotate the obj that we are inspecting
        self.rot_x = 0.0
        self.rot_y = 0.0

    def reset_rotation(self):
        #set the rotation to 0
        self.rot_x = 0.0
        self.rot_y = 0.0

    def can_be_inspected(self, player_x, player_z, cam_dir_x, cam_dir_z):
        #calculat the distance and FOV to the object
        dist = math.hypot(self.px - player_x, self.pz - player_z)
        if dist > 2.0 or dist == 0: 
            return False
            
        # Vector
        vec_x = (self.px - player_x) / dist
        vec_z = (self.pz - player_z) / dist
        
        cam_length = math.hypot(cam_dir_x, cam_dir_z)
        if cam_length == 0: 
            return False
            
        #verify el FOV
        dot_product = (vec_x * (cam_dir_x / cam_length)) + (vec_z * (cam_dir_z / cam_length))
        return dot_product > 0.85

    def _apply_material(self, cfg):
        if self.mat_name in cfg:
            val = cfg[self.mat_name]
            if hasattr(val, 'bind'):  
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
            glColor3f(0.7, 0.7, 0.7)

    def draw_world(self, house_model, cfg):
        #put back the object to the original position in the wordl
        glPushMatrix()
        self._apply_material(cfg)
        house_model.draw_material(self.mat_name)
        glPopMatrix()

    def draw_hud(self, house_model, cfg):
        #draw the object in the middle of our screen
        glPushMatrix()
        glTranslatef(0.0, 0.0, -1.2)
        
        # rotation with mouse
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        glTranslatef(-self.px, -self.py, -self.pz)
        
        self._apply_material(cfg)
        house_model.draw_material(self.mat_name)
        
        glPopMatrix()