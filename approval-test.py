import time
import bpy
import sys

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       )


argv = sys.argv
nodetext = argv[argv.index("--nodetext") + 1:][0]  # get all args after "--"

class NodeShareioApproval(Operator):  
    
    bl_label = "NodeShare.io"
    bl_idname = "wm.nodeshareio_approval"
    ns_string: StringProperty(name="", default="")
    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        self.ns_string = nodetext

    
        print('''
        ############# NODE TEXT STRING TO LOAD ##############
        ''')
        print(self.ns_string)
        print(f"Type:{type(self.ns_string)}")
        
        print('''
        #####################################################
        ''')
        print("Pasting Node Text to Material")
        bpy.ops.node.ns_paste_material(ns_string_ext = self.ns_string)


        return {'FINISHED'}
def main():
    bpy.ops.wm.nodeshareio_approval()

classes = (
    NodeShareioApproval,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
    bpy.ops.wm.nodeshareio_approval()
    time.sleep(5)
    bpy.ops.wm.quit_blender()