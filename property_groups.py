if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger


import bpy
from bpy_extras.io_utils import orientation_helper


"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from .Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################


"""---------------------------------------------------------
------------------------------------------------------------
    Property Group
------------------------------------------------------------
---------------------------------------------------------"""


class SSE_SCENE_export_settings(bpy.types.PropertyGroup):
    destination_path: bpy.props.StringProperty(
        name="Destination Path", description="", default="", subtype="DIR_PATH"
    )

    file_base_name: bpy.props.StringProperty(
        name="file_base_name",
        description="",
        default="",
    )

    add_date_suffix: bpy.props.BoolProperty(
        name="Add Date Suffix",
        description="",
        default=True,
    )

    enable_overwrite: bpy.props.BoolProperty(
        name="Enable Overwrite",
        description="",
        default=True,
    )


@orientation_helper(axis_forward="-Z", axis_up="Y")
class SSE_SCENE_fbx_parameters(bpy.types.PropertyGroup):
    filename_ext = ".fbx"
    filter_glob: bpy.props.StringProperty(default="*.fbx", options={"HIDDEN"})

    use_manual_orientation: bpy.props.BoolProperty(
        name="Manual Orientation",
        description="Specify orientation and scale, instead of using embedded data in FBX file",
        default=False,
    )
    global_scale: bpy.props.FloatProperty(
        name="Scale",
        min=0.001,
        max=1000.0,
        default=1.0,
    )
    bake_space_transform: bpy.props.BoolProperty(
        name="Apply Transform",
        description="Bake space transform into object data, avoids getting unwanted rotations to objects when "
        "target space is not aligned with Blender's space "
        "(WARNING! experimental option, use at own risk, known to be broken with armatures/animations)",
        default=False,
    )

    use_custom_normals: bpy.props.BoolProperty(
        name="Custom Normals",
        description="Import custom normals, if available (otherwise Blender will recompute them)",
        default=True,
    )
    colors_type: bpy.props.EnumProperty(
        name="Vertex Colors",
        items=(
            ("NONE", "None", "Do not import color attributes"),
            ("SRGB", "sRGB", "Expect file colors in sRGB color space"),
            ("LINEAR", "Linear", "Expect file colors in linear color space"),
        ),
        description="Import vertex color attributes",
        default="SRGB",
    )

    use_image_search: bpy.props.BoolProperty(
        name="Image Search",
        description="Search subdirs for any associated images (WARNING: may be slow)",
        default=True,
    )

    use_alpha_decals: bpy.props.BoolProperty(
        name="Alpha Decals",
        description="Treat materials with alpha as decals (no shadow casting)",
        default=False,
    )
    decal_offset: bpy.props.FloatProperty(
        name="Decal Offset",
        description="Displace geometry of alpha meshes",
        min=0.0,
        max=1.0,
        default=0.0,
    )

    use_anim: bpy.props.BoolProperty(
        name="Import Animation",
        description="Import FBX animation",
        default=True,
    )
    anim_offset: bpy.props.FloatProperty(
        name="Animation Offset",
        description="Offset to apply to animation during import, in frames",
        default=1.0,
    )

    use_subsurf: bpy.props.BoolProperty(
        name="Subdivision Data",
        description="Import FBX subdivision information as subdivision surface modifiers",
        default=False,
    )

    use_custom_props: bpy.props.BoolProperty(
        name="Custom Properties",
        description="Import user properties as custom properties",
        default=True,
    )
    use_custom_props_enum_as_string: bpy.props.BoolProperty(
        name="Import Enums As Strings",
        description="Store enumeration values as strings",
        default=True,
    )

    ignore_leaf_bones: bpy.props.BoolProperty(
        name="Ignore Leaf Bones",
        description="Ignore the last bone at the end of each chain (used to mark the length of the previous bone)",
        default=False,
    )
    force_connect_children: bpy.props.BoolProperty(
        name="Force Connect Children",
        description="Force connection of children bones to their parent, even if their computed head/tail "
        "positions do not match (can be useful with pure-joints-type armatures)",
        default=False,
    )
    automatic_bone_orientation: bpy.props.BoolProperty(
        name="Automatic Bone Orientation",
        description="Try to align the major bone axis with the bone children",
        default=False,
    )
    primary_bone_axis: bpy.props.EnumProperty(
        name="Primary Bone Axis",
        items=(
            ("X", "X Axis", ""),
            ("Y", "Y Axis", ""),
            ("Z", "Z Axis", ""),
            ("-X", "-X Axis", ""),
            ("-Y", "-Y Axis", ""),
            ("-Z", "-Z Axis", ""),
        ),
        default="Y",
    )
    secondary_bone_axis: bpy.props.EnumProperty(
        name="Secondary Bone Axis",
        items=(
            ("X", "X Axis", ""),
            ("Y", "Y Axis", ""),
            ("Z", "Z Axis", ""),
            ("-X", "-X Axis", ""),
            ("-Y", "-Y Axis", ""),
            ("-Z", "-Z Axis", ""),
        ),
        default="X",
    )

    use_prepost_rot: bpy.props.BoolProperty(
        name="Use Pre/Post Rotation",
        description="Use pre/post rotation from FBX transform (you may have to disable that in some cases)",
        default=True,
    )


class SSE_SCENE_vrm_parameters(bpy.types.PropertyGroup):
    pass


class SSE_SCENE_root_property_group(bpy.types.PropertyGroup):
    export_settings: bpy.props.PointerProperty(
        name="Export Settings",
        description="",
        type=SSE_SCENE_export_settings,
    )

    fbx_settings: bpy.props.PointerProperty(
        name="FBX Settings",
        description="",
        type=SSE_SCENE_fbx_parameters,
    )
    vrm_settings: bpy.props.PointerProperty(
        name="VRM Settings",
        description="",
        type=SSE_SCENE_vrm_parameters,
    )


"""---------------------------------------------------------
------------------------------------------------------------
    Functions
------------------------------------------------------------
---------------------------------------------------------"""


def get_addon_prop_root() -> SSE_SCENE_root_property_group:
    proproot = bpy.context.scene.simple_scene_exporter
    return proproot


def get_export_settings() -> SSE_SCENE_export_settings:
    prop_root = get_addon_prop_root()
    prop = prop_root.export_settings
    return prop


def get_fbx_parameters() -> SSE_SCENE_fbx_parameters:
    prop_root = get_addon_prop_root()
    prop = prop_root.fbx_settings
    return prop


def get_vrm_parameters() -> SSE_SCENE_vrm_parameters:
    prop_root = get_addon_prop_root()
    prop = prop_root.vrm_settings
    return prop


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    SSE_SCENE_export_settings,
    SSE_SCENE_fbx_parameters,
    SSE_SCENE_vrm_parameters,
    SSE_SCENE_root_property_group,
)
