import bpy
from ..utils.translate_utils import TR

class Properties_Global(bpy.types.PropertyGroup):
    show_obj_attributes :bpy.props.BoolProperty(
        name=TR.translate("显示Mesh属性列表"),
        description=TR.translate("勾选后在左下角展示obj的属性面板"),
        default=True
    ) # type: ignore

    @classmethod
    def show_obj_attributes(cls):
        '''
        bpy.context.scene.properties_global.show_obj_attributes
        '''
        return bpy.context.scene.properties_global.show_obj_attributes
    
    
    