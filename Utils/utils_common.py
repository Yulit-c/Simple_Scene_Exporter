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
from addon_utils import paths, check
from bpy.path import module_names

from ..property_groups import (
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


def get_enabled_addon_list():
    enabled_addon_list = []
    for path in paths():
        for mod_name, mod_path in module_names(path):
            is_enabled, is_loaded = check(mod_name)
            if not is_enabled:
                continue
            if "VRM_Addon_for_Blender" in mod_name:
                mod_name = mod_name.split("-")[0]
            enabled_addon_list.append(mod_name)
    return enabled_addon_list


def get_parameters_as_dict(self):
    dic_op_parameters = {}
    # 選択されているインポーターに応じたプロパティグループを取得する
    addon_prop = get_addon_prop_root()
    exporter = 0
    match exporter:
        case 0:
            exporter_prop = addon_prop.fbx_settings
        case 1:
            exporter_prop = addon_prop.vrm_settings
    # 取得したプロパティグループの全てのフィールドの値を辞書として取得する
    [dic_op_parameters.setdefault(k, getattr(exporter_prop, k)) for k in [*exporter_prop.__annotations__]]
    return dic_op_parameters


def set_parameters(self, target_object: bpy.types.Operator | bpy.types.PropertyGroup, parameters: dict[Any]):
    # 取得したパラメーターをOperatorまたはPropertyGroupの値にセットする｡
    for k, v in parameters.items():
        setattr(target_object, k, v)
