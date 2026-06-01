import ctypes
import pywavefront
import glm
import pygame
import os
from OpenGL.GL import *

def load_texture(image_path):
    """
    Carga una imagen con Pygame y la convierte en una textura de OpenGL.
    """
    try:
        # Cargar la imagen
        texture_surface = pygame.image.load(image_path)
        
        # Extraer los datos de píxeles. 
        # El 'True' al final invierte la imagen verticalmente, ya que OpenGL y Pygame 
        # leen el eje Y de las imágenes al revés.
        texture_data = pygame.image.tobytes(texture_surface, "RGBA", True)
        width = texture_surface.get_width()
        height = texture_surface.get_height()

        # Generar un ID de textura en OpenGL
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        # Configurar cómo se escala la textura (Filtro Lineal para que no se vea pixelada)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        # Enviar la imagen a la tarjeta gráfica
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        
        return tex_id
    except Exception as e:
        print(f"Error cargando la textura {image_path}: {e}")
        return None

class Triangle:
    def __init__(self, v1, v2, v3):
        self.a = glm.vec3(v1)
        self.b = glm.vec3(v2)
        self.c = glm.vec3(v3)
        self.normal = glm.normalize(glm.cross(self.b - self.a, self.c - self.a))
        
        # Pre-calculamos los límites espaciales del triángulo con un margen
        margen = 1.0 # Margen de seguridad
        self.min_x = min(self.a.x, self.b.x, self.c.x) - margen
        self.max_x = max(self.a.x, self.b.x, self.c.x) + margen
        self.min_y = min(self.a.y, self.b.y, self.c.y) - margen
        self.max_y = max(self.a.y, self.b.y, self.c.y) + margen
        self.min_z = min(self.a.z, self.b.z, self.c.z) - margen
        self.max_z = max(self.a.z, self.b.z, self.c.z) + margen

class Model3D:
    # NUEVO: Añadimos 'texture_filename' con valor por defecto None
    def __init__(self, file_route, scale=1.0, texture_filename=None):
        print(f"Loading model from {file_route}...")
        self.scene = pywavefront.Wavefront(file_route, collect_faces=True)
        
        self.meshes = []
        self.colliders = [] 
        
        # Cargamos la textura global para este modelo una sola vez
        self.global_texture_id = None
        if texture_filename:
            # Forzamos a que busque en la carpeta 'source/textures'
            tex_path = os.path.join("source", "textures", texture_filename)
            self.global_texture_id = load_texture(tex_path)
            if self.global_texture_id:
                print(f"Textura {texture_filename} aplicada exitosamente al modelo.")
        
        for name, material in self.scene.materials.items():
            v = material.vertices
            stride = material.vertex_size

            if scale != 1.0:
                for i in range(0, len(v), stride):
                    v[i + stride - 3] *= scale  
                    v[i + stride - 2] *= scale  
                    v[i + stride - 1] *= scale  

            vertex_data = (ctypes.c_float * len(v))(*v)
            num_vertices = len(v) // stride
            
            gl_format = GL_V3F
            if material.vertex_format == 'N3F_V3F':
                gl_format = GL_N3F_V3F
            elif material.vertex_format == 'T2F_V3F':
                gl_format = GL_T2F_V3F
            elif material.vertex_format == 'T2F_N3F_V3F':
                gl_format = GL_T2F_N3F_V3F
            
            self.meshes.append({
                'vertex_data': vertex_data,
                'num_vertices': num_vertices,
                'gl_format': gl_format
            })

            # Generar colisiones
            for i in range(0, len(v), stride * 3):
                v1 = (v[i + stride - 3], v[i + stride - 2], v[i + stride - 1])
                v2 = (v[i + stride * 2 - 3], v[i + stride * 2 - 2], v[i + stride * 2 - 1])
                v3 = (v[i + stride * 3 - 3], v[i + stride * 3 - 2], v[i + stride * 3 - 1])
                self.colliders.append(Triangle(v1, v2, v3))
            
        print(f"Model loaded! Polígonos de colisión generados: {len(self.colliders)}")

    def draw(self):
        # Habilitar el uso de arreglos y de texturas 2D
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnable(GL_TEXTURE_2D)
        
        # Para que el color blanco por defecto no tiña nuestra textura
        glColor3f(1.0, 1.0, 1.0) 
        
        # Vinculamos la textura manual (si existe) ANTES de dibujar todo
        if self.global_texture_id is not None:
            glBindTexture(GL_TEXTURE_2D, self.global_texture_id)
        else:
            glBindTexture(GL_TEXTURE_2D, 0)

        for mesh in self.meshes:
            glInterleavedArrays(mesh['gl_format'], 0, mesh['vertex_data'])
            glDrawArrays(GL_TRIANGLES, 0, mesh['num_vertices'])
            
        # Apagamos estados al terminar de dibujar
        glDisable(GL_TEXTURE_2D)
        glDisableClientState(GL_VERTEX_ARRAY)