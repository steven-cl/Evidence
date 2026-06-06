from OpenGL.GL import *
import pygame

class Skybox:
    def __init__(self, texture_paths):
        self.textures = {}
        self.load_textures(texture_paths)

    def load_texture_file(self, filename):
        """Loads an image with Pygame and transfers it to the GPU as a 2D texture"""
        surface = pygame.image.load(filename)
        # Flip the image vertically to align Pygame's coordinate system with OpenGL
        image_data = pygame.image.tostring(surface, "RGB", True)
        width, height = surface.get_width(), surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)

        # Configure filters to prevent visual seams at the edges of the cube
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        
        return tex_id

    def load_textures(self, paths):
        for face, path in paths.items():
            self.textures[face] = self.load_texture_file(path)

    def draw(self):
        """Draws the skybox cube using the standard universal OpenGL mapping"""
        glEnable(GL_TEXTURE_2D)
        size = 10.0

        # FRONT Face (-Z -> posz)
        glBindTexture(GL_TEXTURE_2D, self.textures['posz'])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-size, -size, -size)
        glTexCoord2f(1, 0); glVertex3f( size, -size, -size)
        glTexCoord2f(1, 1); glVertex3f( size,  size, -size)
        glTexCoord2f(0, 1); glVertex3f(-size,  size, -size)
        glEnd()

        # BACK Face (+Z -> negz)
        glBindTexture(GL_TEXTURE_2D, self.textures['negz'])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f( size, -size,  size)
        glTexCoord2f(1, 0); glVertex3f(-size, -size,  size)
        glTexCoord2f(1, 1); glVertex3f(-size,  size,  size)
        glTexCoord2f(0, 1); glVertex3f( size,  size,  size)
        glEnd()

        # LEFT Face (-X -> negx)
        glBindTexture(GL_TEXTURE_2D, self.textures['negx'])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-size, -size,  size)
        glTexCoord2f(1, 0); glVertex3f(-size, -size, -size)
        glTexCoord2f(1, 1); glVertex3f(-size,  size, -size)
        glTexCoord2f(0, 1); glVertex3f(-size,  size,  size)
        glEnd()

        # RIGHT Face (+X -> posx)
        glBindTexture(GL_TEXTURE_2D, self.textures['posx'])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f( size, -size, -size)
        glTexCoord2f(1, 0); glVertex3f( size, -size,  size)
        glTexCoord2f(1, 1); glVertex3f( size,  size,  size)
        glTexCoord2f(0, 1); glVertex3f( size,  size, -size)
        glEnd()

        # TOP Face (+Y -> posy) - Sky alignment over the pavilion
        glBindTexture(GL_TEXTURE_2D, self.textures['posy'])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 1); glVertex3f(-size,  size,  size)
        glTexCoord2f(1, 1); glVertex3f( size,  size,  size)
        glTexCoord2f(1, 0); glVertex3f( size,  size, -size)
        glTexCoord2f(0, 0); glVertex3f(-size,  size, -size)
        glEnd()

        # BOTTOM Face (-Y -> negy)
        glBindTexture(GL_TEXTURE_2D, self.textures['negy'])
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-size, -size,  size)
        glTexCoord2f(1, 0); glVertex3f( size, -size,  size)
        glTexCoord2f(1, 1); glVertex3f( size, -size, -size)
        glTexCoord2f(0, 1); glVertex3f(-size, -size, -size)
        glEnd()

        glDisable(GL_TEXTURE_2D)