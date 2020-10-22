bl_info = {
    "name": "NodeShare.io",
    "description": "",
    "author": "hansford.dev",
    "version": (0, 0, 3),
    "blender": (2, 90, 1),
    "location": "3D View > NS.io",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}


import bpy
import requests
from requests.auth import HTTPBasicAuth

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


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class MyProperties(PropertyGroup):
    

    logged_in: BoolProperty(
        name="Login",
        description="Auth Bool",
        default = False
        )
    have_text: BoolProperty(
        name="NodeText",
        description="Node Text Check",
        default = False
        )
        
    '''
    my_int: IntProperty(
        name = "Int Value",
        description="A integer property",
        default = 23,
        min = 10,
        max = 100
        )
 

    my_float: FloatProperty(
        name = "Float Value",
        description = "A float property",
        default = 23.7,
        min = 0.01,
        max = 30.0
        )

    
    my_float_vector: FloatVectorProperty(
        name = "Float Vector Value",
        description="Something",
        default=(0.0, 0.0, 0.0), 
        min= 0.0, # float
        max = 0.1
    ) 
    my_enum: EnumProperty(
        name="Dropdown:",
        description="Apply Data to attribute.",
        items=[ ('OP1', "Option 1", ""),
                ('OP2', "Option 2", ""),
                ('OP3', "Option 3", ""),
               ]
        )
    '''
    
    username_string: StringProperty(
        name="User Input",
        description=":",
        default="",
        maxlen=1024,
        )
    pw_string: StringProperty(
        name="User Input",
        description=":",
        default="",
        maxlen=1024,
        subtype='PASSWORD'
        )
        
    token_string: StringProperty(
        name="Token",
        description=":",
        default="",
        maxlen=1024,
        )
    

    my_path: StringProperty(
        name = "Directory",
        description="Choose a directory:",
        default="",
        maxlen=1024,
        subtype='DIR_PATH'
        )

    nodesharer_string: StringProperty(
        name="NodeSharer String",
        description=":",
        default="",
        maxlen=1024,
        )

# ------------------------------------------------------------------------
#    Auth Operators
# ------------------------------------------------------------------------

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)
        

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
        
    
class NodeShareioLogin(Operator):
    bl_label = "Login"
    bl_idname = "wm.nodeshareio_login"
    
    def execute(self, context):
        scene = context.scene
        nodeshare = scene.my_tool
        
        # print the values to the console
        print("[  LOG  ]  attempting login")
        headers = {"Accept": "application/json"}
        un = nodeshare.username_string
        pw = nodeshare.pw_string
        auth = HTTPBasicAuth(un, pw)
        try:
            res = requests.post('http://localhost:5000/api/tokens', headers=headers, auth=auth)
            data = res.json()
            if data:
                token = data['token']
            nodeshare.token_string = token
            print(f"[  LOG  ]  set token: {nodeshare.token_string}")
            nodeshare.logged_in = True
        except:
            print('[  LOG  ]  Auth Error')
            
          
        return {'FINISHED'}



class NodeShareioLogout(Operator):
    bl_label = "Logout"
    bl_idname = "wm.nodeshareio_logout"
    
    def execute(self, context):
        scene = context.scene
        nodeshare = scene.my_tool
        nodeshare.token_string = ""
        nodeshare.logged_in =- False
        
        # print the values to the console
        print("Logged Out")
          
        return {'FINISHED'}

# ------------------------------------------------------------------------
#    Main Operator
# ------------------------------------------------------------------------

class NodeShareioCopy(Operator):  
    
    bl_label = "Copy Node Text"
    bl_idname = "wm.nodeshareio_main"
    
    def execute(self, context):
        scene = context.scene
        nodeshare = scene.my_tool

        
        try:
            nodesharer_string = scene.ns_string
            print(f"Node Sharerer Text String: \n{nodesharer_string}")
            nodeshare.have_text = True
            print("+++++++++++++++++++++++++++++++++++++++")
            print(nodeshare.have_text)
            print("+++++++++++++++++++++++++++++++++++++++")
            
            text = "Node Text Updated" if nodeshare.have_text else "Node Text Captured" 
            ShowMessageBox(text, "Success!") 
            
        except:
            return {'FINISHED'}
        
        return {'FINISHED'}

'''
class NodeShareioShare(Operator):  
    
    bl_label = "Share Node Text to NodeShare.io"
    bl_idname = "wm.nodeshareio_main"
    
    # print the values to the console
    print("[  LOG  ]  attempting share")
    headers = {"Accept": "application/json"}
    token = nodeshare.token_string
    try:
        res = requests.post('http://localhost:5000/api/tokens', headers=headers, auth=auth)
        data = res.json()
        if data:
            token = data['token']
        nodeshare.token_string = token
        print(f"[  LOG  ]  set token: {nodeshare.token_string}")
        nodeshare.logged_in = True
    except:
        print('[  LOG  ]  Auth Error')
        
      
    return {'FINISHED'}
    
'''    
'''
class OBJECT_MT_CustomMenu(bpy.types.Menu):
    bl_label = "Select"
    bl_idname = "OBJECT_MT_custom_menu"

    def draw(self, context):
        layout = self.layout

        # Built-in operators
        layout.operator("object.select_all", text="Select/Deselect All").action = 'TOGGLE'
        layout.operator("object.select_all", text="Inverse").action = 'INVERT'
        layout.operator("object.select_random", text="Random")
'''
# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_CustomPanel(Panel):
    bl_label = "NodeShare.io"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "NS.io"
    bl_context = "objectmode"   
    


    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        nodeshare = scene.my_tool
        

        
        #layout.menu(OBJECT_MT_CustomMenu.bl_idname, text="Presets", icon="SCENE")
        
        
        #LOGGED IN LOGIC
        if nodeshare.logged_in:
            
            text = "Update Node Text" if nodeshare.have_text else "Copy Node Text"
            layout.operator("wm.nodeshareio_main",text=text)
            layout.separator()
            layout.operator("wm.nodeshareio_logout")
        else: 
            layout.prop(nodeshare, "username_string", text="username")
            layout.prop(nodeshare, "pw_string", text="password")
            layout.separator()
            layout.operator("wm.nodeshareio_login")

# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    MyProperties,
    NodeShareioLogin,
    NodeShareioLogout,
    NodeShareioCopy,
    #NodeShareioShare,
    #OBJECT_MT_CustomMenu,
    OBJECT_PT_CustomPanel,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MyProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()