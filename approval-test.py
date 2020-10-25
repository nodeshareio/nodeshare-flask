import time
import bpy
import sys
import os
from os.path import abspath, join, dirname
from pathlib import Path
sys.path.insert(0, r"C:\NodeSharer-master")
import nodesharer
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

from dotenv import load_dotenv


dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

argv = sys.argv
args = argv[argv.index("--nodetext") + 1:] # get all args after "--nodetext"
nodetext = args[0]  
nodeid = args[1]  
def check_for_webm(id):
    path = f"C:\\Projects\\NS_TESTmedia\\node_preview_{id}.webm"
    my_file = Path(path)
    if my_file.is_file():
        print(f'''
    ##############################################
        Preview Exists at {path}
    ##############################################    
    ''')
        return True 

    print(f'''
    ##############################################
        Preview Does Not Exists at {path}
    ##############################################    
    ''')
    return False

class MyProperties(PropertyGroup):
    logged_in: BoolProperty(
        name="Admin Login",
        description="Auth Bool",
        default = False
        )
    have_text: BoolProperty(
        name="NodeTextBool",
        description="Node Text Check",
        default = False
        )
            
    username_string: StringProperty(
        name="Admin Uname",
        description=":",
        default="",
        maxlen=1024,
        )
    pw_string: StringProperty(
        name="Admin PW",
        description=":",
        default="",
        maxlen=1024,
        subtype='PASSWORD'
        )
        
    token_string: StringProperty(
        name="Admin Token",
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


class NodeShareioApprovalLogin(Operator):
    bl_label = "Login"
    bl_idname = "wm.nodeshareioadmin_login"
    
    def execute(self, context):
        scene = context.scene
        nodeshare = scene.ns_admin
        
        # print the values to the console
        print("[  LOG  ]  attempting login")
        headers = {"Accept": "application/json"}
        un = "admin@nodeshare.io"
        pw = os.environ.get("ADMIN_PW")
        auth = HTTPBasicAuth(un, pw)
        try:
            res = requests.post('http://localhost:5000/api/tokens', headers=headers, auth=auth)
            data = res.json()
            print(f'data')
            if data:
                token = data['token']
            nodeshare.token_string = token
            print(f"[  LOG  ]  set token: {nodeshare.token_string}")
            nodeshare.logged_in = True
        except:
            print('[  LOG  ]  Auth Error')          
        return {'FINISHED'}



class NodeShareioApprovalLogout(Operator):
    bl_label = "Logout"
    bl_idname = "wm.nodeshareioadmin_logout"
    
    def execute(self, context):
        scene = context.scene
        nodeshare = scene.ns_admin
        nodeshare.token_string = ""
        nodeshare.logged_in =- False
        
        # print the values to the console
        print("Logged Out")
          
        return {'FINISHED'}

class NodeShareioApproval(Operator):  
    
    bl_label = "NodeShare.io"
    bl_idname = "wm.nodeshareio_approval"
    ns_string: StringProperty(name="", default="")
    node_id: StringProperty(name="node_id", default="")

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        scene = context.scene
        self.ns_string = nodetext
        self.node_id = nodeid
    
        print('''
    ############# NODE TEXT STRING TO LOAD ##############
        ''')

        print(f"NODE ID: {self.node_id } \nNODE TEXT:{self.ns_string}")
        print(f"Type ID: {type(self.node_id)} \nType TEXT: {type(self.ns_string)}")
        
        print('''
    #####################################################
        ''')
        print("Pasting Node Text to Material")

        new_mat = nodesharer.NS_mat_constructor(self.ns_string)
        #bpy.ops.node.ns_paste_material(ns_string_ext = self.ns_string)
        print('''
    #####################################################

    Attempting Render

    #####################################################
        ''')

        scene.render.filepath = (f"C:\\Projects\\NS_TESTmedia\\node_preview_{self.node_id}.webm")
        #bpy.ops.render.render(animation=True)
        if check_for_webm(self.node_id):
            print("CALL approve_node() to send webm to server upon approval")
        else:
            return {'CANCELLED'}    



        return {'FINISHED'}
def main():
    bpy.ops.wm.nodeshareio_approval()

classes = (
    MyProperties,
    NodeShareioApproval,
    NodeShareioApprovalLogin,
    NodeShareioApprovalLogout,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    bpy.types.Scene.ns_admin = PointerProperty(type=MyProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.ns_admin


if __name__ == "__main__":
    register()
    bpy.ops.wm.nodeshareioadmin_login()
    bpy.ops.wm.nodeshareio_approval()
    bpy.ops.wm.nodeshareioadmin_logout()
    time.sleep(5)
    bpy.ops.wm.quit_blender()