import bpy
import random
import os


script_dir = os.path.dirname(bpy.context.space_data.text.filepath)
pbr_material = {
    'albedo': os.path.join(script_dir, "assets", "ground", "leafy-grass2-albedo.png"),
    'roughness': os.path.join(script_dir, "assets", "ground", "leafy-grass2-roughness.png"),
    'metallic': os.path.join(script_dir, "assets", "ground", "leafy-grass2-metallic.png"),
    'normal': os.path.join(script_dir, "assets", "ground", "leafy-grass2-normal-ogl.png"),
    'height': os.path.join(script_dir, "assets", "ground", "leafy-grass2-height.png"),
    'ao': os.path.join(script_dir, "assets", "ground", "leafy-grass2-ao.png")
}
plant_models = [
    os.path.join(script_dir, "assets", "vitis_vinifera", "Vitis_vinifera_001_FBX_2012_SM.FBX"),
    os.path.join(script_dir, "assets", "vitis_vinifera", "Vitis_vinifera_002_FBX_2012_SM.FBX"),
    os.path.join(script_dir, "assets", "vitis_vinifera", "Vitis_vinifera_003_FBX_2012_SM.FBX")
]
post_model = os.path.join(script_dir, "assets", "vitis_vinifera", "Vitis_vinifera_Column_2_FBX_SM.FBX")


def create_ground_plane(size=15, subdivisions=100, noise_scale=0.9, intensity=0.2, displacement_strength=0.25, displacement_mid_level=0.0):
    """
    Create a ground plane with displacement and cloud textures.

    Parameters:
    size (int): Size of the ground plane
    subdivisions (int): Number of subdivisions for the object
    noise_scale (float): Scale of the noise texture
    intensity (float): Intensity of the texture
    displacement_strength (float): Strength of the displacement modifier
    displacement_mid_level (float): Mid-level of the displacement modifier
    """
    bpy.ops.mesh.primitive_plane_add(size=size)
    ground_plane = bpy.context.object
    ground_plane.name = "Ground Plane"

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.subdivide(number_cuts=subdivisions)
    bpy.ops.object.mode_set(mode='OBJECT')

    displacement_modifier = ground_plane.modifiers.new(name="Displacement", type='DISPLACE')
    texture = bpy.data.textures.new("CloudsTexture", type='CLOUDS')
    texture.noise_scale = noise_scale
    texture.intensity = intensity
    displacement_modifier.texture = texture
    displacement_modifier.strength = displacement_strength
    displacement_modifier.mid_level = displacement_mid_level
    

def create_texture_node(nodes, image_path, label, location):
    """
    Create a texture node in the material node tree.

    Parameters:
    nodes (bpy.types.Nodes): Node tree to which the texture node is added
    image_path (str): Path to the image file for the texture
    label (str): Label for the texture node
    location (tuple): Location of the node in the node editor

    Returns:
    bpy.types.ShaderNodeTexImage: The created texture node
    """
    texture_node = nodes.new(type='ShaderNodeTexImage')
    texture_node.location = location
    texture_node.label = label
    texture_node.image = bpy.data.images.load(filepath=image_path)
    
    return texture_node


