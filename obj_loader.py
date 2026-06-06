import ctypes
import pywavefront
from OpenGL.GL import *

class Model3D:
    def __init__(self, file_route):
       
        # Initialize the 3D model, separating geometry by materials
   
        print(f"Loading model from: {file_route}...")
        
        self.scene = pywavefront.Wavefront(file_route, collect_faces=True)
        
        # Here we store material information
        self.materiales = {}
        
        for mat_name, material in self.scene.materials.items():
            if not material.vertices:
                continue
                
            slots = len(material.vertices)
            vertex_data = (ctypes.c_float * slots)()
            vertex_data[:] = material.vertices
            
            num_vertices = slots // material.vertex_size
            
            # Used to identify the vertex format exported from Blender
            gl_format = GL_V3F 
            if material.vertex_format == 'N3F_V3F':
                gl_format = GL_N3F_V3F
            elif material.vertex_format == 'T2F_V3F':
                gl_format = GL_T2F_V3F
            elif material.vertex_format == 'T2F_N3F_V3F':
                gl_format = GL_T2F_N3F_V3F
            
            mesh_info = {
                'vertex_data': vertex_data,
                'num_vertices': num_vertices,
                'gl_format': gl_format
            }
            
            if mat_name not in self.materiales:
                self.materiales[mat_name] = []
            self.materiales[mat_name].append(mesh_info)
            
       
        print("Materials ready for main.py:")
        for name in self.materiales.keys():
            print(f" -> '{name}'")


    def draw_material(self, nombre_material):
   
        if nombre_material not in self.materiales:
            return
            
        glEnableClientState(GL_VERTEX_ARRAY)
        for mesh in self.materiales[nombre_material]:
            glInterleavedArrays(mesh['gl_format'], 0, mesh['vertex_data'])
            glDrawArrays(GL_TRIANGLES, 0, mesh['num_vertices'])
        glDisableClientState(GL_VERTEX_ARRAY)