import bpy
import os


script_dir = os.path.dirname(bpy.context.space_data.text.filepath)
hdri_folder = os.path.join(script_dir, "assets", "hdri")
create_vineyard = os.path.join(script_dir, "create_scene_vineyard.py")


img_counter = 0
mask_counter_start = 0
original_camera_positions = {}


def purge_orphans():
    """
    Remove orphaned data blocks from the Blender file.
    """
    bpy.ops.outliner.orphans_purge(do_local_ids=True, do_linked_ids=True, do_recursive=True)


# source: https://github.com/CGArtPython/bpy_building_blocks_examples/blob/main/clean_scene/clean_scene_example_1.py
def clean_scene():
    """
    Remove all objects, collection, materials, particles, textures, 
    images, curves, meshes, actions, nodes, and worlds from the scene.
    """
    if bpy.context.active_object and bpy.context.active_object.mode == "EDIT":
        bpy.ops.object.editmode_toggle()

    for obj in bpy.data.objects:
        obj.hide_set(False)
        obj.hide_select = False
        obj.hide_viewport = False

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    collection_names = [col.name for col in bpy.data.collections]
    for name in collection_names:
        bpy.data.collections.remove(bpy.data.collections[name])

    world_names = [world.name for world in bpy.data.worlds]
    for name in world_names:
        bpy.data.worlds.remove(bpy.data.worlds[name])

    bpy.ops.world.new()
    bpy.context.scene.world = bpy.data.worlds["World"]

    purge_orphans()


def apply_hdri(folder_path, hdri_file):
    """
    Apply an HDRI image as the world environment for lighting and rendering.

    Parameters:
    folder_path (str): The folder path where the HDRI file is located.
    hdri_file (str): The filename of the HDRI image to apply.
    """
    hdri_path = os.path.join(folder_path, hdri_file)
    
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'
    
    bpy.context.scene.world.use_nodes = True
    world = bpy.context.scene.world
    node_tree = world.node_tree
    nodes = node_tree.nodes
    links = node_tree.links

    nodes.clear()

    node_background = nodes.new(type='ShaderNodeBackground')
    node_environment = nodes.new(type='ShaderNodeTexEnvironment')
    node_mapping = nodes.new(type='ShaderNodeMapping')
    node_texture_coord = nodes.new(type='ShaderNodeTexCoord')
    node_output = nodes.new(type='ShaderNodeOutputWorld')

    node_environment.image = bpy.data.images.load(hdri_path)

    links.new(node_texture_coord.outputs['Generated'], node_mapping.inputs['Vector'])
    links.new(node_mapping.outputs['Vector'], node_environment.inputs['Vector'])
    links.new(node_environment.outputs['Color'], node_background.inputs['Color'])
    links.new(node_background.outputs['Background'], node_output.inputs['Surface'])
    

def execute_script(script_path):
    """
    Execute a Python script from the specified file path.

    Parameters:
    script_path (str): Path to the Python script to execute
    """
    if os.path.exists(script_path):
        with open(script_path, "r") as file:
            script_code = file.read()
            exec(script_code, globals())
            

def store_camera_positions():
    """
    Store the current positions of all camera objects inside the scene.
    """
    for camera in bpy.data.objects:
        if camera.type == 'CAMERA':
            original_camera_positions[camera.name] = camera.location.copy()
            
            
def render_camera(camera, is_mask=False, mask_counter=None):
    """
    Render an image or mask from a specified camera in Blender.

    Parameters:
    camera (bpy.types.Object): The camera object to render from
    is_mask (bool): Whether to render a mask
    mask_counter (int, optional): Counter value for naming the mask file
    """
    global img_counter
    
    bpy.context.scene.cycles.samples = 128
    bpy.context.scene.cycles.adaptive_threshold = 0.1
    bpy.context.scene.cycles.denoising_use_gpu = True

    bpy.context.scene.camera = camera

    output_dir = os.path.join(script_dir, "renders")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    bpy.context.scene.view_settings.view_transform = 'Standard'
    bpy.context.scene.view_settings.look = 'None'
    bpy.context.scene.view_settings.exposure = 0.0
    bpy.context.scene.view_settings.gamma = 1.0
    
    bpy.context.scene.render.image_settings.file_format = 'PNG' # PNG for better segmentation masks
    if is_mask and mask_counter is not None:
        filepath = os.path.join(output_dir, f"render_{mask_counter}_mask.png")
    else:
        filepath = os.path.join(output_dir, f"render_{img_counter}.png")

    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)

    if not is_mask:
        img_counter += 1
        
        
