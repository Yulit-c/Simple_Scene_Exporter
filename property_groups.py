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


class SSE_SCENE_root_property_group(bpy.types.PropertyGroup):
    influence: bpy.props.FloatProperty(
        name="Influence",
        description="",
        subtype="DISTANCE",
        default=0.01,
    )


"""---------------------------------------------------------
------------------------------------------------------------
    Functions
------------------------------------------------------------
---------------------------------------------------------"""


def get_addon_prop_root() -> SSE_SCENE_root_property_group:
    prop = bpy.context.scene.simple_scene_exporter
    return prop


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (SSE_SCENE_root_property_group,)
