from OpenGL.GL import *
from OpenGL.GLU import *

class CameraFPS:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        # Detective position in the world (X, Y, Z)
        self.pos_x = 0.0
        self.pos_y = 1.5  # Altura aproximada de los ojos de una persona
        self.pos_z = 5.0
        
        # Head rotation (for looking around with the mouse later)
        self.pitch = 0.0  # Looking up/down (Rotación en X)
        self.yaw = 0.0    # Looking left/right (Rotación en Y)

    def configure_projection(self):
        """
        Configure the camera's "lens". Called once at the start.
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        # 45 degree FOV, aspect ratio, near and far planes
        gluPerspective(45, (self.width / self.height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def update_view(self):
        """
        Apply the camera transformations. Called every frame.
        """
        glLoadIdentity()
        
        # 1. First we rotate the camera (the detective's head)
        glRotatef(self.pitch, 1, 0, 0)
        glRotatef(self.yaw, 0, 1, 0)
        
        # 2. Then we move the world in the OPPOSITE direction of the player's position
        # In OpenGL, you don't actually move the camera, you move the world around it.
        glTranslatef(-self.pos_x, -self.pos_y, -self.pos_z)