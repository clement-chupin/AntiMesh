bl_info = {
    "name": "Anti-mesh",
    "author": "Chupin Clément",
    "version": (1, 0),
    "blender": (2, 92, 0),
    "location": "Object > Anti-mesh",
    "description": "Dynamic boolean transform",
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

bool_active = False

@persistent
def toolUpdated(scene):    
    anti=bpy.context.active_object
    if anti.show_wire == False and anti.display_type == 'TEXTURED' and bool_active:
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
                        if mo.object ==anti:
                            is_in=True
                    if not is_in:
                        ob.modifiers.new("Anti_boolean",'BOOLEAN')
                        print(ob)
                        m = ob.modifiers[len(ob.modifiers)-1]
                        m.object = anti

class OBJECT_OT_bool_easy(bpy.types.Operator):
    bl_idname = "object.apply_all_bool"
    bl_label = "Apply the booleans modifiers"
    bl_icon = 'FUND'
    bl_options = {'REGISTER', 'UNDO'}
    delete_anti: bpy.props.BoolProperty(name="Delete anti-meshes")
    
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
                o = m.object
                bpy.ops.object.modifier_apply(modifier=m.name)
                if self.delete_anti:
                    o.select_set(True) 
                    bpy.ops.object.delete()
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.column().prop(self, "delete_anti")
        
class OBJECT_OT_make_target(bpy.types.Operator):
    bl_idname = "object.made_anti_cible"
    bl_label = "Make object as cible"
    bl_options = {'REGISTER', 'UNDO'}
    bl_icon = 'FUND'
    type = [
    ('NORMAL', "Normal", "Difference between 2 objects", 'CUBE', 0),
    ('ANTI', "Anti-mesh", "Intersection between 2 objects", 'SELECT_SET', 1),
    ('TARGET', "Target", "Union between 2 objects", 'SNAP_VOLUME', 2)]

    mode: bpy.props.EnumProperty(name= "Type of effect", items=type)
    
    def invoke(self, context, event):
        if context.object:
            return self.execute(context)
        else:
            self.report({"WARNING"}, "No active object, could not finish")
            return {"CANCELLED"}
        
    
    def execute(self, context):
        if self.mode == 'NORMAL':
            bpy.context.active_object.show_wire = False
            bpy.context.active_object.display_type = 'SOLID'
        if self.mode == 'ANTI':
            bpy.context.active_object.show_wire = False
            bpy.context.active_object.display_type = 'WIRE'
        if self.mode == 'TARGET':
            bpy.context.active_object.show_wire = True
            bpy.context.active_object.display_type = 'SOLID'
        return {'FINISHED'}
    def draw(self, context):
        layout = self.layout
        layout.column().prop(self, "mode")    
    

class pie_menu_mirror(Menu):
    bl_label = "Anti mesh"
    bl_icon = 'FUND'
    def draw(self, context):
        layout = self.layout
        pie = layout #layout.menu_pie()
        pie.operator("object.made_anti_cible",icon='SNAP_VERTEX')
        pie.operator("object.apply_all_bool",icon='EXPERIMENTAL')
        
        global bool_active
        if bool_active:
            pie.operator("object.active_bool_truc",text="OFF",icon='SHADING_RENDERED')
        else:
            
            pie.operator("object.active_bool_truc",text="ON",icon='SHADING_SOLID')
    
class callPieMenu(bpy.types.Operator):
    bl_idname = "object.menu_pie_miror_n"
    bl_label = "menu"
    def execute(self, context):
        bpy.ops.wm.call_menu(name="pie_menu_mirror")
        return {'FINISHED'}


class test1(bpy.types.Operator):
    bl_idname = "object.active_bool_truc"
    bl_label = "Active Mode"

    def execute(self, context):
        global bool_active
        if bool_active:
            bool_active=False
        else:
            bool_active=True
        return {'FINISHED'}

addon_keymaps = []
def register():
    bpy.app.handlers.depsgraph_update_post.append(toolUpdated)
    bpy.utils.register_class(OBJECT_OT_bool_easy)
    bpy.utils.register_class(OBJECT_OT_make_target)
    bpy.utils.register_class(test1)
    
    bpy.utils.register_class(pie_menu_mirror)
    bpy.utils.register_class(callPieMenu)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type= 'VIEW_3D')
        kmi = km.keymap_items.new("object.menu_pie_miror_n", type= 'X', value= 'PRESS', alt= True) 
        addon_keymaps.append((km, kmi))
        
def unregister():
    bpy.app.handlers.depsgraph_update_post.remove(toolUpdated)
    bpy.utils.unregister_class(OBJECT_OT_make_target)
    bpy.utils.unregister_class(OBJECT_OT_bool_easy)
    
    wm = bpy.context.window_manager
    for km in addon_keymaps:
        wm.keyconfigs.addon.keymaps.remove(km)
    addon_keymaps.clear()
    
if __name__ == "__main__":
    register()
