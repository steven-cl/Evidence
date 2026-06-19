from OpenGL.GL import *
from obj_loader import Model3D
from pared import Texture
from door_In import Door
import glm


def create_visual_config():
    return {
        # Main texturing
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
        

        # Living room
        "matMesaTV": Texture('source/textures/texture_muebles.jpg'),
        "matLamp": Texture('source/textures/texture_blood.jpg'),
        "matLamp2": Texture('source/textures/texture_blood.jpg'),
        "matLamp3": Texture('source/textures/texture_blood.jpg'),
        "matLamp4": Texture('source/textures/texture_blood.jpg'),
        "matLamp5": Texture('source/textures/texture_blood.jpg'),
        "matTV":   (0.05, 0.05, 0.05),
        "matJarron": Texture('source/textures/texture_jar.jpg'),
        "matBotella":   (0.05, 0.05, 0.05),
        "matBotella2":   (0.05, 0.05, 0.05),
        "matBotella3":   (0.05, 0.05, 0.05),
        "matBotella4": Texture('source/textures/texture_glass.jpg'),
        "matMesaSala": Texture('source/textures/texture_muebles.jpg'),
        "matLuz": (0.05, 0.05, 0.05),
        "matLuz2": (0.05, 0.05, 0.05),
        "matLuz3": (0.05, 0.05, 0.05),
        "matLuz4": (0.05, 0.05, 0.05),
        "matLuz5": (0.05, 0.05, 0.05),
        "matLuz6": (0.05, 0.05, 0.05),
        "matLuz7": (0.05, 0.05, 0.05),
        "matLuz8": (0.05, 0.05, 0.05),
      
        # Decorations
        "matDeco": Texture('source/textures/texture_deco.jpg'),
        "matDeco2": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco3": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco4": Texture('source/textures/texture_Deco2.jpg'),
        "matDeco5": Texture('source/textures/texture_Deco2.jpg'),
        # Kitchen
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
        # Bedroom textures start here
        "matBaseC": Texture('source/textures/texture_wood.jpg'),
        "matBaseC2": Texture('source/textures/texture_wood.jpg'),
        "matBaseC3": Texture('source/textures/texture_wood.jpg'),
        "matBaseC4": Texture('source/textures/texture_wood.jpg'),
        "matColchonA": Texture('source/textures/texture_tela.jpg'),
        "matColchonB": Texture('source/textures/texture_tela.jpg'),
        "matColchonC": Texture('source/textures/texture_tela.jpg'),
        "matColchonD": Texture('source/textures/texture_tela.jpg'),
        "matAlmohada": Texture('source/textures/texture_telaB.jpg'),
        "matAlmohada2": Texture('source/textures/texture_telaB.jpg'),
        "matAlmohada3": Texture('source/textures/texture_telaB.jpg'),
        "matAlmohada4": Texture('source/textures/texture_telaB.jpg'),
        "matAlmohada5": Texture('source/textures/texture_telaB.jpg'),
        "matAlmohada6": Texture('source/textures/texture_telaB.jpg'),
        "matAlmohada7": Texture('source/textures/texture_telaB.jpg'),
        "matAlmohada8": Texture('source/textures/texture_telaB.jpg'),

        "matSofaA": Texture('source/textures/texture_telaC.jpg'),
        "matSillo": Texture('source/textures/texture_telaC.jpg'),
        "matCojin": Texture('source/textures/texture_telaB.jpg'),
        "matCojin2": Texture('source/textures/texture_telaB.jpg'),
        "matCojin3": Texture('source/textures/texture_telaB.jpg'),
        "matCojin4": Texture('source/textures/texture_telaB.jpg'),
        "matCojin5": Texture('source/textures/texture_telaB.jpg'),
        "matCojin6": Texture('source/textures/texture_telaB.jpg'),
        "matCojinSillon": Texture('source/textures/texture_telaB.jpg'),
        
        # Clocks
        "matReloj": Texture('source/textures/texture_shining.jpg'),
        "matRelojHoras": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora2": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora3": Texture('source/textures/texture_watch.jpg'),
        "matRelojHora4": Texture('source/textures/texture_watch.jpg'),
        
        
        "matTecho": Texture('source/textures/texture_techo.jpg'),
        "matPiso": Texture('source/textures/texture_floor.jpg'),

        #Basement
        "matStairs": Texture('source/textures/texture_basement.jpg'),
        "matPsotano": Texture('source/textures/texture_wall_basement.jpg'),
        "matPosaManos": Texture('source/textures/texture_metalB.jpg'),
        "matMarcoPuertaSot": (0.45, 0.24, 0.1),
        "matMesaSotano": Texture('source/textures/texture_wood.jpg'),
        "matRodapies": (0.22, 0.18, 0.14),
        "matMachete": Texture('source/textures/texture_machete.jpg'),
        "matMangoMachete": (0.05, 0.05, 0.05),
        "matCadaver": Texture('source/textures/texture_sa.jpg'),
        "matCadaverB": Texture('source/textures/texture_sa.jpg'),
        "matCadaverC": Texture('source/textures/texture_sa.jpg'),
        "matCadaverD": Texture('source/textures/texture_sa.jpg'),
        "matCuerpoP": (0.62, 0.52, 0.42),
        "matPie1": (0.62, 0.52, 0.42),
        "matPie2": (0.62, 0.52, 0.42),
        "matPie3": (0.62, 0.52, 0.42),
        "matPie4": (0.62, 0.52, 0.42),
        "matCuadro": (0.45, 0.24, 0.1),
        "matFoto": Texture('source/textures/texture_port.jpg'),
        "matCruz": Texture('source/textures/texture_wood.jpg'),

        #yard
        "matPatio": Texture('source/textures/texture_pasto.jpg'),
        "matGrama": (0.25, 0.45, 0.15),
        "matLimite": Texture('source/textures/texture_metalB.jpg'),
        "matPilar": Texture('source/textures/texture_wall_basement.jpg'),
        "matPilar2": Texture('source/textures/texture_wall_basement.jpg'),
        "matPilar3": Texture('source/textures/texture_wall_basement.jpg'),
        "matPilar4": Texture('source/textures/texture_wall_basement.jpg'),
        "matPilar5": Texture('source/textures/texture_wall_basement.jpg'),
        "matPilar6": Texture('source/textures/texture_wall_basement.jpg'),
        "matStairs2": (0.45, 0.45, 0.45),
        "matTechoExt": (0.45, 0.45, 0.45),
        "matBasePilar": (0.45, 0.45, 0.45),
        "matTubos": (0.45, 0.45, 0.45),
        "matCaja": Texture('source/textures/texture_wall_basement.jpg'),
        "matHueso": (0.45, 0.45, 0.45),
        "matOrganos": (0.35, 0.02, 0.02),
        "matDetalles": (0.35, 0.02, 0.02),

        "matNota": Texture('source/textures/texture_nota.jpg'),
        "matNotaB": Texture('source/textures/texture_nota.jpg'),
        "matNotaC": Texture('source/textures/texture_nota.jpg'),
        "matNotaD": Texture('source/textures/texture_nota.jpg'),
        "matNotaE": Texture('source/textures/texture_nota.jpg'),
        "matNotaF": Texture('source/textures/texture_nota.jpg'),
        "matNota2": Texture('source/textures/texture_notaB.jpg'),
        "matPcaja": (0.45, 0.45, 0.45),
        "matPanel": Texture('source/textures/texture_caja.jpg'),
        "matN": Texture('source/textures/texture_caja.jpg'),
        "matHelices": Texture('source/textures/texture_machete.jpg'),
        "matLlave": (0.05, 0.05, 0.05),
        "matPllave": Texture('source/textures/texture_machete.jpg'),
        "matManiCaja": Texture('source/textures/texture_machete.jpg'),
        "matVent": (0.05, 0.05, 0.05),
        
        

        "matSofa": Texture('source/textures/texture_telaB.jpg'),
        "matSillon": Texture('source/textures/texture_telaB.jpg'),

    }


