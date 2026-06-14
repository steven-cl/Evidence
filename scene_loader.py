from OpenGL.GL import *

from obj_loader import Model3D
from pared import Texture
from door_In import Door
import glm


def create_visual_config():
    return {
        "matParedPrincipal": Texture('source/textures/texture_wall.jpg'),
        "matPared": Texture('source/textures/texture_wall.jpg'),
        "matPared2": Texture('source/textures/texture_wall.jpg'),
        "matPared3": Texture('source/textures/texture_wall.jpg'),
        "matPared4": Texture('source/textures/texture_wall.jpg'),
        "matPared5": Texture('source/textures/texture_wall.jpg'),
        "matPared6": Texture('source/textures/texture_wall.jpg'),
        "matMarcoPuerta": (0.45, 0.24, 0.1),
        "matPuerta": Texture('source/textures/texture_wood.jpg'),
        "matPerilla": (0.05, 0.05, 0.05),
        "matMarcoPuerta2": (0.45, 0.24, 0.1),
        "matPuerta2": Texture('source/textures/texture_wood.jpg'),
        "matP2": (0.05, 0.05, 0.05),
        "matMarcoPuerta3": (0.45, 0.24, 0.1),
        "matPuerta3": Texture('source/textures/texture_wood.jpg'),
        "matP3": (0.05, 0.05, 0.05),
        "matMarcoPuerta4": (0.45, 0.24, 0.1),
        "matPuerta4": Texture('source/textures/texture_wood.jpg'),
        "matP4": (0.05, 0.05, 0.05),
        "matMarcoPuerta5": (0.45, 0.24, 0.1),
        "matPuerta5": Texture('source/textures/texture_wood.jpg'),
        "matP5": (0.05, 0.05, 0.05),
        "matMarcoPuerta6": (0.45, 0.24, 0.1),
        "matPuerta6": Texture('source/textures/texture_wood.jpg'),
        "matP6": (0.05, 0.05, 0.05),
        "matMarcoPuerta7": (0.45, 0.24, 0.1),
        "matPuerta7": Texture('source/textures/texture_wood.jpg'),
        "matP7": (0.05, 0.05, 0.05),
        "matSofa": Texture('source/textures/texture_tela.jpg'),
        "matSillon": Texture('source/textures/texture_tela.jpg'),
        "matMesaTV": Texture('source/textures/texture_muebles.jpg'),
        "matLamp": Texture('source/textures/texture_blood.jpg'),
        "matLamp2": Texture('source/textures/texture_blood.jpg'),
        "matLamp3": Texture('source/textures/texture_blood.jpg'),
        "matLamp4": Texture('source/textures/texture_blood.jpg'),
        "matLamp5": Texture('source/textures/texture_blood.jpg'),
        "matTV": (0.05, 0.05, 0.05),
        "matJarron": (0.55, 0.27, 0.08),
        "matBotella": (0.05, 0.05, 0.05),
        "matBotella2": (0.05, 0.05, 0.05),
        "matBotella3": (0.05, 0.05, 0.05),
        "matBotella4": (0.05, 0.05, 0.05),
        "matMesaSala": Texture('source/textures/texture_muebles.jpg'),
        "matLuz": (0.05, 0.05, 0.05),
        "matLuz2": (0.05, 0.05, 0.05),
        "matLuz3": (0.05, 0.05, 0.05),
        "matLuz4": (0.05, 0.05, 0.05),
        "matLuz5": (0.05, 0.05, 0.05),
        "matLuz6": (0.05, 0.05, 0.05),
        "matLuz7": (0.05, 0.05, 0.05),
        "matLuz8": (0.05, 0.05, 0.05),
        "matDeco": Texture('source/textures/texture_deco.jpg'),
        "matDeco2": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco3": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco4": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco5": Texture('source/textures/texture_Deco2.jpg'),
        "matCocina": Texture('source/textures/texture_base_kitchen.jpg'),
        "matGabinete": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete2": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete3": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete4": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete5": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete6": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete7": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete8": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete9": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete10": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete11": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete12": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete13": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete14": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete15": Texture('source/textures/texture_kitchen.jpg'),
        "matGabinete16": Texture('source/textures/texture_kitchen.jpg'),
        "matManivela": Texture('source/textures/texture_metal.jpg'),
        "matManivela2": Texture('source/textures/texture_metal.jpg'),
        "matManivela3": Texture('source/textures/texture_metal.jpg'),
        "matManivela4": Texture('source/textures/texture_metal.jpg'),
        "matManivela5": Texture('source/textures/texture_metal.jpg'),
        "matManivela6": Texture('source/textures/texture_metal.jpg'),
        "matManivela7": Texture('source/textures/texture_metal.jpg'),
        "matManivela8": Texture('source/textures/texture_metal.jpg'),
        "matManivela9": Texture('source/textures/texture_metal.jpg'),
        "matManivela10": Texture('source/textures/texture_metal.jpg'),
        "matManivela11": Texture('source/textures/texture_metal.jpg'),
        "matManivela12": Texture('source/textures/texture_metal.jpg'),
        "matManivela13": Texture('source/textures/texture_metal.jpg'),
        "matManivela14": Texture('source/textures/texture_metal.jpg'),
        "matManivela15": Texture('source/textures/texture_metal.jpg'),
        "matManivela16": Texture('source/textures/texture_metal.jpg'),
        "matPerillaCocina": Texture('source/textures/texture_metal.jpg'),
        "matPerillaCocina2": Texture('source/textures/texture_metal.jpg'),
        "matQuemadores": Texture('source/textures/texture_metal.jpg'),
        "matComedor": Texture('source/textures/texture_wood.jpg'),
        "matSilla": Texture('source/textures/texture_wood.jpg'),
        "matSilla2": Texture('source/textures/texture_wood.jpg'),
        "matSilla3": Texture('source/textures/texture_wood.jpg'),
        "matSilla4": Texture('source/textures/texture_wood.jpg'),
        "matHorno": Texture('source/textures/texture_horno.jpg'),
        "matBaseCama": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama2": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama3": Texture('source/textures/texture_wood.jpg'),
        "matBaseCama4": Texture('source/textures/texture_wood.jpg'),
        "matColchon": Texture('source/textures/texture_tela.jpg'),
        "matColchon2": Texture('source/textures/texture_tela.jpg'),
        "matColchon3": Texture('source/textures/texture_tela.jpg'),
        "matColchon4": Texture('source/textures/texture_tela.jpg'),
        "matReloj": Texture('source/textures/texture_shining.jpg'),
        "matRelojHoras": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora2": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora3": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora4": Texture('source/textures/texture_watch.jpg'),
        "matTecho": Texture('source/textures/texture_techo.jpg'),
        "matPiso": Texture('source/textures/texture_floor.jpg'),
    }


