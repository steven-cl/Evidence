import math
from OpenGL.GL import *

class InspectableObject:
    # Changed 'mat_name' parameter to 'mat_names' to accept a list or string
    def __init__(self, mat_names, px, py, pz, name="Object"):
        # If it's a single string, convert to list. If it's already a list, keep it.
        self.mat_names = mat_names if isinstance(mat_names, list) else [mat_names]
        
        self.px = px  # Original position X (from Blender)
        self.py = py  # Original position Y
        self.pz = pz  # Original position Z
        self.name = name
        
        # Active rotation angles during inspection
        self.rot_x = 0.0
        self.rot_y = 0.0

    def reset_rotation(self):
        """Resets rotation to zero when the object is dropped"""
        self.rot_x = 0.0
        self.rot_y = 0.0

    def can_be_inspected(self, player_x, player_y, player_z, cam_dir_x, cam_dir_y, cam_dir_z):
        """Calculates distance and field of view towards the object in 3D"""
        dist_x = self.px - player_x
        dist_y = self.py - player_y
        dist_z = self.pz - player_z
        dist_3d = math.sqrt(dist_x**2 + dist_y**2 + dist_z**2)
        
        if dist_3d > 1.8 or dist_3d == 0: 
            return False
            
        # Normalized vector towards the object
        vec_x = dist_x / dist_3d
        vec_y = dist_y / dist_3d
        vec_z = dist_z / dist_3d
        
        cam_length = math.sqrt(cam_dir_x**2 + cam_dir_y**2 + cam_dir_z**2)
        if cam_length == 0: 
            return False
            
        # 3D Dot Product
        norm_cam_x = cam_dir_x / cam_length
        norm_cam_y = cam_dir_y / cam_length
        norm_cam_z = cam_dir_z / cam_length
        
        dot_product = (vec_x * norm_cam_x) + (vec_y * norm_cam_y) + (vec_z * norm_cam_z)
        
        return dot_product > 0.99

    # Now receives the specific material name as a parameter
    def _apply_material(self, visual_config, mat_name):
        if mat_name in visual_config:
            val = visual_config[mat_name]
            if hasattr(val, 'bind'):  # It's a valid texture
                glEnable(GL_TEXTURE_2D)
                glColor3f(1.0, 1.0, 1.0)
                val.bind()
            else:  # It's a solid RGB color
                glDisable(GL_TEXTURE_2D)
                glBindTexture(GL_TEXTURE_2D, 0)
                glColor3f(val[0], val[1], val[2])
        else:
            glDisable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
            glColor3f(0.7, 0.7, 0.7)

    def draw_world(self, house_model, visual_config, is_highlighted=False):
        """Draws the static object in its original position in the house"""
        glPushMatrix()
        
        # 1. GLOW / SOLID SILHOUETTE EFFECT
        if is_highlighted:
            glPushAttrib(GL_ENABLE_BIT | GL_POLYGON_BIT | GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            glDisable(GL_TEXTURE_2D)
            glDisable(GL_LIGHTING)
            glDisable(GL_DEPTH_TEST)
            glDepthMask(GL_FALSE)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE) 
            glColor3f(0.5, 0.5, 0.1) 
            
            glPushMatrix()
            glTranslatef(self.px, self.py, self.pz)
            glScalef(1.06, 1.06, 1.06) 
            glTranslatef(-self.px, -self.py, -self.pz)
            
            # Loop through all parts of the object to draw the glowing outline
            for mat in self.mat_names:
                house_model.draw_material(mat)
            
            glPopMatrix()
            glPopAttrib()

        # 2. NORMAL OBJECT DRAWING
        # Loop through all parts, apply their specific textures, and draw them
        for mat in self.mat_names:
            self._apply_material(visual_config, mat)
            house_model.draw_material(mat)
        
        glPopMatrix()

    def draw_hud(self, house_model, visual_config):
        """Isolates the object and draws it centered in front of the screen"""
        glPushMatrix()
        
        glTranslatef(0.0, 0.0, -1.2)
        glRotatef(self.rot_x, 1, 0, 0)
        glRotatef(self.rot_y, 0, 1, 0)
        glTranslatef(-self.px, -self.py, -self.pz)
        
        # Loop through all parts to draw them in the HUD
        for mat in self.mat_names:
            self._apply_material(visual_config, mat)
            house_model.draw_material(mat)
        
        glPopMatrix()