# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import bpy, addon_utils, os, shutil
from bpy_extras.image_utils import load_image
from os.path import basename, dirname
from sys import platform
from pathlib import Path
from bpy.props import StringProperty
from bpy.types import (
    Operator, 
    AddonPreferences,
    Header,
    Menu,
    Panel
)

addon_keymaps = []

# class CompositorViewerCachePrefs(bpy.types.AddonPreferences):
#     bl_idname = __package__

#     for mod in addon_utils.modules():
#         if mod.bl_info['name'] == "Compositor Viewer Cache":
#             filepath = mod.__file__

#     if platform == "win32":
#         templatepath= str(Path(filepath).parent) + str(Path('/Template/Comp_VIEWER_Template.blend'))
#     else:
#         templatepath= str(Path(filepath).parent) + str(Path('/Template/Comp_VIEWER_Template.blend'))
    
    
#     templatefilepath: bpy.props.StringProperty(
#         name="Blender Template",
#         subtype='FILE_PATH',
#         default = str(templatepath)
#     ) # type: ignore

#     templatename: bpy.props.StringProperty(
#     name="Blender Template",
#     # subtype='FILE_PATH',
#     default = "Comp_Viewer"
#     ) # type: ignore


#     def draw(self, context):
#         layout = self.layout
#         layout.label(text="""Blender file path to import the template from""")
#         layout.prop(self, "templatefilepath")
#         layout.label(text="""The template to import""")
#         layout.prop(self, "templatename")



# def import_template(context):

#     templatefilepath = Path(context.preferences.addons[__package__].preferences.templatefilepath)
#     templatename = context.preferences.addons[__package__].preferences.templatename


#     try:
#         bpy.data.workspaces[templatename]
#         bpy.context.window.workspace = bpy.data.workspaces[templatename]
#     except:
#         bpy.ops.wm.append(
#         filepath="Comp_VIEWER_Template.blend",
#         directory= str(str(templatefilepath)+ str(Path("/WorkSpace/"))),
#         filename = templatename)
#         bpy.context.window.workspace = bpy.data.workspaces[templatename]



# def scn_optimize(context):

#     bpy.context.scene.view_settings.view_transform = 'Standard'

#     bpy.context.scene.use_nodes = True
#     # bpy.context.scene.node_tree.use_opencl = True
#     # bpy.context.scene.node_tree.edit_quality = 'LOW'
#     # bpy.context.scene.node_tree.chunk_size = '256'

#     tree = bpy.context.scene.node_tree
#     for node in tree.nodes:
#         tree.nodes.remove(node)
    
#     centerx = bpy.context.scene.node_tree.view_center[0]
#     centery = bpy.context.scene.node_tree.view_center[1]

    
#     # create scale node
#     scale_node = tree.nodes.new(type='CompositorNodeScale')
#     scale_node.space = 'RENDER_SIZE'
#     scale_node.frame_method =  'FIT'
#     scale_node.inputs[0].default_value =  (.15,0.0,.15,1.0)
#     scale_node.location = centerx,centery

#     # create output node
#     comp_node = tree.nodes.new('CompositorNodeComposite')   
#     comp_node.location = centerx+200,centery-100

#     # create viwer node
#     view_node = tree.nodes.new('CompositorNodeViewer')   
#     view_node.location = centerx+200,centery+50

#     # link nodes
#     links = tree.links
#     link = links.new(scale_node.outputs[0], comp_node.inputs[0])
#     link = links.new(scale_node.outputs[0], view_node.inputs[0])


# ----------------------------------------------------------
#  Shortcuts Parsing System (supports CTRL/ALT/SHIFT/OSKEY)
# ----------------------------------------------------------

# All valid key enums in Blender
VALID_KEYS = {k.identifier for k in bpy.types.Event.bl_rna.properties['type'].enum_items}

MODIFIER_WORDS = {
    "CTRL": "ctrl",
    "CONTROL": "ctrl",
    "SHIFT": "shift",
    "ALT": "alt",
    "OSKEY": "oskey",
    "CMD": "oskey",
    "COMMAND": "oskey",
}

