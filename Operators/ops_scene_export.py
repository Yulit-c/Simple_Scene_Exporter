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

import re
from pathlib import Path
from datetime import datetime

import bpy

from ..property_groups import (
    FBXParameters,
    VRMParameters,
    SSE_SCENE_fbx_parameters,
    SSE_SCENE_vrm_parameters,
    get_addon_prop_root,
    get_export_settings,
    get_fbx_parameters,
    get_vrm_parameters,
)
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

logger = preparating_logger(__name__)
#######################################################f


"""---------------------------------------------------------
------------------------------------------------------------
    Operators
------------------------------------------------------------
---------------------------------------------------------"""


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

        # 出力先のディレクトリパスを作成
        dest_path = Path(export_settings.destination_path)
        if not dest_path.exists():
            self.report({"INFO"}, f"Dest Path does not exist : {dest_path}")
            return {"CANCELLED"}
        # プロパティに応じて今日付のディレクトリを作成する
        date = datetime.today()
        today = f"{date.year}_{date.month:0>2}_{date.day:0>2}"
        if export_settings.make_today_sub_dir:
            dest_path = dest_path.joinpath(today)
            dest_path.mkdir(exist_ok=True)

        # 出力ファイルパスを生成
        base_name = f"{export_settings.file_base_name}"
        # 今日付のタイムスタンプを付与する
        if export_settings.add_date_suffix:
            base_name += f"_{today}"
        # Overrideしない場合は連番を付与する
        new_numbering = None
        if not export_settings.enable_overwrite:
            for i in dest_path.glob(f"{base_name}*"):
                if not (mo := re.search(rf"({base_name})_(\d{{3}}$)", i.stem)):
                    continue
                old_numbering = mo[2]
                new_numbering = f"{int(old_numbering) + 1:0>3}"
            # 既存連番ファイルが無い場合は000を付与する
            numeric = new_numbering if new_numbering else "000"
            base_name += f"_{numeric}"

        file_name = f"{base_name }.{self.exporter.lower()}"  # {base_name}_{YYYY_MM_DD}_{numeric}.{extension}
        file_path = str(dest_path.joinpath(file_name))

        # アンドゥ履歴へ登録
        history_label = f"Simple {self.exporter} Export"
        bpy.ops.ed.undo_push(message=history_label)

        # エクスポーターに対応したファイルをエクスポートする
        with context.temp_override(selected_objects=export_settings.source_collection.all_objects):
            match self.exporter:
                case "FBX":
                    fbx_settings = get_fbx_parameters()
                    parameters = fbx_settings.get_parameters_as_dict(fbx_settings.ignore_props)
                    bpy.ops.export_scene.fbx(
                        filepath=file_path,
                        use_selection=True,
                        **parameters,
                    )

                case "VRM":
                    vrm_settings = get_vrm_parameters()
                    parameters = vrm_settings.get_parameters_as_dict(vrm_settings.ignore_props)
                    l = [i for i in context.selected_objects if i.type == "ARMATURE"]
                    if not len(l):
                        self.report({"INFO"}, f"Armature Object Count is not 1")
                        return {"CANCELLED"}
                    armature_object = l[0]
                    logger.debug(armature_object.name)
                    bpy.ops.export_scene.vrm(
                        filepath=file_path,
                        use_addon_preferences=False,
                        export_only_selections=True,
                        armature_object_name=armature_object.name,
                        **parameters,
                    )

        self.report({"INFO"}, f"Exported {self.exporter} File : {file_path}")

        return {"FINISHED"}


"""---------------------------------------------------------
------------------------------------------------------------
    Resiter Target
------------------------------------------------------------
---------------------------------------------------------"""
CLASSES = (
    SSE_OT_scene_export,
    SSE_OT_set_fbx_parameters,
    SSE_OT_set_vrm_parameters,
)
