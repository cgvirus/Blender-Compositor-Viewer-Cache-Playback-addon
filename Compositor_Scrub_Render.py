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


import bpy
import time
from bpy.types import Panel
from bpy.app.handlers import persistent



class SR_props:

    scrub_timer_running = False
    last_time = 0
    latency = 0.22
    

def remove_handler():
    for h in bpy.app.handlers.frame_change_post:
        if getattr(h, "__name__", "") == "schedule_render":
            bpy.app.handlers.frame_change_post.remove(h)
            print("Removed previous handler.")




def isCompositor_visible():

    ctx = bpy.context
    if ctx is None or ctx.screen is None:
        return False
    
    for area in ctx.screen.areas:
        if area.type == "NODE_EDITOR":
            space = area.spaces.active
            if hasattr(space, "tree_type") and space.tree_type == 'CompositorNodeTree':
                # print("The active area is the Compositor editor!")
                return True
    return False


def render_after_scrubbing():

    now = time.time()
    difference = now - SR_props.last_time
    
    if difference < SR_props.latency:
        #print("Still Scrubbing")
        return SR_props.latency
        
    #print("Scrubbing stopped")
    
    try:
        bpy.ops.render.render()
    except Exception as e:
        print("Error during render:", e)
            
    SR_props.scrub_timer_running = False
    
    return None




def schedule_render(scene):

    if not isCompositor_visible():
        return

    
    SR_props.last_time = time.time()

    if not SR_props.scrub_timer_running:
        SR_props.scrub_timer_running = True
        bpy.app.timers.register(render_after_scrubbing, first_interval = SR_props.latency )



def scrub_render_enable(self, context):

    if self.scrub_render_prop:
        print ("Scrub Enabled")
        remove_handler()
        bpy.app.handlers.frame_change_post.append(schedule_render)
    else:
        remove_handler()
        print ("Scrub disabled")


@persistent
def sr_load_post(dummy):
    """
    Restore handler when file is loaded and property was saved checked.
    (No use of bpy.context — safe for load_post)
    """
    try:
        for sc in bpy.data.scenes:
            if getattr(sc, "scrub_render_prop", False):
                print("Scrub Render: Restoring handler after file load.")
                remove_handler()
                bpy.app.handlers.frame_change_post.append(schedule_render)
                break
    except Exception as e:
        print("Scrub Render load_post error:", e)


#UI
class SR_PT_panel(bpy.types.Panel):

    bl_label = "Scrub Render"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Options"


    def draw(self, context):
        layout = self.layout
        layout.prop(context.scene, "scrub_render_prop")



classes = [

    SR_PT_panel
]

def register():
    
    for cls in classes:
        bpy.utils.register_class(cls) 

    bpy.types.Scene.scrub_render_prop = bpy.props.BoolProperty(
        name="Enable Scrub Render",
        description="A custom checkbox property",
        default=False,
        update= scrub_render_enable
        )
    
    bpy.app.handlers.load_post.append(sr_load_post)
    

def unregister():

    for h in list(bpy.app.handlers.load_post):
        if getattr(h, "__name__", "") == "sr_load_post":
            bpy.app.handlers.load_post.remove(h)
            
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.scrub_render_prop