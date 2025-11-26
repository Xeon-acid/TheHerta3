import os
import struct

from ..config.main_config import GlobalConfig


class ObjWriter:
    '''
    工具类
    专门负责把ObjBufferModel中的数据写入到文件中

    这个类专门用在生成Mod时调用
    我们规定生成的Mod文件夹结构如下:

    文件夹: Mod_工作空间名称
    - 文件夹: Buffer                    存放所有二进制缓冲区文件,包括IB和VB文件
    - 文件夹: Texture                   存放所有贴图文件
    - 文件:   工作空间名称.ini           所有ini内容要全部写在一起,如果写在多个ini里面通过namespace关联,则可能会导致Mod开启或关闭时有一瞬间的上贴图延迟
    '''

    @staticmethod
    def write_ib_buf_r32_uint(index_list:list[int],buf_file_name:str):
        ib_path = os.path.join(GlobalConfig.path_generatemod_buffer_folder(), buf_file_name)
        packed_data = struct.pack(f'<{len(index_list)}I', *index_list)
        with open(ib_path, 'wb') as ibf:
            ibf.write(packed_data) 

