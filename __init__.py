bl_info = {
    "name": "Simple Scene Exporter",
    "author": "Yu-Lit",
    "version": (0, 1, 0),
    "blender": (4, 1, 0),
    "location": "",
    "description": "",
    "warning": "",
    "support": "COMMUNITY",
    "doc_url": "",
    "tracker_url": "",
    "category": "",
}


if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "debug",
        "property_groups",
        "ops_scene_export",
        "ui_panels",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from .Logging import preparation_logger
    from . import debug
    from . import property_groups
    from .Operators import ops_scene_export
    from .UI import ui_panels


import bpy

from .debug import (
    launch_debug_server,
)


"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from .Logging.preparation_logger import preparating_logger

logger = preparating_logger(__name__)


"""---------------------------------------------------------
------------------------------------------------------------
    REGISTER/UNREGISTER
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    *property_groups.CLASSES,
    *ops_scene_export.CLASSES,
    *ui_panels.CLASSES,
)


def register():
    for cls in CLASSES:
        try:
            bpy.utils.register_class(cls)
        except:
            logger.debug(f"{cls.__name__} : already registred")

    ## Property Group の登録
    bpy.types.Scene.simple_scene_exporter = bpy.props.PointerProperty(
        type=property_groups.SSE_SCENE_root_property_group
    )

    # デバッグ用
    # launch_debug_server()


def unregister():
    for cls in CLASSES:
        if hasattr(bpy.types, cls.__name__):
            bpy.utils.unregister_class(cls)
            logger.debug(f"{cls.__name__} unregistred")
