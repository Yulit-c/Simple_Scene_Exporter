if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups

from typing import Any

import bpy
from ..property_groups import (
    FBXParameters,
    VRMParameters,
    get_addon_prop_root,
    get_export_settings,
    get_fbx_parameters,
    get_vrm_parameters,
)


"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from ..Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)
#######################################################

"""---------------------------------------------------------
------------------------------------------------------------
    Functions
------------------------------------------------------------
---------------------------------------------------------"""


def draw_fbx_parameters(data: FBXParameters, layout: bpy.types.UILayout):
    # ----------------------------------------------------------
    #    Main
    # ----------------------------------------------------------
    row = layout.row(align=True)
    row.prop(data, "path_mode")
    sub = row.row(align=True)
    sub.enabled = data.path_mode == "COPY"
    sub.prop(
        data,
        "embed_textures",
        text="",
        icon="PACKAGE" if data.embed_textures else "UGLYPACKAGE",
    )
    row = layout.row(align=True)
    row.prop(data, "batch_mode")
    sub = row.row(align=True)
    sub.prop(data, "use_batch_own_dir", text="", icon="NEWFOLDER")
    layout.separator()

    # ----------------------------------------------------------
    #    Include
    # ----------------------------------------------------------
    layout.column().prop(data, "object_types")
    layout.prop(data, "use_custom_props")
    layout.separator()

    # ----------------------------------------------------------
    #    Transform
    # ----------------------------------------------------------
    layout.prop(data, "global_scale")
    layout.prop(data, "apply_scale_options")

    layout.prop(data, "axis_forward")
    layout.prop(data, "axis_up")

    layout.prop(data, "apply_unit_scale")
    layout.prop(data, "use_space_transform")
    row = layout.row()
    row.prop(data, "bake_space_transform")
    row.label(text="", icon="ERROR")
    layout.separator()

    # ----------------------------------------------------------
    #    Geometry
    # ----------------------------------------------------------

    layout.prop(data, "mesh_smooth_type")
    layout.prop(data, "use_subsurf")
    layout.prop(data, "use_mesh_modifiers")
    layout.prop(data, "use_mesh_edges")
    layout.prop(data, "use_triangles")
    sub = layout.row()
    sub.prop(data, "use_tspace")
    layout.prop(data, "colors_type")
    layout.prop(data, "prioritize_active_color")
    layout.separator()

    # ----------------------------------------------------------
    #    Armature
    # ----------------------------------------------------------
    layout.prop(data, "primary_bone_axis")
    layout.prop(data, "secondary_bone_axis")
    layout.prop(data, "armature_nodetype")
    layout.prop(data, "use_armature_deform_only")
    layout.prop(data, "add_leaf_bones")
    layout.separator()

    # ----------------------------------------------------------
    #    Bake Animation
    # ----------------------------------------------------------
    sub = layout.column()
    sub.prop(data, "bake_anim")
    sub.enabled = data.bake_anim
    sub.prop(data, "bake_anim_use_all_bones")
    sub.prop(data, "bake_anim_use_nla_strips")
    sub.prop(data, "bake_anim_use_all_actions")
    sub.prop(data, "bake_anim_force_startend_keying")
    sub.prop(data, "bake_anim_step")
    sub.prop(data, "bake_anim_simplify_factor")


def draw_vrm_parameters(data: VRMParameters, layout: bpy.types.UILayout):
    layout.prop(data, "export_invisibles")
    layout.prop(data, "enable_advanced_preferences")
    if data.enable_advanced_preferences:
        box = layout.box()
        box.prop(data, "export_invisibles")
        box.prop(data, "export_fb_ngon_encoding")
        box.prop(data, "export_all_influences")
        box.prop(data, "export_lights")
