from OpenGL.GL import *
from PIL import Image

class Texture:
    def __init__(self, filepath):
        # ID único para la textura
        self.id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.id)

        #el mero wrapping aqui
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        # En teorua esto es un tipo de suavisado, pero no noto diferencia(sujeto a revision)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        try:
            # Cargamos la imagen usando Pillow
            image = Image.open(filepath)
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            img_data = image.convert("RGBA").tobytes()
            
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
        except Exception as e:
            print(f"No se pudo cargar la textura twin {filepath}: {e}")
        finally:
            glBindTexture(GL_TEXTURE_2D, 0)

    def bind(self):
        glBindTexture(GL_TEXTURE_2D, self.id)

    def unbind(self):
        glBindTexture(GL_TEXTURE_2D, 0)