#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk
from gi.repository import Gtk


class FvpViewCreate(Gtk.HBox):

    PAGE_SETUP = 1
    PAGE_WORK = 2

    def __init__(self, param, app, window):
        super(FvpViewCreate, self).__init__()

        self.param = param
        self.application = app
        self.window = window

        for plugin in self.param.pluginManager.getPluginList():
            for os_name in plugin.get_os_name_list():
                assert False

        self.noneDisplay = Gtk.EventBox()
        self.noneDisplay.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))
        self.add(self.noneDisplay)


    def _showSetupPage(self):
        pass

    def _showWorkPage(self):
        pass