def parse_shortcut(text):
    """
    Converts shortcut string into Blender key + modifier dict.

    Examples:
      "Ctrl C"         → ("C", {"ctrl":True})
      "Alt Shift R"    → ("R", {"alt":True, "shift":True})
      "CTRL+ALT+V"     → ("V", {"ctrl":True, "alt":True})
      "NONE" or ""     → (None, {})

    """
    if not text or text.strip().upper() == "NONE":
        return None, {}

    parts = text.replace("+", " ").split()
    parts = [p.strip().upper() for p in parts]

    mods = {"ctrl": False, "shift": False, "alt": False, "oskey": False}
    key = None

    for p in parts:
        if p in MODIFIER_WORDS:                  # modifier (ctrl/shift/alt/cmd)
            mods[MODIFIER_WORDS[p]] = True
        elif p in VALID_KEYS:                    # a blender key (C, R, SPACE, F3, etc.)
            key = p

    if key is None:
        return None, {}

    return key, mods


class CompositorViewerCachePrefs(bpy.types.AddonPreferences):

    bl_idname = __package__

    Render_Cache_shortcut: bpy.props.StringProperty(
        name="Render Cache Shortcut",
        default="Ctrl Alt NUMPAD_0"
    ) # type: ignore

    Privew_Cache_shortcut: bpy.props.StringProperty(
        name="Privew Cache Shortcut",
        default="Shift Ctrl P"
    ) # type: ignore

    ViwerNode_Back_shortcut: bpy.props.StringProperty(
        name="ViwerNode Back Shortcut",
        default="Ctrl Shift V"
    ) # type: ignore

    Delete_Cache_shortcut: bpy.props.StringProperty(
        name="Delete Cache Shortcut",
        default="Shift Ctrl D"
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Customize Shortcuts")

        col.prop(self, "Render_Cache_shortcut")
        col.prop(self, "Privew_Cache_shortcut")
        col.prop(self, "ViwerNode_Back_shortcut")
        col.prop(self, "Delete_Cache_shortcut")




def render_it(context):

    # Auto set cache render path with scenename
    projpath = bpy.data.filepath
    projname = bpy.path.basename(projpath)
    directory = os.path.dirname(projpath)
    scn = bpy.context.scene
    scname = scn.name
    renderpath = Path("%s/%s_compcache_temp/%s_cache/%s_cache" % (directory , projname, scname, scname))
    bpy.context.scene.render.filepath = str(renderpath)

    olddisptype = bpy.context.preferences.view.render_display_type

    
    # Refresh Render View
    bpy.ops.screen.frame_jump(end=False)


    #set frame
    old_frame_start = scn.frame_start
    old_frame_end = scn.frame_end
    old_frame_current = scn.frame_current

    def renderinit(context):

        if  bpy.context.preferences.view.render_display_type != 'NONE':
            bpy.context.preferences.view.render_display_type = 'NONE'

        if bpy.context.scene.use_preview_range == True:
            
            scn.frame_start = scn.frame_preview_start
            scn.frame_end= scn.frame_preview_end
            scn.frame_current = scn.frame_start
        

    def postrender(context):
        scn.frame_start = old_frame_start
        scn.frame_end = old_frame_end
            

    renderinit(context)
    # bpy.app.handlers.render_post.append(postrender)
    bpy.ops.render.render("INVOKE_DEFAULT", animation=True)
    cache_it(context)
    bpy.context.preferences.view.render_display_type = olddisptype
    postrender(context)



    # while scn.frame_current == old_frame_current:
    #     continue
    # else:
    #     bpy.app.handlers.render_post.remove(postrender)



def imgdetect(context):
    scn = bpy.context.scene
    img_formt = str(scn.render.image_settings.file_format)

    if img_formt == "JPEG":
        img_formt = "jpg"
    elif img_formt == "PNG":
        img_formt = "png"
    elif img_formt == "TARGA":
        img_formt = "tga"
    elif img_formt == "TARGA_RAW":
        img_formt = "tga"
    elif img_formt == "BMP":
        img_formt = "bmp"
    elif img_formt == "IRIS":
        img_formt = "rgb"
    elif img_formt == "JPEG2000":
        img_formt = "jp2"
    elif img_formt == "CINEON":
        img_formt = "cin"
    elif img_formt == "DPX":
        img_formt = "dpx"
    elif img_formt == "OPEN_EXR":
        img_formt = "exr"
    elif img_formt == "OPEN_EXR_MULTILAYER":
        img_formt = "exr"
    elif img_formt == "HDR":
        img_formt = "hdr"
    elif img_formt == "TIFF":
        img_formt = "tif"
    else:
        img_formt = "png"


    filepath = scn.render.filepath
    cachename = bpy.path.basename(filepath)
    default_place_holder = "0000"+"." + img_formt


    img = cachename+default_place_holder
    imgpath = filepath + default_place_holder

    return img,imgpath


def cache_it(context):

    scn = bpy.context.scene
    scname = scn.name  

    img,imgpath = imgdetect(context)

    if bpy.data.images.get(img):
        loadimg = bpy.data.images[img]
        if bpy.data.images[img].filepath != imgpath:
            bpy.data.images[img].filepath = imgpath
    else:
        loadimg = load_image(imgpath, check_existing=True, place_holder=True)


    if bpy.context.scene.use_preview_range == True:
    
        end_frame = bpy.data.scenes[scname].frame_preview_end
        start_frame = bpy.data.scenes[scname].frame_preview_start
    else:
        end_frame = bpy.data.scenes[scname].frame_end
        start_frame = bpy.data.scenes[scname].frame_start


    bpy.context.area.spaces.active.image = loadimg
    loadimg.source = 'SEQUENCE'
    bpy.context.area.spaces.active.image_user.frame_duration = end_frame




def set_viwer_node(context):
    img = bpy.data.images["Viewer Node"]
    bpy.context.area.spaces.active.image = img


def dleteCache(context):
    img,imgpath = imgdetect(context)
    bpy.data.images[img].user_clear()
    bpy.data.images[img].reload()
    scn = bpy.context.scene
    filepath = scn.render.filepath
    #Delete directory
    directroy = str(Path(filepath).parents[0])
    shutil.rmtree(directroy)





# class ImportCompViwerTemplate(bpy.types.Operator):
#     """Import comp viewer template"""
#     bl_idname = "import.import_view_comp_template"
#     bl_label = "import comp viwer template"


#     def execute(self, context):

#         try:
#             import_template(context)
#             # scn_optimize(context)
#             return {'FINISHED'}
#         except:
#             self.report({'ERROR'},'No template found!')
#             return {'CANCELLED'}


class CompositorviewRenderCache(bpy.types.Operator):
    """Render the cache"""
    bl_idname = "view.composit_render_cache"
    bl_label = "Render Cache"
    bl_options = {'REGISTER'}


    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'IMAGE_EDITOR'
    

    def execute(self, context):
        if bpy.data.is_saved:
            
            cache_it(context)
            render_it(context)        
            set_viwer_node(context)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, 'File not saved!')
            return {'CANCELLED'}