def move_and_render_cameras(render_masks=False):
    """
    Move cameras to predefined positions along the vineyard and render images.

    Parameters:
    render_masks (bool): Whether to render segmentation masks instead of normal images.
    """
    global mask_counter_start

    cameras_collection = bpy.data.collections.get("Cameras")
    cameras_to_render = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
    original_positions = {camera: camera.location.x for camera in cameras_to_render}

    if not original_camera_positions:
        store_camera_positions()

    if render_masks:
        mask_counter = mask_counter_start
    else:
        mask_counter_start = img_counter
        mask_counter = None

    num_stops = 8  # default 8
    step_distance = -1.25
    row_offset = 2.0
    num_rows = 6  # default 6

    for row in range(num_rows):
        for camera in cameras_to_render:
            render_camera(camera, render_masks, mask_counter)
            if render_masks:
                mask_counter += 1

        for stop in range(1, num_stops + 1):
            for camera in cameras_to_render:
                camera.location.x += step_distance
                render_camera(camera, render_masks, mask_counter)
                if render_masks:
                    mask_counter += 1

        if row < num_rows - 1:
            for camera in cameras_to_render:
                camera.location.x = original_positions[camera]
                camera.location.y += row_offset

               
def reset_camera_positions():
    """
    Reset all camera objects to their original starting positions.
    """
    for camera in bpy.data.objects:
        if camera.type == 'CAMERA' and camera.name in original_camera_positions:
            camera.location = original_camera_positions[camera.name].copy()


def reset_material_nodes_to_emission():
    """
    Reset all material nodes to only use an emission shader.
    """
    for material in bpy.data.materials:
        material.use_nodes = True
        
        nodes = material.node_tree.nodes
        nodes.clear()

        emission_node = nodes.new(type='ShaderNodeEmission')
        emission_node.location = (0, 0)

        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (200, 0)

        links = material.node_tree.links
        links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])


def set_emission_material_color(material_names, color):
    """
    Set the color of the emission shader for the specified materials.

    Parameters:
    material_names (list): A list of material names to update
    color (tuple): A tuple of three floats representing the emission color
    """
    for material_name in material_names:
        material = bpy.data.materials.get(material_name)
        for node in material.node_tree.nodes:
            if node.type == 'EMISSION':
                node.inputs['Color'].default_value = (*color, 0.0)
                break


def set_world_to_emission_material(color):
    """
    Set the world background to an emission shader with the specified color.

    Parameters:
    color (tuple): A tuple of three floats representing the emission color
    """
    world = bpy.context.scene.world
    world.use_nodes = True

    nodes = world.node_tree.nodes
    nodes.clear()

    emission_node = nodes.new(type='ShaderNodeEmission')
    emission_node.location = (0, 0)
    emission_node.inputs['Color'].default_value = (*color, 1.0)

    output_node = nodes.new(type='ShaderNodeOutputWorld')
    output_node.location = (200, 0)

    links = world.node_tree.links
    links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])


def segmentation_masks():
    """
    Apply emission shaders with specific colors to grouped materials and the world background.
    """
    reset_material_nodes_to_emission()
    set_emission_material_color(["Grape", "Grape.001", "Grape.002"], (2.0/255, 2.0/255, 2.0/255))
    set_emission_material_color(["Leaf_1", "Leaf_1.001", "Leaf_1.002", "Leaf_2", "Leaf_2.001", "Leaf_2.002", "Leaf_3", "Leaf_3.001", "Leaf_3.002", "Trunk", "Trunk.001", "Trunk.002", "Twig 1", "Twig 1.001", "Twig 1.002", "Twig 2", "Twig 2.001", "Twig 2.002", "Branch.001", "Branch.002"], (1.0/255, 1.0/255, 1.0/255))
    set_emission_material_color(["Branch", "PBR_Material", "Rope_metall"], (0.0, 0.0, 0.0))
    set_world_to_emission_material((0.0, 0.0, 0.0))


def delete_ground_plane():
    """
    Delete the ground plane from the Blender scene if it exists.
    """
    ground_plane_name = "Ground Plane"
    ground_plane = bpy.data.objects.get(ground_plane_name)
    if ground_plane:
        bpy.data.objects.remove(ground_plane, do_unlink=True)
        
        
if __name__ == "__main__":
    hdri_files = [f for f in os.listdir(hdri_folder) if f.endswith('.hdr')]
    for hdri_file in hdri_files:
        clean_scene()
        apply_hdri(hdri_folder, hdri_file)
        execute_script(create_vineyard)
        move_and_render_cameras()
        reset_camera_positions()
        segmentation_masks()
        delete_ground_plane()
        move_and_render_cameras(render_masks=True)