def create_doors():
    doors = [
        Door("matPuerta", -2.9858, 1.379, 0.37832, "matPerilla", -3.7616, 1.0498, 0.45044),
        Door("matPuerta2", 0.96918, 1.379, -1.5806, "matP2", 0.95666, 1.05, -0.80633),
        Door("matPuerta3", 3.6967, 1.379, 1.5812, "matP3", 3.7112, 1.05, 0.81052),
        Door("matPuerta4", 3.6952, 1.379, -0.70732, "matP4", 3.7136, 1.05, -1.4746),
        Door("matPuerta5", 3.6953, 1.379, -3.466, "matP5", 3.7113, 1.05, -4.2389),
        Door("matPuerta7", 2.8285, 1.379, -5.9659, "matP7", 2.0526, 1.05, -5.9807),
        Door("matPuerta6", -2.9858, 1.379, -1.5134, "matP6", 3.7616, 1.379, -1.5282),
        Door("matManiCaja", -6.055, 1.2843, -1.0216, "matN", -6.0372, 1.284, -0.80611),
        
        Door("matGabinete3", -8.7252, 1.7951, 3.0372, "matManivela3", -8.7069, 1.4967, 2.3771, -1.0),
        Door("matGabinete6", -8.7252, 1.7951, 0.61547, "matManivela6", -8.7069, 1.4967, 1.2762),
        Door("matGabinete8", -7.7657, 0.26301, 1.079, "matManivela8", -7.3133, 0.091964, 1.0919, -1.0),
        Door("matGabinete7", -6.7669, 0.26301, 1.079, "matManivela7", -7.2203, 0.091964, 1.0919),
        Door("matGabinete", -8.7261, 2.026, 4.0371, "matManivela2", -8.7132, 1.9285, 3.5848, -1.0),
    ]
    
    for door in doors:
        is_safe_door = (door.mat == "matManiCaja")
        setattr(door, 'is_safe', is_safe_door)
        setattr(door, 'is_locked', is_safe_door)
        
        # Require key to open Door #6
        if door.mat == "matPuerta6":
            setattr(door, 'requires_key', True)
            setattr(door, 'is_locked', True)
            
    return doors