class CompositorviewDiscCache(bpy.types.Operator):
    """Starts the Cache preview"""
    bl_idname = "view.composit_disc_cache"
    bl_label = "Preview Cache"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'IMAGE_EDITOR'

    def execute(self, context):
        try:
            cache_it(context)
            bpy.ops.image.reload()
            bpy.ops.screen.animation_play()
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No cache to preview')
            return {'CANCELLED'}



class CompositorSetViewNode(bpy.types.Operator):
    """Set Viwer Node Back"""
    bl_idname = "view.composit_set_view_node"
    bl_label = "Cache to Viwer Node"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'IMAGE_EDITOR'


    def execute(self, context):
        try:
            set_viwer_node(context)
            self.report({'INFO'}, 'Viewer Set')
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No Viewer Node found!')
            return {'CANCELLED'}




class CompositorviewDeleteCache(bpy.types.Operator):
    """Delete the cache Directory"""
    bl_idname = "view.compositor_delete_cache"
    bl_label = "Delete Cache"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.area and context.area.type == 'IMAGE_EDITOR'


    def execute(self, context):
        try:
            set_viwer_node(context)
            dleteCache(context)
            self.report({'INFO'}, 'Cache Deleted')
            return {'FINISHED'}
        except:
            self.report({'INFO'}, 'No Cache Directory to Delete')
            return {'CANCELLED'}


