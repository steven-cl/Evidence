import ctypes
import pywavefront
import glm
import pygame
import os
from OpenGL.GL import *

def load_texture(image_path):
    """
    Loads an image with Pygame and converts it into an OpenGL texture.
    """
    try:
        texture_surface = pygame.image.load(image_path)
        texture_data = pygame.image.tobytes(texture_surface, "RGBA", True)
        width = texture_surface.get_width()
        height = texture_surface.get_height()

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        return tex_id
    except Exception as e:
        print(f"Error loading texture {image_path}: {e}")
        return None

class Triangle:
    def __init__(self, v1, v2, v3, is_double_sided=True):
        self.a = glm.vec3(v1)
        self.b = glm.vec3(v2)
        self.c = glm.vec3(v3)
        self.is_double_sided = is_double_sided
        
        # SAFE CROSS PRODUCT: Prevent zero-length normalization (avoids NaN camera explosions)
        cross_prod = glm.cross(self.b - self.a, self.c - self.a)
        if glm.length(cross_prod) > 0.0001:
            self.normal = glm.normalize(cross_prod)
        else:
            self.normal = glm.vec3(0.0, 1.0, 0.0)
        
        # Precompute spatial bounding box limits
        margin = 1.0 
        self.min_x = min(self.a.x, self.b.x, self.c.x) - margin
        self.max_x = max(self.a.x, self.b.x, self.c.x) + margin
        self.min_y = min(self.a.y, self.b.y, self.c.y) - margin
        self.max_y = max(self.a.y, self.b.y, self.c.y) + margin
        self.min_z = min(self.a.z, self.b.z, self.c.z) - margin
        self.max_z = max(self.a.z, self.b.z, self.c.z) + margin

