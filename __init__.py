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
from . import Compositor_Scrub_Render, Compositor_Viewer_Cache_Playback


modules = [Compositor_Scrub_Render, Compositor_Viewer_Cache_Playback]


def register():
    from bpy.utils import register_class

    for module in modules:
        module.register()



def unregister():
    from bpy.utils import unregister_class

    for module in modules:
        module.unregister()



if __name__ == "__main__":
    register()