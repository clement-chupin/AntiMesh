# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
import bpy
from bpy.app.handlers import persistent
bl_info = {
    "name": "AntiMesh",
    "author": "Chupin Clément",
    "version": (1, 1),
    "blender": (2, 92, 0),
    "location": "View3D > Object > Anti Mesh",
    "description": "Dynamic boolean transform, Alt-X for shortcut, don't forget to active the add-on and make your cible object as target",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}
import bpy
import time
from bpy.types import WorkSpaceTool
from bpy.types import Menu
from bpy.app.handlers import persistent
from bpy.props import BoolProperty

class AddOn_AntiMesh_Property(bpy.types.PropertyGroup):
    anti_active: bpy.props.BoolProperty(name="AntiMesh")
    modifier_at_first: bpy.props.BoolProperty(name="Place new modifier at first")
    
    type_boolean = [
    ('DIFFERENCE', "Difference", "Difference between 2 objects", 'SELECT_DIFFERENCE', 0),
    ('INTERSECT', "Intersection", "Intersection between 2 objects", 'SELECT_INTERSECT', 1),
    ('UNION', "Union", "Union between 2 objects", 'SELECT_EXTEND', 2)]

    mode_boolean: bpy.props.EnumProperty(name= "Effect ", items=type_boolean, default='DIFFERENCE')
    
@persistent
def toolUpdated(scene):    
    anti=bpy.context.active_object
    if anti is not None:
        if anti.type == 'MESH':
            if anti.show_wire == False and anti.display_type == 'TEXTURED' and bpy.context.scene.custom_props.anti_active:
                if (bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).idname == "builtin.primitive_cube_add" 
                    and bpy.context.active_operator.bl_idname == 'MESH_OT_primitive_cube_add'
                    or bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).idname == "builtin.primitive_cone_add" 
                    and bpy.context.active_operator.bl_idname == 'MESH_OT_primitive_cone_add'
                    or bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).idname == "builtin.primitive_cylinder_add" 
                    and bpy.context.active_operator.bl_idname == 'MESH_OT_primitive_cylinder_add'
                    or bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).idname == "builtin.primitive_uv_sphere_add" 
                    and bpy.context.active_operator.bl_idname == 'MESH_OT_primitive_uv_sphere_add'
                    or bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode).idname == "builtin.primitive_ico_sphere_add" 
                    and bpy.context.active_operator.bl_idname == 'MESH_OT_primitive_ico_sphere_add'
                    ):
                    anti.scale = (1.001,1.001,1.001)
                    anti.display_type = 'WIRE'
                    for ob in bpy.data.objects:
                        if ob.type == 'MESH' and ob.show_wire == True:
                            is_in = False
                            for mo in ob.modifiers:
                                if mo.type == 'BOOLEAN':
                                    if mo.object ==anti:
                                        is_in=True       
                            if not is_in:
                                ob.modifiers.new("Anti_boolean",'BOOLEAN')
                                m = ob.modifiers[len(ob.modifiers)-1]
                                m.operation = bpy.context.scene.custom_props.mode_boolean
                                m.object = anti
                                if bpy.context.scene.custom_props.modifier_at_first:
                                    bpy.context.view_layer.objects.active = ob
                                    bpy.ops.object.modifier_move_to_index(modifier=m.name, index=0)

class OBJECT_OT_bool_easy(bpy.types.Operator):
    bl_idname = "object.apply_all_bool"
    bl_label = "Apply the booleans modifiers"
    bl_icon = 'FUND'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    bl_options = {'REGISTER', 'UNDO'}
    delete_anti: bpy.props.BoolProperty(name="Delete anti-meshes",default=True)
    def invoke(self, context, event):
        if context.object:
            return self.execute(context)
        else:
            self.report({"WARNING"}, "No active object, could not finish")
            return {"CANCELLED"}

    def execute(self, context):
        obj = bpy.context.active_object
        bpy.ops.object.select_all(action='DESELECT')
        for m in obj.modifiers:
            if m.type == 'BOOLEAN':
                if m.object is not None:
                    o = m.object
                    bpy.ops.object.modifier_apply(modifier=m.name)
                    if self.delete_anti:
                        o.select_set(True) 
                        bpy.ops.object.delete()
                else:
                    bpy.context.active_object.modifiers.remove(m)
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.column().prop(self, "delete_anti")
        