def create_doors():
    return [
        Door("matPuerta", -2.9858, 1.379, 0.37832, "matPerilla", -3.7616, 1.0498, 0.45044),
        Door("matPuerta2", 0.96918, 1.379, -1.5806, "matP2", 0.95666, 1.05, -0.80633),
        Door("matPuerta3", 3.6967, 1.379, 1.5812, "matP3", 3.7112, 1.05, 0.81052),
        Door("matPuerta4", 3.6952, 1.379, -0.70732, "matP4", 3.7136, 1.05, -1.4746),
        Door("matPuerta5", 3.6953, 1.379, -3.466, "matP5", 3.7113, 1.05, -4.2389),
        Door("matPuerta7", 2.8285, 1.379, -5.9659, "matP7", 2.0526, 1.05, -5.9807),
    ]


def build_door_material_set(setting_doors):
    door_materials = set()
    for door in setting_doors:
        door_materials.add(door.mat)
        door_materials.add(door.mat_perilla)
    return door_materials


def load_scene_assets():
    # 1. Generate configs and doors FIRST
    config_visual = create_visual_config()
    setting_doors = create_doors()
    door_materials = build_door_material_set(setting_doors)
    
    # 2. Pass door_materials to Model3D so it knows what to separate
    house = Model3D('source/models/RenewHouse.obj', scale=1.0, door_materials=door_materials)
    
    return house, config_visual, setting_doors, door_materials


