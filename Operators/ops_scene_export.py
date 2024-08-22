if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups
    from ..Utils import utils_common

import bpy
import os

from ..property_groups import get_addon_prop_root

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
    Operators
------------------------------------------------------------
---------------------------------------------------------"""


class SSE_OT_scene_export(bpy.types.Operator):
    bl_idname = "sse.scene_export"
    bl_label = "Simple Scene Export"
    bl_description = ""
    bl_options = {"UNDO", "REGISTER"}

    def execute(self, context):
        return {"FINISHED"}


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (SSE_OT_scene_export,)