#Notas

#Nota 1: La casa estuvo abandonada mucho tiempo, como alguien podría vivir en condiciones tan precarias como estas, a menos que, la vida sea lo último que tenga un valor aquí.

#Nota 2: DollMaker suele ver su reloj 4 veces cuando esta torturando a sus víctimas, un hombre obsesionado con el tiempo nunca vive en paz.

#Nota 3: Podrías probar a ingresar los números en orden ascendente.

#Nota 4: El tiempo es un asesino silencioso, quizás esta vez te ayude capturar a uno.

#Nota 5: Me levanté temprano hoy, desayuné muy tranquilamente sabiendo que le di la eternidad y belleza de una muñeca a todas ellas.

#Nota 6: Al principio suelen ser ruidosas, pero una vez que se dan cuenta de que les hice un favor dejan de quejarse. Supongo que es parte de compartirme su felicidad.



def build_door_material_set(setting_doors):
    door_materials = set()
    for door in setting_doors:
        door_materials.add(door.mat)
        door_materials.add(door.mat_perilla)
    return door_materials

# List of the objects that we are inspectables
#Thi shit is so important

# NEW: Extract the material names of the objects for exclusion.
def build_inspectable_material_set(setting_inspectables):
    inspectable_materials = set()
    for obj in setting_inspectables:
        for mat in obj.mat_names:
            inspectable_materials.add(mat)
    return inspectable_materials

# List of interactive objects that can be inspected.
def create_inspectables():
    from inspect_obj import InspectableObject
    return [
        InspectableObject("matJarron", 0.67176, 0.38023, 3.9105),
        InspectableObject("matBotella4", 0.037556, 0.57008, 2.7768),
        InspectableObject("matNota", -0.16774, 0.47904, 2.8266),
        InspectableObject("matNotaB", -1.2706, 0.45003, -0.99463),
        InspectableObject("matNotaC", -5.9904, 0.10123, 0.12632),
        InspectableObject("matNotaD", -9.232, 0.69037, 1.4855),
        InspectableObject("matNotaE", -9.0343, 1.7336, 2.4406),
        InspectableObject("matNotaF", 7.3597, 0.47214, -0.55389),
        InspectableObject("matNota2", -7.022, 0.69689, 0.47165),
        InspectableObject(["matMachete", "matMangoMachete"], 1.6192, -2.6512, -4.3964, name=""),
        
        # Add the Safe Key as an interactive object located inside the safe coordinates
        InspectableObject(["matLlave", "matPllave"], -6.2983, 0.90647, -0.60902, name="Key")
    ]


