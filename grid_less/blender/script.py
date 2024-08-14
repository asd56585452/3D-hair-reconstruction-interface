import bpy
import mathutils
import random
import ctypes
import os
import sys
import shutil

args = sys.argv[sys.argv.index("--") + 1:]

bpy.ops.object.delete()
bpy.ops.wm.ply_import(filepath="../HairStep/results/real_imgs/hair3D/grid.ply")
hair = bpy.data.objects['grid']
drop_rate = 0.0

hair_vertices = hair.data.vertices
print(hair_vertices[0].co)
hair_edges = hair.data.edges
hairs = []
hair_max_len = 2
hair_t = [hair_edges[0].vertices[0]]
hair_edges_list = []
for edge in hair_edges:
    hair_edges_list.append([edge.vertices[0],edge.vertices[1]])
hair_edges_list.sort()
for edge in hair_edges_list:
    if hair_t[-1] != edge[0]:
        if random.random()>drop_rate:
            hairs.append(hair_t)
            if len(hair_t)>hair_max_len:
                hair_max_len = len(hair_t)
        hair_t = [edge[0]]
    hair_t.append(edge[1])

# 创建一个新的平面对象
bpy.ops.mesh.primitive_plane_add(size=0.0001, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
obj = bpy.context.object
obj.name = "HairPlane"



# 添加一个新的粒子系统
particle_system = obj.modifiers.new(name='Hair', type='PARTICLE_SYSTEM')
particle_system_settings = particle_system.particle_system.settings

# 设置粒子系统为头发类型
particle_system_settings.type = 'HAIR'
particle_system_settings.count = len(hairs)
particle_system_settings.hair_step = hair_max_len
bpy.ops.particle.disconnect_hair(all=False)
particle_system_settings.display_step = 5

## 确保粒子系统已经创建

bpy.ops.object.mode_set(mode='PARTICLE_EDIT')
bpy.context.scene.tool_settings.particle_edit.display_step = 5

#強至更新
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.ops.object.delete()


# 获取粒子系统（假设对象只有一个粒子系统）
particle_system = obj.particle_systems[-1]

# 获取粒子系统设置
particle_settings = particle_system.settings

particle_modifier = obj.modifiers[-1]

for i,particle in enumerate(particle_system.particles):
    hair_indexs = hairs[i]
    for ii,hair_key in enumerate(particle.hair_keys):
        if ii>=len(hair_indexs):
            co=hair_vertices[hair_indexs[-1]].co
        else:
            co=hair_vertices[hair_indexs[ii]].co
        co=mathutils.Vector((co.x, -co.z, co.y))
        hair_key.co_object_set(obj, particle_modifier, particle, co)

# 刪除ply檔
bpy.ops.object.select_all(action='DESELECT')
bpy.data.objects['grid'].select_set(True)
bpy.ops.object.delete() 
        
# 新增材質
        
# bpy.context.scene.render.engine = 'CYCLES'
material = bpy.data.materials.new(name="HairMaterial")
material.use_nodes = True

# 獲取材質節點
nodes = material.node_tree.nodes
links = material.node_tree.links

# 清除默認節點
for node in nodes:
    nodes.remove(node)

# 添加Principled BSDF節點
principled_bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
principled_bsdf.location = (0, 0)

# 添加材質輸出節點
material_output = nodes.new(type='ShaderNodeOutputMaterial')
material_output.location = (200, 0)

# 連接節點
links.new(principled_bsdf.outputs['BSDF'], material_output.inputs['Surface'])

# 設置頭髮顏色
principled_bsdf.inputs['Base Color'].default_value = (float(args[0]), float(args[1]), float(args[2]), 1)

# 將材質應用於對象
if obj.data.materials:
    obj.data.materials[0] = material
else:
    obj.data.materials.append(material)

# 確保粒子系統使用材質
particle_system.settings.material = 1  # 第1個材質

# 獲取當前區域和空間
area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
space = next(space for space in area.spaces if space.type == 'VIEW_3D')

# 設置著色模式
space.shading.type = 'RENDERED'

# 材質輸出
import bpy

class SimpleExportOperator(bpy.types.Operator):
    bl_idname = "export.um_export"
    bl_label = "Unity Material Export"
    bl_options = {'REGISTER', 'UNDO'}

    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        # 在这里添加你的自定义导出逻辑
        print(self.directory)
        shutil.copyfile("blender/HairMaterial.mat", self.directory+'HairMaterial.mat')
        shutil.copyfile("blender/HairShaderGraph.shadergraph", self.directory+'HairShaderGraph.shadergraph')
        rgba=principled_bsdf.inputs['Base Color'].default_value
        # 读取文件内容
        with open(self.directory+'HairMaterial.mat', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        # 编辑指定行
        line_number_to_edit = 82  # 要编辑的行号（从0开始）
        new_line_content = "    - _Color: {r: "+str(rgba[0])+", g: "+str(rgba[1])+", b: "+str(rgba[2])+", a: "+str(rgba[3])+"}\n"
        lines[line_number_to_edit] = new_line_content

        # 将修改后的内容写回文件
        with open(self.directory+'HairMaterial.mat', 'w', encoding='utf-8') as file:
            file.writelines(lines)
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

def menu_func_export(self, context):
    self.layout.operator(SimpleExportOperator.bl_idname, text="Unity Material Export ")

def register():
    bpy.utils.register_class(SimpleExportOperator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

def unregister():
    bpy.utils.unregister_class(SimpleExportOperator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
