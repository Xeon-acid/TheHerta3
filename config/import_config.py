import os 
import json
import bpy
import json
import math
import bmesh
import os


from typing import List, Dict, Union
from dataclasses import dataclass, field, asdict

from ..utils.json_utils import JsonUtils
from ..utils.format_utils import Fatal

from .main_config import GlobalConfig

from ..common.migoto_format import D3D11GameType, TextureReplace


@dataclass
class ImportConfig:
    '''
    在一键导入工作空间时，Import.json会记录导入的GameType，在生成Mod时需要用到
    所以这里我们读取Import.json来确定要从哪个提取出来的数据类型文件夹中读取
    然后读取tmp.json来初始化D3D11GameType
    '''
    draw_ib: str  # DrawIB
    
    # 使用field(default_factory)来初始化可变默认值
    category_hash_dict: Dict[str, str] = field(init=False,default_factory=dict)
    import_model_list: List[str] = field(init=False,default_factory=list)
    match_first_index_list: List[int] = field(init=False,default_factory=list)
    part_name_list: List[str] = field(init=False,default_factory=list)
    vshash_list: List[str] = field(init=False,default_factory=list)
    
    vertex_limit_hash: str = ""
    work_game_type: str = ""
    
    TextureResource_Name_FileName_Dict: Dict[str, str] = field(init=False,default_factory=dict)  # 自动贴图配置项
    PartName_SlotTextureReplaceDict_Dict: Dict[str, Dict[str, TextureReplace]] = field(init=False,default_factory=dict)  # 自动贴图配置项

    def __post_init__(self):
        workspace_import_json_path = os.path.join(GlobalConfig.path_workspace_folder(), "Import.json")
        draw_ib_gametypename_dict = JsonUtils.LoadFromFile(workspace_import_json_path)
        gametypename = draw_ib_gametypename_dict.get(self.draw_ib,"")

        # 新版本中，我们把数据类型的信息写到了tmp.json中，这样我们就能够读取tmp.json中的内容来决定生成Mod时的数据类型了。
        extract_gametype_folder_path = GlobalConfig.path_extract_gametype_folder(draw_ib=self.draw_ib,gametype_name=gametypename)
        self.extract_gametype_folder_path = extract_gametype_folder_path
        tmp_json_path = os.path.join(extract_gametype_folder_path,"tmp.json")
        if os.path.exists(tmp_json_path):
            self.d3d11GameType:D3D11GameType = D3D11GameType(tmp_json_path)
        else:
            raise Fatal("您还没有提取模型并一键导入当前工作空间内容，如果您是在Mod逆向后直接生成Mod，那么步骤是错误的，Mod逆向只是拿到模型文件，要生成Mod还需要从游戏中提取原模型以获取模型的Hash值等用于生成Mod的重要信息，随后在Blender中一键导入当前工作空间内容后，即可选中工作空间集合来生成Mod。\n可以理解为：Mod逆向只是拿到模型和贴图，后面的步骤就和Mod逆向没有关系了，全部需要走Mod制作的标准流程")
        
        '''
        读取tmp.json中的内容，后续会用于生成Mod的ini文件
        需要在确定了D3D11GameType之后再执行
        '''
        extract_gametype_folder_path = GlobalConfig.path_extract_gametype_folder(draw_ib=self.draw_ib,gametype_name=self.d3d11GameType.GameTypeName)
        tmp_json_path = os.path.join(extract_gametype_folder_path,"tmp.json")
        tmp_json_dict = JsonUtils.LoadFromFile(tmp_json_path)

        self.category_hash_dict = tmp_json_dict["CategoryHash"]
        self.import_model_list = tmp_json_dict["ImportModelList"]
        self.match_first_index_list = tmp_json_dict["MatchFirstIndex"]
        self.part_name_list = tmp_json_dict["PartNameList"]
        # print(self.partname_textureresourcereplace_dict)
        self.vertex_limit_hash = tmp_json_dict["VertexLimitVB"]
        self.work_game_type = tmp_json_dict["WorkGameType"]
        self.vshash_list = tmp_json_dict.get("VSHashList",[])
        self.original_vertex_count = tmp_json_dict.get("OriginalVertexCount",0)

        # 自动贴图依赖于这个字典
        partname_textureresourcereplace_dict:dict[str,str] = tmp_json_dict["PartNameTextureResourceReplaceList"]

        print("读取配置: " + tmp_json_path)
        # print(partname_textureresourcereplace_dict)
        for partname, texture_resource_replace_list in partname_textureresourcereplace_dict.items():
            slot_texture_replace_dict = {}
            for texture_resource_replace in texture_resource_replace_list:
                splits = texture_resource_replace.split("=")
                slot_name = splits[0].strip()
                texture_filename = splits[1].strip()

                resource_name = "Resource_" + os.path.splitext(texture_filename)[0]

                filename_splits = os.path.splitext(texture_filename)[0].split("_")
                texture_hash = filename_splits[2]

                texture_replace = TextureReplace()
                texture_replace.hash = texture_hash
                texture_replace.resource_name = resource_name
                texture_replace.style = filename_splits[3]

                slot_texture_replace_dict[slot_name] = texture_replace

                self.TextureResource_Name_FileName_Dict[resource_name] = texture_filename

            self.PartName_SlotTextureReplaceDict_Dict[partname] = slot_texture_replace_dict