def setup_pbr_material(pbr_files, obj_name="Ground Plane", uv_scale=(15.0, 15.0)):
    """
    Setup a PBR material for a given object.

    Parameters:
    texture_files (dict): Dictionary of texture file paths
    obj_name (str): Name of the object to apply the material to
    uv_scale (tuple): UV scale for the mapping node
    """
    obj = bpy.data.objects.get(obj_name)
    material = bpy.data.materials.new(name="PBR_Material")
    obj.data.materials.append(material)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links

    nodes.clear()

    principled_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    principled_bsdf.location = (0, 0)
    material_output = nodes.new(type='ShaderNodeOutputMaterial')
    material_output.location = (400, 0)
    links.new(principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])
    
    texture_coord = nodes.new(type='ShaderNodeTexCoord')
    texture_coord.location = (-600, 200)
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-400, 200)
    mapping.inputs['Scale'].default_value = (*uv_scale, 1.0)
    links.new(texture_coord.outputs['UV'], mapping.inputs['Vector'])

    if 'albedo' in pbr_files:
        albedo_node = create_texture_node(nodes, pbr_files['albedo'], "Albedo (Base Color)", (-200, 200))
        links.new(mapping.outputs['Vector'], albedo_node.inputs['Vector'])
        links.new(albedo_node.outputs['Color'], principled_bsdf.inputs['Base Color'])

    if 'roughness' in pbr_files:
        roughness_node = create_texture_node(nodes, pbr_files['roughness'], "Roughness", (-200, 0))
        links.new(mapping.outputs['Vector'], roughness_node.inputs['Vector'])
        links.new(roughness_node.outputs['Color'], principled_bsdf.inputs['Roughness'])

    if 'metallic' in pbr_files:
        metallic_node = create_texture_node(nodes, pbr_files['metallic'], "Metallic", (-200, -200))
        links.new(mapping.outputs['Vector'], metallic_node.inputs['Vector'])
        links.new(metallic_node.outputs['Color'], principled_bsdf.inputs['Metallic'])

    if 'normal' in pbr_files:
        normal_map_node = nodes.new(type='ShaderNodeNormalMap')
        normal_map_node.location = (0, -400)

        normal_texture_node = create_texture_node(nodes, pbr_files['normal'], "Normal Map", (-200, -400))
        links.new(mapping.outputs['Vector'], normal_texture_node.inputs['Vector'])
        links.new(normal_texture_node.outputs['Color'], normal_map_node.inputs['Color'])
        links.new(normal_map_node.outputs['Normal'], principled_bsdf.inputs['Normal'])

    if 'height' in pbr_files:
        displacement_node = nodes.new(type='ShaderNodeDisplacement')
        displacement_node.location = (0, -600)

        height_texture_node = create_texture_node(nodes, pbr_files['height'], "Height Map", (-200, -600))
        links.new(mapping.outputs['Vector'], height_texture_node.inputs['Vector'])
        links.new(height_texture_node.outputs['Color'], displacement_node.inputs['Height'])
        links.new(displacement_node.outputs['Displacement'], material_output.inputs['Displacement'])

    if 'ao' in pbr_files:
        ao_node = create_texture_node(nodes, pbr_files['ao'], "Ambient Occlusion", (-200, 400))
        mix_node = nodes.new(type='ShaderNodeMixRGB')
        mix_node.inputs['Fac'].default_value = 1.0
        mix_node.location = (0, 200)

        links.new(mapping.outputs['Vector'], ao_node.inputs['Vector'])
        links.new(ao_node.outputs['Color'], mix_node.inputs[1])
        if 'albedo' in pbr_files:
            links.new(albedo_node.outputs['Color'], mix_node.inputs[2])
        links.new(mix_node.outputs['Color'], principled_bsdf.inputs['Base Color'])


def add_grass_particles(obj_name="Ground Plane", particle_count=300000, hair_length=0.04, brownian_factor=0.04, damping=0.01):
    """
    Adds a particle system to simulate grass on a specified object.

    Parameters:
        obj_name (str): Name of the object to add the particle system to.
        particle_count (int): Number of particles (grass strands) to generate.
        hair_length (float): Length of the hair particles.
        brownian_factor (float): Brownian motion factor for randomness in particle positioning.
        damping (float): Damping factor for particle movement.
    """
    # Retrieve the plane object and set it as active
    object = bpy.data.objects.get(obj_name)
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.particle_system_add()
    particle_system = object.particle_systems[0]
    
    particle_settings = particle_system.settings
    particle_settings.type = 'HAIR'
    particle_settings.count = particle_count
    particle_settings.hair_length = hair_length
    particle_settings.use_advanced_hair = True
    particle_settings.brownian_factor = brownian_factor
    particle_settings.damping = damping
    
    
def create_vineyard_trellis(plant_files, post_file, grid_rows=5, grid_columns=7, x_spacing=1.6, y_spacing=2.0, post_offset=0.8):
    """
    Create a vineyard trellis system with plant and post models.

    Parameters:
    plant_files (list): List of file paths for plant models
    post_file (str): File path for the post model
    grid_rows (int): Number of rows in the vineyard grid
    grid_columns (int): Number of columns in the vineyard grid
    x_spacing (float): Spacing between plants along the X axis
    y_spacing (float): Spacing between plants along the Y axis
    post_offset (float): Offset for the posts relative to the plants
    """
    x_offset = -((grid_columns - 1) * x_spacing) / 2
    y_offset = -((grid_rows - 1) * y_spacing) / 2
    
    collection_name = "Vineyard"
    plant_collection = bpy.data.collections.new(f"{collection_name} Plants")
    bpy.context.scene.collection.children.link(plant_collection)
    post_collection = bpy.data.collections.new(f"{collection_name} Posts")
    bpy.context.scene.collection.children.link(post_collection)
    
    plant_models = []
    for plant_file in plant_files:
        bpy.ops.import_scene.fbx(filepath=plant_file)
        plant_models.append(bpy.context.selected_objects[0])
    bpy.ops.import_scene.fbx(filepath=post_file)
    post_model = bpy.context.selected_objects[0]
    
    for row in range(grid_rows):
        for col in range(grid_columns):
            x = x_offset + col * x_spacing
            y = y_offset + row * y_spacing
            z = 0
            
            random_plant_model = random.choice(plant_models)
            plant_instance = random_plant_model.copy()
            plant_instance.location = (x, y, z)
            plant_collection.objects.link(plant_instance)
        
        start_post = post_model.copy()
        start_post.location = (x_offset - post_offset, y_offset + row * y_spacing, 0)
        start_post.scale.x *= -1 
        post_collection.objects.link(start_post)
        end_post = post_model.copy()
        end_post.location = (x_offset + (grid_columns - 1) * x_spacing + post_offset, y_offset + row * y_spacing, 0)
        post_collection.objects.link(end_post)
 
    for plant_model in plant_models:
        bpy.context.scene.collection.objects.unlink(plant_model)
    bpy.context.scene.collection.objects.unlink(post_model)
    

