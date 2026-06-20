from OpenGL.GL import *
from PIL import Image
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Texture:
    def __init__(self, filepath):
        # Unique ID for the texture
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        # Texture wrapping parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # These are filtering settings; may be reviewed later
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        try:
            # Load the image using Pillow
            image = Image.open(resource_path(filepath))
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.convert("RGBA").tobytes()
            
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        except Exception as e:
            print(f"Failed to load texture {filepath}: {e}")
        finally:
            glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)