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
from ..property_groups import *
from ..Utils.utils_common import get_enabled_addon_list

from ..Operators.ops_scene_export import (
    SSE_OT_set_target_collections,
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

logger = preparating_logger(__package__)
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

        # ----------------------------------------------------------
        #    UI List
        # ----------------------------------------------------------
        col = layout.column()
        col.prop(export_settings, "source_collection")
        col.separator()

        row = col.row(align=True)
        data = get_wm_root_prop().get_target_collections()
        data.reflesh_target_collection_list()
        row.template_list(
            SSE_UL_show_target_collections.__name__,
            "",
            data,
            "target_collection_list",
            data,
            "target_collections_active_index",
        )
        col = row.column(align=True)
        col.operator(
            SSE_OT_set_target_collections.bl_idname, text="", icon="LINKED"
        ).mode = "INCLUDE"
        col.operator(
            SSE_OT_set_target_collections.bl_idname, text="", icon="UNLINKED"
        ).mode = "EXCLUDE"
        col.operator(
            SSE_OT_set_target_collections.bl_idname, text="", icon="ARROW_LEFTRIGHT"
        ).mode = "INVERT"

        # ----------------------------------------------------------
        #    Operator
        # ----------------------------------------------------------
        col = layout.column()
        col.prop(export_settings, "destination_path")
        col.prop(export_settings, "copy_files")
        if export_settings.copy_files:
            col.prop(export_settings, "copy_destination_path")
        col.separator()
        col.operator(
            SSE_OT_set_fbx_parameters.bl_idname,
            text="Export Settings",
            icon="PREFERENCES",
        )
        col.separator()
        row = col.row()
        row.scale_y = 2.0
        row.operator(SSE_OT_scene_export.bl_idname, text="Export", icon="EXPORT")


"""---------------------------------------------------------
------------------------------------------------------------
    UI List
------------------------------------------------------------
---------------------------------------------------------"""


class SSE_UL_show_target_collections(bpy.types.UIList):

    def draw_item(
        self,
        context: bpy.types.Context,
        layout: bpy.types.UILayout,
        data,
        item: SSE_WM_target_collection,
        icon,
        active_data,
        active_propname,
        index,
    ):
        row = layout.row(align=True)
        match item.item_type:
            case "NONE":
                row.label(text=item.name, icon="INFO")
            case "COLLECTION":
                coll = get_coll_root_prop(item.collection)
                row.label(text=item.name, icon="OUTLINER_COLLECTION")
                row.prop(coll.get_target_info(), "is_target", text="")


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    SSE_PT_view_3d_panel,
    SSE_UL_show_target_collections,
)
