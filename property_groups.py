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

from typing import Any

import bpy
from bpy_extras.io_utils import (
    orientation_helper,
    path_reference_mode,
    axis_conversion,
)


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
    source_collection: bpy.props.PointerProperty(
        name="Source Collection",
        description="",
        type=bpy.types.Collection,
    )
    destination_path: bpy.props.StringProperty(
        name="Destination Path", description="", default="", subtype="DIR_PATH"
    )
    make_today_sub_dir: bpy.props.BoolProperty(
        name="Make Today's Dir",
        description="",
        default=True,
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


class ExporterParametersBase(bpy.types.PropertyGroup):
    def get_parameters_as_dict(self, ignore: tuple[str]) -> dict[str, Any]:
        dic_op_parameters = {}
        # 自身の全フィールドの値を辞書として取得する("ignore"で指定されたものは除外)
        [
            dic_op_parameters.setdefault(k, getattr(self, k))
            for k in [*self.__annotations__]
            if not k in ignore
        ]
        return dic_op_parameters

    def set_parameters(
        self, target_data: bpy.types.Operator | bpy.types.PropertyGroup, parameters: dict[Any]
    ):
        # 取得したパラメーターをOperatorまたはPropertyGroupのプロパティにセットする｡
        for k, v in parameters.items():
            setattr(target_data, k, v)


@orientation_helper(axis_forward="-Z", axis_up="Y")
class FBXParameters(ExporterParametersBase):

    ignore_props = (
        "exporter",
        "filter_glob",
        "directory",
        "ui_tab",
        "filepath",
        "files",
        "use_selection",
        "use_visible",
        "use_active_collection",
        "batch_mode",
        "use_batch_own_dir",
        "expand_include",
        "expand_transform",
        "expand_orientation",
        "expand_armature",
        "expand_animation",
    )

    # ----------------------------------------------------------
    #    For UI
    # ----------------------------------------------------------
    expand_include: bpy.props.BoolProperty(
        name="Expand Include",
        description="",
        default=True,
    )
    expand_transform: bpy.props.BoolProperty(
        name="Expand Include",
        description="",
        default=True,
    )
    expand_orientation: bpy.props.BoolProperty(
        name="Expand Include",
        description="",
        default=True,
    )
    expand_armature: bpy.props.BoolProperty(
        name="Expand Include",
        description="",
        default=False,
    )
    expand_animation: bpy.props.BoolProperty(
        name="Expand Include",
        description="",
        default=False,
    )
    # -----------------------------------------------------------

    filename_ext = ".fbx"
    filter_glob: bpy.props.StringProperty(default="*.fbx", options={"HIDDEN"})

    use_selection: bpy.props.BoolProperty(
        name="Selected Objects",
        description="Export selected and visible objects only",
        default=False,
    )
    use_visible: bpy.props.BoolProperty(
        name="Visible Objects", description="Export visible objects only", default=False
    )
    use_active_collection: bpy.props.BoolProperty(
        name="Active Collection",
        description="Export only objects from the active collection (and its children)",
        default=False,
    )
    global_scale: bpy.props.FloatProperty(
        name="Scale",
        description="Scale all data (Some importers do not support scaled armatures!)",
        min=0.001,
        max=1000.0,
        soft_min=0.01,
        soft_max=1000.0,
        default=1.0,
    )
    apply_unit_scale: bpy.props.BoolProperty(
        name="Apply Unit",
        description="Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)",
        default=True,
    )
    apply_scale_options: bpy.props.EnumProperty(
        items=(
            (
                "FBX_SCALE_NONE",
                "All Local",
                "Apply custom scaling and units scaling to each object transformation, FBX scale remains at 1.0",
            ),
            (
                "FBX_SCALE_UNITS",
                "FBX Units Scale",
                "Apply custom scaling to each object transformation, and units scaling to FBX scale",
            ),
            (
                "FBX_SCALE_CUSTOM",
                "FBX Custom Scale",
                "Apply custom scaling to FBX scale, and units scaling to each object transformation",
            ),
            ("FBX_SCALE_ALL", "FBX All", "Apply custom scaling and units scaling to FBX scale"),
        ),
        name="Apply Scalings",
        description="How to apply custom and units scalings in generated FBX file "
        "(Blender uses FBX scale to detect units on import, "
        "but many other applications do not handle the same way)",
    )

    use_space_transform: bpy.props.BoolProperty(
        name="Use Space Transform",
        description="Apply global space transform to the object rotations. When disabled "
        "only the axis space is written to the file and all object transforms are left as-is",
        default=True,
    )
    bake_space_transform: bpy.props.BoolProperty(
        name="Apply Transform",
        description="Bake space transform into object data, avoids getting unwanted rotations to objects when "
        "target space is not aligned with Blender's space "
        "(WARNING! experimental option, use at own risk, known to be broken with armatures/animations)",
        default=False,
    )

    object_types: bpy.props.EnumProperty(
        name="Object Types",
        options={"ENUM_FLAG"},
        items=(
            ("EMPTY", "Empty", ""),
            ("CAMERA", "Camera", ""),
            ("LIGHT", "Lamp", ""),
            ("ARMATURE", "Armature", "WARNING: not supported in dupli/group instances"),
            ("MESH", "Mesh", ""),
            ("OTHER", "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)"),
        ),
        description="Which kind of object to export",
        default={"EMPTY", "CAMERA", "LIGHT", "ARMATURE", "MESH", "OTHER"},
    )

    use_mesh_modifiers: bpy.props.BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to mesh objects (except Armature ones) - "
        "WARNING: prevents exporting shape keys",
        default=True,
    )
    use_mesh_modifiers_render: bpy.props.BoolProperty(
        name="Use Modifiers Render Setting",
        description="Use render settings when applying modifiers to mesh objects (DISABLED in Blender 2.8)",
        default=True,
    )
    mesh_smooth_type: bpy.props.EnumProperty(
        name="Smoothing",
        items=(
            ("OFF", "Normals Only", "Export only normals instead of writing edge or face smoothing data"),
            ("FACE", "Face", "Write face smoothing"),
            ("EDGE", "Edge", "Write edge smoothing"),
        ),
        description="Export smoothing information "
        "(prefer 'Normals Only' option if your target importer understand split normals)",
        default="OFF",
    )
    colors_type: bpy.props.EnumProperty(
        name="Vertex Colors",
        items=(
            ("NONE", "None", "Do not export color attributes"),
            ("SRGB", "sRGB", "Export colors in sRGB color space"),
            ("LINEAR", "Linear", "Export colors in linear color space"),
        ),
        description="Export vertex color attributes",
        default="SRGB",
    )
    prioritize_active_color: bpy.props.BoolProperty(
        name="Prioritize Active Color",
        description="Make sure active color will be exported first. Could be important "
        "since some other software can discard other color attributes besides the first one",
        default=False,
    )
    use_subsurf: bpy.props.BoolProperty(
        name="Export Subdivision Surface",
        description="Export the last Catmull-Rom subdivision modifier as FBX subdivision "
        "(does not apply the modifier even if 'Apply Modifiers' is enabled)",
        default=False,
    )
    use_mesh_edges: bpy.props.BoolProperty(
        name="Loose Edges",
        description="Export loose edges (as two-vertices polygons)",
        default=False,
    )
    use_tspace: bpy.props.BoolProperty(
        name="Tangent Space",
        description="Add binormal and tangent vectors, together with normal they form the tangent space "
        "(will only work correctly with tris/quads only meshes!)",
        default=False,
    )
    use_triangles: bpy.props.BoolProperty(
        name="Triangulate Faces",
        description="Convert all faces to triangles",
        default=False,
    )
    use_custom_props: bpy.props.BoolProperty(
        name="Custom Properties",
        description="Export custom properties",
        default=False,
    )
    add_leaf_bones: bpy.props.BoolProperty(
        name="Add Leaf Bones",
        description="Append a final bone to the end of each chain to specify last bone length "
        "(use this when you intend to edit the armature from exported data)",
        default=True,  # False for commit!
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
    use_armature_deform_only: bpy.props.BoolProperty(
        name="Only Deform Bones",
        description="Only write deforming bones (and non-deforming ones when they have deforming children)",
        default=False,
    )
    armature_nodetype: bpy.props.EnumProperty(
        name="Armature FBXNode Type",
        items=(
            ("NULL", "Null", "'Null' FBX node, similar to Blender's Empty (default)"),
            ("ROOT", "Root", "'Root' FBX node, supposed to be the root of chains of bones..."),
            ("LIMBNODE", "LimbNode", "'LimbNode' FBX node, a regular joint between two bones..."),
        ),
        description="FBX type of node (object) used to represent Blender's armatures "
        "(use the Null type unless you experience issues with the other app, "
        "as other choices may not import back perfectly into Blender...)",
        default="NULL",
    )
    bake_anim: bpy.props.BoolProperty(
        name="Baked Animation",
        description="Export baked keyframe animation",
        default=True,
    )
    bake_anim_use_all_bones: bpy.props.BoolProperty(
        name="Key All Bones",
        description="Force exporting at least one key of animation for all bones "
        "(needed with some target applications, like UE4)",
        default=True,
    )
    bake_anim_use_nla_strips: bpy.props.BoolProperty(
        name="NLA Strips",
        description="Export each non-muted NLA strip as a separated FBX's AnimStack, if any, "
        "instead of global scene animation",
        default=True,
    )
    bake_anim_use_all_actions: bpy.props.BoolProperty(
        name="All Actions",
        description="Export each action as a separated FBX's AnimStack, instead of global scene animation "
        "(note that animated objects will get all actions compatible with them, "
        "others will get no animation at all)",
        default=True,
    )
    bake_anim_force_startend_keying: bpy.props.BoolProperty(
        name="Force Start/End Keying",
        description="Always add a keyframe at start and end of actions for animated channels",
        default=True,
    )
    bake_anim_step: bpy.props.FloatProperty(
        name="Sampling Rate",
        description="How often to evaluate animated values (in frames)",
        min=0.01,
        max=100.0,
        soft_min=0.1,
        soft_max=10.0,
        default=1.0,
    )
    bake_anim_simplify_factor: bpy.props.FloatProperty(
        name="Simplify",
        description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
        min=0.0,
        max=100.0,  # No simplification to up to 10% of current magnitude tolerance.
        soft_min=0.0,
        soft_max=10.0,
        default=1.0,  # default: min slope: 0.005, max frame step: 10.
    )
    path_mode: path_reference_mode
    embed_textures: bpy.props.BoolProperty(
        name="Embed Textures",
        description='Embed textures in FBX binary file (only for "Copy" path mode!)',
        default=False,
    )
    batch_mode: bpy.props.EnumProperty(
        name="Batch Mode",
        items=(
            ("OFF", "Off", "Active scene to file"),
            ("SCENE", "Scene", "Each scene as a file"),
            (
                "COLLECTION",
                "Collection",
                "Each collection (data-block ones) as a file, does not include content of children collections",
            ),
            (
                "SCENE_COLLECTION",
                "Scene Collections",
                "Each collection (including master, non-data-block ones) of each scene as a file, "
                "including content from children collections",
            ),
            (
                "ACTIVE_SCENE_COLLECTION",
                "Active Scene Collections",
                "Each collection (including master, non-data-block one) of the active scene as a file, "
                "including content from children collections",
            ),
        ),
    )
    use_batch_own_dir: bpy.props.BoolProperty(
        name="Batch Own Dir",
        description="Create a dir for each exported file",
        default=True,
    )
    use_metadata: bpy.props.BoolProperty(
        name="Use Metadata",
        default=True,
        options={"HIDDEN"},
    )


class SSE_SCENE_fbx_parameters(FBXParameters):
    pass


class VRMParameters(ExporterParametersBase):
    ignore_props = (
        "exporter",
        "use_addon_preferences",
        "export_only_selections",
    )

    use_addon_preferences: bpy.props.BoolProperty(  #
        name="Export using add-on preferences",
        description="Export using add-on preferences instead of operator arguments",
    )
    export_invisibles: bpy.props.BoolProperty(
        name="Export Invisible Objects",
        default=True,
    )
    export_only_selections: bpy.props.BoolProperty(
        name="Export Only Selections",
    )
    enable_advanced_preferences: bpy.props.BoolProperty(
        name="Enable Advanced Options",
    )
    export_fb_ngon_encoding: bpy.props.BoolProperty(
        name="Try the FB_ngon_encoding under development" + " (Exported meshes can be corrupted)",
    )
    export_all_influences: bpy.props.BoolProperty(
        name="Export All Bone Influences",
        description="Don't limit to 4, most viewers truncate to 4, "
        + "so bone movement may cause jagged meshes",
        default=False,
    )
    export_lights: bpy.props.BoolProperty(
        name="Export Lights",
    )


class SSE_SCENE_vrm_parameters(VRMParameters):
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
