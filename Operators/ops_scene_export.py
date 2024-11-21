if "bpy" in locals():
    import importlib

    reloadable_modules = [
        "preparation_logger",
        "property_groups",
        "utils_common",
        "utils_ui",
    ]

    for module in reloadable_modules:
        if module in locals():
            importlib.reload(locals()[module])

else:
    from ..Logging import preparation_logger
    from .. import property_groups
    from ..Utils import utils_common
    from ..Utils import utils_ui

import shutil
from pathlib import Path
from datetime import datetime

import bpy

from ..property_groups import *
from ..Utils.utils_ui import (
    draw_fbx_parameters,
    draw_vrm_parameters,
)

"""---------------------------------------------------------
------------------------------------------------------------
    Logger
------------------------------------------------------------
---------------------------------------------------------"""
from ..Logging.preparation_logger import preparating_logger

logger = preparating_logger(__package__)
#######################################################f


"""---------------------------------------------------------
------------------------------------------------------------
    Operators
------------------------------------------------------------
---------------------------------------------------------"""


class SSE_OT_set_target_collections(bpy.types.Operator):
    bl_idname = "sse.set_target_collections"
    bl_label = "Set Target Collections"
    bl_description = ""
    bl_options = {"INTERNAL", "UNDO"}

    mode: bpy.props.EnumProperty(
        name="Mode",
        description="",
        items=(
            ("INCLUDE", "Include", ""),
            ("EXCLUDE", "Exclude", ""),
            ("INVERT", "Invert", ""),
        ),
        default="INCLUDE",
    )

    def execute(self, context):
        source_collection = get_export_settings().get_source_collection()
        for coll in source_collection.children:
            target_info = get_coll_root_prop(coll).get_target_info()
            match self.mode:
                case "INCLUDE":
                    target_info.is_target = True
                case "EXCLUDE":
                    target_info.is_target = False
                case "INVERT":
                    target_info.is_target = not (target_info.is_target)

        return {"FINISHED"}


class SSE_OperatorBase(bpy.types.Operator):
    exporter: bpy.props.EnumProperty(
        name="Exporter",
        description="",
        items=(
            ("FBX", "FBX", "Export FBX File"),
            ("VRM", "VRM", "Export VRM File"),
        ),
        default="FBX",
    )


class SSE_OT_set_fbx_parameters(SSE_OperatorBase, FBXParameters):
    bl_idname = "sse.set_fbx_parameters"
    bl_label = "Set FBX Parameters"
    bl_description = ""
    bl_options = {"INTERNAL", "PRESET"}

    def draw(self, context):
        draw_fbx_parameters(self, self.layout)

    def invoke(self, context, event):
        fbx_settings = get_fbx_parameters()
        dic_parameters = fbx_settings.get_parameters_as_dict(self.ignore_props)
        fbx_settings.set_parameters(self, dic_parameters)
        from pprint import pprint

        pprint(dic_parameters)
        return context.window_manager.invoke_props_dialog(self, width=600)

    def execute(self, context):
        # オペレーターのプロパティの値をエクスポート設定にセットする
        fbx_settings = get_fbx_parameters()
        operator_parameters = self.as_keywords(ignore=self.ignore_props)
        for k, v in operator_parameters.items():
            logger.debug(f"{k} : {v}")
            setattr(fbx_settings, k, v)

        #
        return {"FINISHED"}


class SSE_OT_set_vrm_parameters(SSE_OperatorBase, VRMParameters):
    bl_idname = "sse.set_vrm_parameters"
    bl_label = "Set VRM Parameters"
    bl_description = ""
    bl_options = {"INTERNAL", "PRESET"}

    def draw(self, context):
        draw_vrm_parameters(self, self.layout)

    def invoke(self, context, event):
        vrm_settings = get_vrm_parameters()
        dic_parameters = vrm_settings.get_parameters_as_dict(self.ignore_props)
        vrm_settings.set_parameters(self, dic_parameters)
        return context.window_manager.invoke_props_dialog(self, width=600)

    def execute(self, context):
        # オペレーターのプロパティの値をエクスポート設定にセットする
        vrm_settings = get_vrm_parameters()
        operator_parameters = self.as_keywords(ignore=self.ignore_props)
        for k, v in operator_parameters.items():
            logger.debug(f"{k} : {v}")
            setattr(vrm_settings, k, v)

        #
        return {"FINISHED"}


class SSE_OT_scene_export(SSE_OperatorBase):
    bl_idname = "sse.scene_export"
    bl_label = "Simple Scene Export"
    bl_description = ""
    bl_options = {"INTERNAL"}

    def execute(self, context):
        # エクスポート設定のプロパティを取得
        export_settings = get_export_settings()
        # ソースコレクションが定義されていない場合は終了
        if not export_settings.source_collection:
            self.report({"INFO"}, f"Source Collection is not selected")
            return {"CANCELLED"}
        target_collection_list = (
            get_wm_root_prop().get_target_collections().target_collection_list
        )
        if target_collection_list[0].item_type == "NONE":
            self.report({"INFO"}, f"Collection not linked to source collection")
            return {"CANCELLED"}
        if not export_settings.destination_path:
            self.report({"INFO"}, f"Destination Path is not defined")
            return {"CANCELLED"}
        if export_settings.copy_files and not export_settings.copy_destination_path:
            self.report({"INFO"}, f"Copy Destination Path is not defined")
            return {"CANCELLED"}
        if export_settings.destination_path == export_settings.copy_destination_path:
            self.report({"INFO"}, f"Destination and Copy Destination Path are the same")
            return {"CANCELLED"}

        # 出力先のディレクトリパスを作成
        dest_abs_path = bpy.path.abspath(export_settings.destination_path)
        dest_path = Path(dest_abs_path)
        dest_path.mkdir(exist_ok=True)

        # アンドゥ履歴へ登録
        history_label = f"Simple {self.exporter} Export"
        bpy.ops.ed.undo_push(message=history_label)

        target: SSE_WM_target_collection
        # Source Collectionの子コレクションの内､ターゲットのコレクションをエクスポートする
        for target in target_collection_list:
            if not (target_coll := target.get_collection()):
                continue
            if not get_coll_root_prop(target_coll).get_target_info().is_target:
                continue

            # 出力ファイルパスを生成
            base_name = f"{target_coll.name}"

            file_name = f"{base_name }.{self.exporter.lower()}"
            file_path = dest_path.joinpath(file_name)

            # エクスポーターに対応したファイルをエクスポートする
            with context.temp_override(selected_objects=target_coll.all_objects):
                match self.exporter:
                    case "FBX":
                        fbx_settings = get_fbx_parameters()
                        parameters = fbx_settings.get_parameters_as_dict(
                            fbx_settings.ignore_props
                        )
                        bpy.ops.export_scene.fbx(
                            filepath=str(file_path), use_selection=True, **parameters
                        )
                logger.debug(f"Exported {self.exporter} File : {file_path}")

            # 出力ファイルのコピー
            if not (export_settings.copy_files and file_path.exists()):
                continue

            copy_dest_abs_path = bpy.path.abspath(export_settings.copy_destination_path)
            copy_dest_path = Path(copy_dest_abs_path)
            copy_file_path = copy_dest_path.joinpath(file_name)
            shutil.copyfile(file_path, copy_file_path)
            logger.debug(f"Copied FIle : {file_path} -->> {copy_file_path}\n")

        return {"FINISHED"}


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    SSE_OT_set_target_collections,
    SSE_OT_scene_export,
    SSE_OT_set_fbx_parameters,
    SSE_OT_set_vrm_parameters,
)
