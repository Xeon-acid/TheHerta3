import bpy
import blf
import os

from ..config.main_config import GlobalConfig, LogicName
from ..config.properties_dbmt_path import Properties_DBMT_Path
from ..config.properties_global import Properties_Global

# 3Dmigoto属性绘制
def draw_migoto_overlay():
    """在 3D 视图左下角绘制自定义信息"""
    context = bpy.context  # 直接使用 bpy.context 获取完整上下文
    if len(context.selected_objects) == 0:
        return
    
    if not Properties_Global.show_obj_attributes():
        return

    obj = context.selected_objects[0]
    region = context.region
    font_id = 0  # 默认字体

    # 设置绘制位置（左上角，稍微偏移避免遮挡默认信息）
    x = 70
    y = 60  # 从顶部往下偏移

    # 获取自定义属性
    gametypename = obj.get("3DMigoto:GameTypeName", None)
    recalculate_tangent = obj.get("3DMigoto:RecalculateTANGENT", None)
    recalculate_color = obj.get("3DMigoto:RecalculateCOLOR", None)

    # 设置字体样式（可选）
    blf.size(font_id, 24)  # 12pt 大小
    blf.color(font_id, 1, 1, 1, 1)  # 白色

    # 绘制文本
    if gametypename:
        y += 20
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, f"GameType: {gametypename}")

        y += 20
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, f"Recalculate TANGENT: {recalculate_tangent}")
        

        y += 20
        blf.position(font_id, x, y, 0)
        blf.draw(font_id, f"Recalculate COLOR: {recalculate_color}")

# 存储 draw_handler 引用，方便后续移除
migoto_draw_handler = None


# 用于选择DBMT所在文件夹，主要是这里能自定义逻辑从而实现保存DBMT路径，这样下次打开就还能读取到。
class OBJECT_OT_select_dbmt_folder(bpy.types.Operator):
    bl_idname = "object.select_dbmt_folder"
    bl_label = "选择SSMT-Package路径"

    directory: bpy.props.StringProperty(
        subtype='DIR_PATH',
        options={'HIDDEN'},
    ) # type: ignore

    def execute(self, context):
        scene = context.scene
        if self.directory:
            scene.dbmt_path.path = self.directory
            # print(f"Selected folder: {self.directory}")
            # 在这里放置你想要执行的逻辑
            # 比如验证路径是否有效、初始化某些资源等
            GlobalConfig.save_dbmt_path()
            
            self.report({'INFO'}, f"Folder selected: {self.directory}")
        else:
            self.report({'WARNING'}, "No folder selected.")
        
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    



class PanelBasicInformation(bpy.types.Panel):
    bl_label = "基础信息" 
    bl_idname = "VIEW3D_PT_CATTER_Buttons_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'TheHerta'
    

    def draw(self, context):
        layout = self.layout

        layout.prop(context.scene.properties_global,"show_obj_attributes")

        # use_sepecified_dbmt
        layout.prop(context.scene.dbmt_path, "use_specified_dbmt",text="使用指定位置的SSMT-Package")

        if Properties_DBMT_Path.use_specified_dbmt():
            # Path button to choose DBMT-GUI.exe location folder.
            row = layout.row()
            row.operator("object.select_dbmt_folder")

            ssmt_package_3dmigoto_path = os.path.join(Properties_DBMT_Path.path(), "3Dmigoto-GameMod-Fork")
            if not os.path.exists(ssmt_package_3dmigoto_path):
                layout.label(text="Error:Please select SSMT-Package path ", icon='ERROR')

        
        GlobalConfig.read_from_main_json()

        layout.label(text="SSMT-Package路径: " + GlobalConfig.dbmtlocation)
        # print(MainConfig.dbmtlocation)

        layout.label(text="当前游戏: " + GlobalConfig.gamename)
        layout.label(text="当前逻辑: " + GlobalConfig.logic_name)
        layout.label(text="当前工作空间: " + GlobalConfig.workspacename)

        # layout.prop(context.scene.properties_import_model,"use_mirror_workflow",text="使用非镜像工作流")
        



    