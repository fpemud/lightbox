#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class FvpViewCreate(Gtk.HBox):

    def __init__(self):
        super(FvpViewCreate, self).__init__()

        self.noneDisplay = Gtk.EventBox()
        self.noneDisplay.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))
        self.add(self.noneDisplay)