class OBJECT_OT_make_target(bpy.types.Operator):
    bl_idname = "object.made_anti_cible"
    bl_label = "Make object as"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectmode"
    
    bl_options = {'REGISTER', 'UNDO'}
    bl_icon = 'FUND'
    type_object = [
    ('NORMAL', "Normal", "Difference between 2 objects", 'CUBE', 0),
    ('ANTI', "Anti-mesh", "Intersection between 2 objects", 'SELECT_SET', 1),
    ('TARGET', "Target", "Union between 2 objects", 'SNAP_VOLUME', 2)]

    mode_object: bpy.props.EnumProperty(name= "Object :", items=type_object)
    def invoke(self, context, event):
        if context.object:
            return self.execute(context)
        else:
            self.report({"WARNING"}, "No active object, could not finish")
            return {"CANCELLED"}
        
    
    def execute(self, context):
        if self.mode_object == 'NORMAL':
            bpy.context.active_object.show_wire = False
            bpy.context.active_object.display_type = 'SOLID'
        if self.mode_object == 'ANTI':
            bpy.context.active_object.show_wire = False
            bpy.context.active_object.display_type = 'WIRE'
        if self.mode_object == 'TARGET':
            bpy.context.active_object.show_wire = True
            bpy.context.active_object.display_type = 'SOLID'
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        layout.column().prop(self, "mode_object")    


class VIEW3D_MT_mode_object_menu(Menu):
    bl_label = "Anti mesh"
    bl_icon = 'FUND'
    def draw(self, context):
        layout = self.layout
        layout.operator("object.made_anti_cible",text="Normal mode",icon='CUBE').mode_object = 'NORMAL'
        layout.operator("object.made_anti_cible",text="Effector mode",icon='SELECT_SET').mode_object = 'ANTI'
        layout.operator("object.made_anti_cible",text="Target mode",icon='SNAP_VOLUME').mode_object = 'TARGET'

class VIEW3D_MT_MainMenu(Menu):
    bl_label = "Anti mesh"
    bl_idname = "VIEW3D_MT_MainMenu"
    bl_icon = 'FUND'
    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene.custom_props,"anti_active")
        layout.operator("object.apply_all_bool",icon='MODIFIER')
        layout.menu("VIEW3D_MT_mode_object_menu",text="Change object mode",icon='MOD_EXPLODE')
        layout.separator(factor=1.0)
        layout.label(text="Advenced options",icon='PROPERTIES')
        layout.row()
        layout.prop(context.scene.custom_props,text="",property="mode_boolean")
        layout.prop(context.scene.custom_props,"modifier_at_first",icon='FUND')
        

def VIEW3D_MT_addon_top_bar(self, context):
    self.layout.menu(VIEW3D_MT_MainMenu.bl_idname)
    
addon_keymaps = []
def register():
    bpy.utils.register_class(AddOn_AntiMesh_Property)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=AddOn_AntiMesh_Property)
    
    bpy.app.handlers.depsgraph_update_post.append(toolUpdated)
    bpy.utils.register_class(OBJECT_OT_bool_easy)
    bpy.utils.register_class(OBJECT_OT_make_target)
    bpy.utils.register_class(VIEW3D_MT_mode_object_menu)
    bpy.utils.register_class(VIEW3D_MT_MainMenu)
    bpy.types.VIEW3D_MT_object.append(VIEW3D_MT_addon_top_bar)
    
    
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu", type= 'X', value= 'PRESS', alt= True)
        kmi.properties.name = "VIEW3D_MT_MainMenu"
        addon_keymaps.append((km, kmi))

def unregister():

    bpy.utils.unregister_class(AddOn_AntiMesh_Property)
    bpy.app.handlers.depsgraph_update_post.remove(toolUpdated)
    bpy.utils.unregister_class(OBJECT_OT_bool_easy)
    bpy.utils.unregister_class(OBJECT_OT_make_target)
    bpy.utils.unregister_class(VIEW3D_MT_mode_object_menu)
    bpy.utils.unregister_class(VIEW3D_MT_MainMenu)
    bpy.types.VIEW3D_MT_object.remove(VIEW3D_MT_addon_top_bar)
 
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc is not None:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    
if __name__ == "__main__":
    register()