def apply_material(material_name, config_visual):
    if material_name in config_visual:
        assigned = config_visual[material_name]
        if isinstance(assigned, Texture):
            glEnable(GL_TEXTURE_2D)
            glColor3f(1.0, 1.0, 1.0)
            assigned.bind()
        else:
            glDisable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)
            glColor3f(assigned[0], assigned[1], assigned[2])
    else:
        glDisable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        glColor3f(0.6, 0.6, 0.6)


def draw_static_model(house, config_visual, door_materials):
    glPushMatrix()

    for material_name in house.materiales.keys():
        if material_name in door_materials:
            continue

        if material_name == "matTerrenoExt":
            continue

        apply_material(material_name, config_visual)
        house.draw_material(material_name)

    glPopMatrix()


def update_doors(setting_doors, dt):
    for door in setting_doors:
        door.update(dt)


def draw_doors(setting_doors, house, config_visual):
    for door in setting_doors:
        door.draw(house, config_visual)


def ray_intersects_triangle(ray_origin, ray_vector, tri):
    """
    Algoritmo de intersección Möller-Trumbore.
    Dispara un láser y devuelve si golpeó el triángulo y a qué distancia.
    """
    EPSILON = 0.0000001
    edge1 = tri.b - tri.a
    edge2 = tri.c - tri.a
    h = glm.cross(ray_vector, edge2)
    a = glm.dot(edge1, h)
    
    # Si el rayo es paralelo al triángulo, no hay intersección
    if -EPSILON < a < EPSILON:
        return False, 0.0 
        
    f = 1.0 / a
    s = ray_origin - tri.a
    u = f * glm.dot(s, h)
    
    if u < 0.0 or u > 1.0:
        return False, 0.0
        
    q = glm.cross(s, edge1)
    v = f * glm.dot(ray_vector, q)
    
    if v < 0.0 or u + v > 1.0:
        return False, 0.0
        
    t = f * glm.dot(edge2, q)
    if t > EPSILON:
        return True, t # ¡Impacto confirmado!
    return False, 0.0

# [MODIFICADO] Añadimos 'house' como parámetro para acceder a la geometría real
def toggle_nearest_visible_door(setting_doors, house, camera, max_distance=2.5):
    """
    Lanza un rayo desde el centro del Crosshair para detectar la puerta exacta.
    """
    # Origen: Posición de los ojos de la cámara
    ray_origin = glm.vec3(camera.pos_x, camera.pos_y, camera.pos_z)
    # Dirección: Hacia dónde mira exactamente el Crosshair
    ray_dir = glm.vec3(camera.front_x, camera.front_y, camera.front_z)
    
    closest_door = None
    min_dist = max_distance

    for door in setting_doors:
        # Obtenemos los triángulos en la posición EXACTA en la que está la puerta AHORA
        triangles = door.get_transformed_triangles(house)
        door_hit_dist = float('inf')
        hit_door = False
        
        # Disparamos el láser contra cada polígono de la puerta
        for tri in triangles:
            hit, t = ray_intersects_triangle(ray_origin, ray_dir, tri)
            if hit and t < door_hit_dist:
                door_hit_dist = t
                hit_door = True
                
        # Si le dimos a la puerta, y está más cerca que el límite de 2.5 metros
        if hit_door and door_hit_dist < min_dist:
            min_dist = door_hit_dist
            closest_door = door

    if closest_door:
        closest_door.toggle()
