import bpy
import numpy

from ..config.main_config import GlobalConfig, LogicName

class MeshUtils:

    @classmethod
    def set_import_normals(cls,mesh,normals):
        # Blender4.2 移除了mesh.create_normal_splits()
        if bpy.app.version <= (4, 0, 0):
            # mesh.use_auto_smooth = True

            # 这里直接同步了SpectrumQT的导入代码，方便测试对比细节
            normals = numpy.asarray(normals, dtype=numpy.float32) 
            loop_vertex_idx = numpy.empty(len(mesh.loops), dtype=numpy.int32)
            mesh.loops.foreach_get('vertex_index', loop_vertex_idx)

            # Initialize empty split vertex normals
            mesh.create_normals_split()
            # Write vertex normals, they will be immidiately converted to loop normals
            mesh.loops.foreach_set('normal', normals[loop_vertex_idx].flatten().tolist())
            # Read loop normals
            recalculated_normals = numpy.empty(len(mesh.loops)*3, dtype=numpy.float32)
            mesh.loops.foreach_get('normal', recalculated_normals)
            recalculated_normals = recalculated_normals.reshape((-1, 3))
            # Force usage of custom normals
            mesh.use_auto_smooth = True
            # Force vertex normals interpolation across the polygon (required in older versions)
            mesh.polygons.foreach_set('use_smooth', numpy.ones(len(mesh.polygons), dtype=numpy.int8))
            # Write loop normals to permanent storage
            mesh.normals_split_custom_set(recalculated_normals.tolist())
        
        # if GlobalConfig.logic_name != LogicName.UnityCPU:
        mesh.normals_split_custom_set_from_vertices(normals)

        # 导入的时候，计算和不计算TANGENT没啥区别，干脆不计算了
        # 因为只要导出的时候计算就行了
        # mesh.calc_tangents()