class Model3D:
    def __init__(self, file_route, scale=1.0, texture_filename=None, door_materials=None):
        """
        Initialize the 3D model, separating geometry by materials into structured dictionaries.
        """
        print(f"Loading model from: {file_route}...")
        self.scene = pywavefront.Wavefront(file_route, collect_faces=True)
        
        self.materiales = {}
        self.colliders = [] 
        self.door_source_triangles = {} 
        
        # Spatial Grid Partitioning Parameters
        self.grid_size = 3.0  
        self.spatial_grid = {} 
        
        if door_materials is None:
            door_materials = set()
        
        self.global_texture_id = None
        if texture_filename:
            tex_path = os.path.join("source", "textures", texture_filename)
            self.global_texture_id = load_texture(tex_path)
        
        for name, material in self.scene.materials.items():
            if not material.vertices:
                continue
                
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
            
            mesh_info = {
                'vertex_data': vertex_data,
                'num_vertices': num_vertices,
                'gl_format': gl_format
            }

            if name not in self.materiales:
                self.materiales[name] = []
            self.materiales[name].append(mesh_info)

            # --- AUTOMATED BOUNDING BOX GENERATION FOR LAMPS & FURNITURE ---
            # [UNIFIED] Added furniture tags: "mesa", "comedor", "sofa", "sillon", "cama", "silla", "cocina", "gabinete", "horno"
            FURNITURE_KEYWORDS = ["lamp", "mesa", "comedor", "sofa", "sillon", "cama", "silla", "cocina", "gabinete", "horno"]
            
            if any(kw in name.lower() for kw in FURNITURE_KEYWORDS):
                b_min_x, b_max_x = float('inf'), float('-inf')
                b_min_y, b_max_y = float('inf'), float('-inf')
                b_min_z, b_max_z = float('inf'), float('-inf')
                
                # Scan all vertices to find the absolute spatial boundaries of the object
                for idx in range(0, len(v), stride):
                    x = v[idx + stride - 3]
                    y = v[idx + stride - 2]
                    z = v[idx + stride - 1]
                    if x < b_min_x: b_min_x = x
                    if x > b_max_x: b_max_x = x
                    if y < b_min_y: b_min_y = y
                    if y > b_max_y: b_max_y = y
                    if z < b_min_z: b_min_z = z
                    if z > b_max_z: b_max_z = z
                
                # Apply safety padding margin ONLY for lamps to seal tight gaps with walls
                if "lamp" in name.lower():
                    padding = 0.12 
                    b_min_x -= padding; b_max_x += padding
                    b_min_z -= padding; b_max_z += padding
                
                # Map the 8 corners of the custom bounding box
                c000 = (b_min_x, b_min_y, b_min_z)
                c100 = (b_max_x, b_min_y, b_min_z)
                c010 = (b_min_x, b_max_y, b_min_z)
                c110 = (b_max_x, b_max_y, b_min_z)
                c001 = (b_min_x, b_min_y, b_max_z)
                c101 = (b_max_x, b_min_y, b_max_z)
                c011 = (b_min_x, b_max_y, b_max_z)
                c111 = (b_max_x, b_max_y, b_max_z)
                
                # Build the 6 solid faces (12 triangles total) pointing strictly OUTWARD around the asset
                box_triangles = [
                    Triangle(c001, c101, c011, is_double_sided=False), Triangle(c111, c011, c101, is_double_sided=False), # Front Face (+Z)
                    Triangle(c100, c000, c110, is_double_sided=False), Triangle(c010, c110, c000, is_double_sided=False), # Back Face (-Z)
                    Triangle(c000, c001, c010, is_double_sided=False), Triangle(c011, c010, c001, is_double_sided=False), # Left Face (-X)
                    Triangle(c101, c100, c111, is_double_sided=False), Triangle(c110, c111, c100, is_double_sided=False), # Right Face (+X)
                    Triangle(c010, c011, c110, is_double_sided=False), Triangle(c111, c110, c011, is_double_sided=False), # Top Face Roof (+Y)
                    Triangle(c000, c100, c001, is_double_sided=False), Triangle(c101, c001, c100, is_double_sided=False)  # Bottom Face Floor (-Y)
                ]
                
                for tri in box_triangles:
                    self.colliders.append(tri)
                    self._add_to_grid(tri)
                continue # Skip the complex high-poly evaluation completely

            # Identify tiny high-poly decorations that don't need any collision tracking at all
            is_ignored_prop = any(kw in name.lower() for kw in ["manivela", "botella", "reloj", "quemador", "perilla", "deco", "luz", "jarron"])
            if is_ignored_prop:
                continue 

            # Keywords that define architecture. Architecture must be 100% solid.
            STRUCTURAL_KEYWORDS = ["pared", "piso", "techo", "puerta", "marco"]
            is_structural = any(kw in name.lower() for kw in STRUCTURAL_KEYWORDS)

            # Generate mathematical polygon structures natively at 100% density for structural walls
            for i in range(0, len(v), stride * 3):
                v1 = (v[i + stride - 3], v[i + stride - 2], v[i + stride - 1])
                v2 = (v[i + stride * 2 - 3], v[i + stride * 2 - 2], v[i + stride * 2 - 1])
                v3 = (v[i + stride * 3 - 3], v[i + stride * 3 - 2], v[i + stride * 3 - 1])
                
                tri = Triangle(v1, v2, v3)
                
                if name in door_materials:
                    if name not in self.door_source_triangles:
                        self.door_source_triangles[name] = []
                    self.door_source_triangles[name].append(tri)
                else:
                    self.colliders.append(tri)
                    self._add_to_grid(tri)
            
        print(f"Model loaded! Active optimized physics triangles: {len(self.colliders)}")

    def _add_to_grid(self, tri):
        """Helper to inject a triangle into the pre-computed spatial partitioning hash map"""
        start_x = int(tri.min_x // self.grid_size)
        end_x = int(tri.max_x // self.grid_size)
        start_z = int(tri.min_z // self.grid_size)
        end_z = int(tri.max_z // self.grid_size)
        
        for gx in range(start_x, end_x + 1):
            for gz in range(start_z, end_z + 1):
                cell_key = (gx, gz)
                if cell_key not in self.spatial_grid:
                    self.spatial_grid[cell_key] = []
                self.spatial_grid[cell_key].append(tri)

    def draw(self):
        glEnableClientState(GL_VERTEX_ARRAY)
        if self.global_texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.global_texture_id)
            glColor3f(1.0, 1.0, 1.0)

        for nombre_material, lista_meshes in self.materiales.items():
            for mesh in lista_meshes:
                glInterleavedArrays(mesh['gl_format'], 0, mesh['vertex_data'])
                glDrawArrays(GL_TRIANGLES, 0, mesh['num_vertices'])
            
        glDisable(GL_TEXTURE_2D)
        glDisableClientState(GL_VERTEX_ARRAY)

    def draw_material(self, nombre_material):
        if nombre_material not in self.materiales:
            return
            
        glEnableClientState(GL_VERTEX_ARRAY)
        if self.global_texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.global_texture_id)
            glColor3f(1.0, 1.0, 1.0)

        for mesh in self.materiales[nombre_material]:
            glInterleavedArrays(mesh['gl_format'], 0, mesh['vertex_data'])
            glDrawArrays(GL_TRIANGLES, 0, mesh['num_vertices'])

        glDisableClientState(GL_VERTEX_ARRAY)

    def get_close_walls(self, px, pz, radius=2.0):
        close_walls = []
        start_x = int((px - radius) // self.grid_size)
        end_x = int((px + radius) // self.grid_size)
        start_z = int((pz - radius) // self.grid_size)
        end_z = int((pz + radius) // self.grid_size)
        
        for gx in range(start_x, end_x + 1):
            for gz in range(start_z, end_z + 1):
                cell_key = (gx, gz)
                if cell_key in self.spatial_grid:
                    close_walls.extend(self.spatial_grid[cell_key])
        return close_walls