def set_material_properties(material_names, metallic, roughness, normal_map_strength=None):
    """
    Set certain properties for a list of materials.

    Parameters:
    material_names (list): List of material names
    metallic (float): Metallic value to set
    roughness (float): Roughness value to set
    normal_map_strength (float, optional): Strength for normal maps
    """
    for mat_name in material_names:
        mat = bpy.data.materials.get(mat_name)
        nodes = mat.node_tree.nodes

        principled = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
        principled.inputs["Metallic"].default_value = metallic
        principled.inputs["Roughness"].default_value = roughness

        if normal_map_strength is not None:
            normal_map = next(node for node in nodes if node.type == 'NORMAL_MAP')
            normal_map.inputs["Strength"].default_value = normal_map_strength


def configure_materials():
    """Configure the materials of various components for more realism."""
    leaf_materials = [mat.name for mat in bpy.data.materials if mat.name.startswith("Leaf")]
    set_material_properties(leaf_materials, metallic=0.4, roughness=0.8, normal_map_strength=0.1)
    
    twig_materials = [mat.name for mat in bpy.data.materials if mat.name.startswith("Twig")]
    set_material_properties(twig_materials, metallic=0.2, roughness=1)

    grape_materials = [mat.name for mat in bpy.data.materials if mat.name.startswith("Grape")]
    set_material_properties(grape_materials, metallic=0.2, roughness=0)

    branch_trunk_materials = [mat.name for mat in bpy.data.materials if mat.name.startswith("Branch") or mat.name.startswith("Trunk")]
    set_material_properties(branch_trunk_materials, metallic=0.5, roughness=0.5)
    
    # change all metal posts to wooden posts
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for slot in obj.material_slots:
                if slot.material.name == "Metal_Color":
                    slot.material = bpy.data.materials.get("Branch")


def create_new_scene():
    """Create a new scene with a ground plane, ground PBR material, grass particle system, and vineyard trellis system."""
    create_ground_plane()
    setup_pbr_material(pbr_material)
    add_grass_particles()
    create_vineyard_trellis(plant_models, post_model)
    configure_materials()
    
            
def create_camera(name, location, rotation, scale):
    """
    Create a new camera and add it to the Cameras collection.

    Parameters:
    name (str): Name of the camera
    location (tuple): Location of the camera
    rotation (tuple): Rotation of the camera
    scale (float): Scale of the camera

    Returns:
    bpy.types.Object: The created camera object
    """
    if "Cameras" not in bpy.data.collections:
        cameras_collection = bpy.data.collections.new("Cameras")
        bpy.context.scene.collection.children.link(cameras_collection)
    else:
        cameras_collection = bpy.data.collections["Cameras"]
    
    bpy.ops.object.camera_add(location=location, rotation=rotation)
    camera = bpy.context.object
    camera.name = name
    camera.scale = (scale, scale, scale)
    
    cameras_collection.objects.link(camera)
    bpy.context.scene.collection.objects.unlink(camera)

    return camera

    
def setup_camera(camera, focal_length=6, sensor_width=9.9, sensor_height=14.5, resolution_x=1104, resolution_y=1608):
    """
    Configure a camera's properties.

    Parameters:
    camera (bpy.types.Object): Camera object to configure
    focal_length (float): Focal length of the camera
    sensor_width (float): Sensor width of the camera
    sensor_height (float): Sensor height of the camera
    resolution_x (int): Horizontal resolution
    resolution_y (int): Vertical resolution
    """
    camera.data.lens = focal_length
    camera.data.sensor_width = sensor_width
    camera.data.sensor_height = sensor_height
    bpy.context.scene.render.resolution_x = resolution_x
    bpy.context.scene.render.resolution_y = resolution_y
    camera.data.sensor_fit = 'HORIZONTAL'


def camera_platform():
    """Create a platform of four cameras inside the scene."""
    camera_1 = create_camera(name="Camera_1", location=(4.735, -5, 1), rotation=(1.5708, 0, 2.129), scale=0.471)
    setup_camera(camera_1, focal_length=8) # focal length 6mm: location x 4.6, rotation z 2.181
    
    camera_2 = create_camera(name="Camera_2", location=(4.735, -4.9, 1), rotation=(1.5708, 0, 1.012), scale=0.471)
    setup_camera(camera_2, focal_length=8) # focal length 6mm: location x 4.6, rotation z 0.959 
    
    camera_3 = create_camera(name="Camera_3", location=(5, -5, 1), rotation=(1.5708, 0, 3.142), scale=0.471)
    setup_camera(camera_3)
    
    camera_4 = create_camera(name="Camera_4", location=(5, -4.9, 1), rotation=(1.5708, 0, 0), scale=0.471)
    setup_camera(camera_4)


if __name__ == "__main__":
    create_new_scene()
    camera_platform()