# UI


class viwerdisccache(Menu):
    bl_label = "Disc Cahce"
    bl_idname = "IMAGE_MT_disccache"


    
    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_DEFAULT'
        st = context.space_data
    
        layout.operator("view.composit_render_cache", text="Render Cache", icon='RENDER_ANIMATION')
        layout.operator("view.composit_disc_cache", text="Preview Cache", icon='PLAY')
        layout.operator("view.composit_set_view_node", text="Viwer Node", icon='LOOP_BACK')
        layout.operator("view.compositor_delete_cache", text="Delete Cache", icon='TRASH')



# def draw_file_import(self,context):
#     layout = self.layout
#     layout.operator("import.import_view_comp_template", text="Import Compositor Viewer Cache template")   


def draw_in_activeTool(self, context):
    layout = self.layout
    st = context.space_data
    if st.ui_mode == 'VIEW':

        row = layout.row()
        row.label(text="Compositor Cache")

        row = layout.row(align=True)

        # layout.separator_spacer()

        row.operator("view.composit_render_cache", text="", icon='RENDER_ANIMATION')
        row.operator("view.composit_disc_cache", text="", icon='PLAY')
        row.operator("view.composit_set_view_node", text="", icon='LOOP_BACK')
        row.operator("view.compositor_delete_cache", text="", icon='TRASH')

def draw_in_header(self, context):
    layout = self.layout
    st = context.space_data
    if st.ui_mode == 'VIEW':

        row = layout.row()
        row.label(text="")

        row = layout.row(align=True)

        # layout.separator_spacer()

        row.operator("view.composit_render_cache", text="", icon='RENDER_ANIMATION')
        row.operator("view.composit_disc_cache", text="", icon='PLAY')
        row.operator("view.composit_set_view_node", text="", icon='LOOP_BACK')
        row.operator("view.compositor_delete_cache", text="", icon='TRASH')


def draw_item(self, context):
    layout = self.layout
    layout.menu(viwerdisccache.bl_idname)






classes = (
    # CompositorViewerCachePrefs,
    # ImportCompViwerTemplate,
    CompositorViewerCachePrefs,
    CompositorviewRenderCache,
    CompositorviewDiscCache,
    CompositorSetViewNode,
    CompositorviewDeleteCache,
    viwerdisccache
)   


def register_keymaps():

    prefs = bpy.context.preferences.addons[__package__].preferences
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name="Image", space_type="IMAGE_EDITOR")

    def add_kmi(op_id, shortcut_text):
        key, mods = parse_shortcut(shortcut_text)
        if not key:
            return

        kmi = km.keymap_items.new(
            op_id,
            key,
            'PRESS',
            ctrl=mods["ctrl"],
            shift=mods["shift"],
            alt=mods["alt"],
            oskey=mods["oskey"]
        )
        addon_keymaps.append((km, kmi))


    add_kmi("view.composit_render_cache", prefs.Render_Cache_shortcut)
    add_kmi("view.composit_disc_cache", prefs.Privew_Cache_shortcut)
    add_kmi("view.composit_set_view_node", prefs.ViwerNode_Back_shortcut)
    add_kmi("view.compositor_delete_cache", prefs.Delete_Cache_shortcut)


def unregister_keymaps():

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


def register():

    from bpy.utils import register_class
    
    for c in classes:
        bpy.utils.register_class(c)

    # Add menus and UI
    bpy.types.IMAGE_MT_image.append(draw_item)
    bpy.types.IMAGE_PT_active_tool.append(draw_in_activeTool)
    bpy.types.IMAGE_HT_header.append(draw_in_header)
    register_keymaps()




def unregister():
    
    from bpy.utils import unregister_class
    
    unregister_keymaps()

    bpy.types.IMAGE_MT_image.remove(draw_item)
    bpy.types.IMAGE_PT_active_tool.remove(draw_in_activeTool)
    bpy.types.IMAGE_HT_header.remove(draw_in_header)
    
    for c in reversed(classes):
        bpy.utils.unregister_class(c)