def load_scene_assets():
    # 1. Load static configuration
    visual_config = create_visual_config()
    setting_doors = create_doors()
    door_materials = build_door_material_set(setting_doors)
    
    # 2. Load inspectable objects configuration
    setting_inspectables = create_inspectables()
    inspectable_materials = build_inspectable_material_set(setting_inspectables)
    
    # 3. Merge all dynamic materials to tell Model3D to separate them
    all_dynamic_materials = door_materials.copy()
    all_dynamic_materials.update(inspectable_materials)
    
    # 4. Load the house
    house = Model3D('source/models/RenewHouse.obj', scale=1.0, door_materials=all_dynamic_materials)
    
    # 5. RETURN THE EXACT 6 VALUES EXPECTED BY MAIN.PY
    return house, visual_config, setting_doors, door_materials, setting_inspectables, inspectable_materials


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


def draw_static_model(house, visual_config, door_materials, inspectable_materials=None):
    glPushMatrix()

    for material_name in house.materiales.keys():
        # 1. Ignore dynamic doors
        if material_name in door_materials:
            continue
            
        # 2. Ignore inspectable objects so they don't stick to tables
        if inspectable_materials and material_name in inspectable_materials:
            continue

        if material_name == "matTerrenoExt":
            continue

        apply_material(material_name, visual_config)
        house.draw_material(material_name)

    glPopMatrix()


def update_doors(setting_doors, dt):
    for door in setting_doors:
        door.update(dt)


def draw_doors(setting_doors, house, visual_config):
    for door in setting_doors:
        door.draw(house, visual_config)


def draw_inspectables_world(setting_inspectables, inspected_object, house, visual_config, looked_obj=None):
    for obj in setting_inspectables:
        if obj != inspected_object:
            # Calculate if we are looking the object
            is_highlighted = (obj == looked_obj)
            obj.draw_world(house, visual_config, is_highlighted)


def draw_inspected_hud(inspected_object, house, visual_config):
    if inspected_object:
        # we gotta clear the depth buufer so the obj doesn't go through the walls 
        glClear(GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        inspected_object.draw_hud(house, visual_config)


def ray_intersects_triangle(ray_origin, ray_vector, tri):
    EPSILON = 0.0000001
    edge1 = tri.b - tri.a
    edge2 = tri.c - tri.a
    h = glm.cross(ray_vector, edge2)
    a = glm.dot(edge1, h)
    
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
        return True, t 
    return False, 0.0


def get_looked_at_door(setting_doors, house, camera, max_distance=2.5):
    #use the ray to know what door we are looking at
    ray_origin = glm.vec3(camera.pos_x, camera.pos_y, camera.pos_z)
    ray_dir = glm.vec3(camera.front_x, camera.front_y, camera.front_z)
    
    closest_door = None
    min_dist = max_distance

    for door in setting_doors:
        triangles = door.get_transformed_triangles(house)
        door_hit_dist = float('inf')
        hit_door = False
        
        for tri in triangles:
            hit, t = ray_intersects_triangle(ray_origin, ray_dir, tri)
            if hit and t < door_hit_dist:
                door_hit_dist = t
                hit_door = True
                
        if hit_door and door_hit_dist < min_dist:
            min_dist = door_hit_dist
            closest_door = door

    return closest_door


# CLEAN UNIFICATION: Removed duplicated simple proximity function to preserve precise Raycast logic exclusively
def toggle_nearest_visible_door(setting_doors, house, camera, audio, safe_ui, max_distance=2.5):
    target_door = get_looked_at_door(setting_doors, house, camera, max_distance)
    if target_door:
        # Evaluate safe interaction
        if getattr(target_door, 'is_safe', False) and not getattr(target_door, 'is_open', False):
            if getattr(target_door, 'is_locked', True):
                safe_ui.active = True
                return
                
        # Evaluate key requirement
        if getattr(target_door, 'requires_key', False):
            if not getattr(camera, 'has_key', False):
                audio.play_sfx("safe_error") # Suena a bloqueado si no tienes la llave
                return 
            else:
                setattr(target_door, 'requires_key', False) 
                
        # Open or close the door
        target_door.toggle()
        
        # Play the corresponding sound effect
        if getattr(target_door, 'is_safe', False):
            if getattr(target_door, 'is_open', False):
                audio.play_sfx("safe_open")
            else:
                audio.play_sfx("safe_close")
        else:
            if getattr(target_door, 'is_open', False):
                audio.play_sfx("door_open")
            else:
                audio.play_sfx("door_close")
        
        # Auto-lock the safe when closed again
        if getattr(target_door, 'is_safe', False) and not getattr(target_door, 'is_open', False):
            target_door.is_locked = True