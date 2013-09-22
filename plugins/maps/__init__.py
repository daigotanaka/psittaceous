# The MIT License (MIT)
# 
# Copyright (c) 2013 Daigo Tanaka (@daigotanaka)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os

from plugins import Plugin
from plugins.maps.config import config


def register(app):
    if not config.get("active"):
        return
    global maps_plugin
    maps_plugin = MapsPlugin(app)
    app.register_command(["maps", "show me the map", "show me the map of", "show me the map at"], "maps", maps_plugin.show_maps)
    app.register_command(["directions", "directions to"], "maps directions", maps_plugin.show_direction)


class MapsPlugin(Plugin):

    def show_maps(self, param, **kwargs):
        if not param:
            self.app.say("Maps of where?")
            param = self.app.record_content(duration=7.0)
 
        self.app.say("Showing the map at %s" % param, nowait=True)
        html = "http://maps.google.com?q=%s" % param
        self.app.update_screen(html=html)

    def show_direction(self, param, **kwargs):
        if not param:
            self.app.say("Directions to where?")
            param = self.app.record_content(duration=7.0)
 
        self.app.say("Showing the directions to %s" % param, nowait=True)
        html = "http://maps.google.com?saddr=current location&daddr=%s" % param
        self.app.update_screen(html=html)
