if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
        "ops_scene_export",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups
    from ..Utils import utils_common
    from ..Operators import ops_scene_export


import bpy
from ..property_groups import (
    get_addon_prop_root,
    get_export_settings,
    get_fbx_parameters,
    get_vrm_parameters,
)
from ..Utils.utils_common import get_enabled_addon_list

from ..Operators.ops_scene_export import (
    SSE_OT_scene_export,
    SSE_OT_set_fbx_parameters,
    SSE_OT_set_vrm_parameters,
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
    Panel
------------------------------------------------------------
---------------------------------------------------------"""


class SSE_PT_view_3d_panel(bpy.types.Panel):
    bl_category = "SSE"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_label = "Simple Export"

    def draw(self, context):
        layout = self.layout
        export_settings = get_export_settings()

        col: bpy.types.UILayout
        col = layout.column()
        col.prop(export_settings, "source_collection")
        col.separator()
        col.prop(export_settings, "destination_path")
        col.prop(export_settings, "file_base_name")
        col.prop(export_settings, "make_today_sub_dir")
        col.separator(factor=1.0)
        col.prop(export_settings, "add_date_suffix")
        col.prop(export_settings, "enable_overwrite")
        layout.separator()

        col = layout.column()
        # ----------------------------------------------------------
        #    FBX Exporter
        # ----------------------------------------------------------
        exporter = "FBX"
        row = col.row(align=True)
        op = row.operator(SSE_OT_scene_export.bl_idname)
        op.exporter = exporter
        op = row.operator(SSE_OT_set_fbx_parameters.bl_idname, text="", icon="PREFERENCES")
        op.exporter = exporter
        # ----------------------------------------------------------
        #    VRM Exporter
        # ----------------------------------------------------------
        exporter = "VRM"
        row = col.row(align=True)
        row.enabled = "VRM_Addon_for_Blender" in get_enabled_addon_list()
        op = row.operator(SSE_OT_scene_export.bl_idname)
        op.exporter = exporter
        op = row.operator(SSE_OT_set_vrm_parameters.bl_idname, text="", icon="PREFERENCES")
        op.exporter = exporter


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (SSE_PT_view_3d_panel,)
