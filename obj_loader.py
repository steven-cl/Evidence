import ctypes
import pywavefront
from OpenGL.GL import *

class Model3D:
    def __init__(self, file_route):
        """
        Initialize and process the 3D model into memory using direct OpenGL arrays.
        """
        print(f"Loading model from {file_route}...")
        
        # collect_faces=True extracts the pure geometry from the file
        self.scene = pywavefront.Wavefront(file_route, collect_faces=True)
        
        # We pre-process the mesh in RAM only once to avoid lagging the game
        self.meshes = []
        for name, material in self.scene.materials.items():
            
            # Convert the Python list to a C array (required by OpenGL)
            vertex_data = (ctypes.c_float * len(material.vertices))(*material.vertices)
            
            # Calculate the total number of vertices
            num_vertices = len(material.vertices) // material.vertex_size
            
            # Map the format exported by Blender to OpenGL constants
            gl_format = GL_V3F # Default format (only 3D positions)
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
            
        print("Model loaded and processed successfully!")

    def draw(self):
        """
        Send instructions to OpenGL to render the model using vertex arrays.
        """
        # Enable the use of vertex arrays in OpenGL
        glEnableClientState(GL_VERTEX_ARRAY)
        
        for mesh in self.meshes:
            # Tell OpenGL the format of the mesh and pass the data
            glInterleavedArrays(mesh['gl_format'], 0, mesh['vertex_data'])
            
            # Draw everything at once (much more efficient)
            glDrawArrays(GL_TRIANGLES, 0, mesh['num_vertices'])
            
        glDisableClientState(GL_VERTEX_ARRAY)