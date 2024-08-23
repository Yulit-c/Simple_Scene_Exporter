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
from ..Operators.ops_scene_export import (
    SSE_OT_scene_export,
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
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "SSE"
    bl_label = "Simple Export"

    def draw(self, context):
        layout = self.layout
        export_settings = get_export_settings()

        col: bpy.types.UILayout
        col = layout.column()
        col.prop(export_settings, "destination_path")
        col.prop(export_settings, "file_base_name")
        col.prop(export_settings, "add_date_suffix")
        col.prop(export_settings, "enable_overwrite")
        layout.separator()

        col = layout.column()
        col.operator(SSE_OT_scene_export.bl_idname)
        col.operator(SSE_OT_scene_export.bl_idname)


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (SSE_PT_view_3d_panel,)
