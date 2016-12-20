#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import tempfile
import shutil
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gtk
from fvp_param import FvpParam
from fvp_plugin_manager import FvpPluginManager
from fvp_vm_environment import FvpVmEnvironment
from fvp_window import FvpWindow


class FvpApplication(Gtk.Application):

    """Application object for fvm-player"""

    def __init__(self):
        Gtk.Application.__init__(self, application_id="org.fpemud.lightbox",
                                 flags=Gio.ApplicationFlags.HANDLES_OPEN)
        self.param = FvpParam()
        self._main_win = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.param.tmpDir = tempfile.mkdtemp(prefix="lightbox.")
        self.param.pluginManager = FvpPluginManager(self.param)

    def do_shutdown(self):
        # fixme: should stop vm
        shutil.rmtree(self.param.tmpDir)
        Gtk.Application.do_shutdown(self)

    def do_command_line(self, command_line):
        assert False

        optionContext = GLib.OptionContext("ELEMENT")
#        optionContext.add_main_entries(optionEntries, None)
        optionContext.add_group(Gtk.get_option_group(True))
        if not optionContext.parse(command_line):
            print("option parsing failed: %s\n", )
            return 1

        return 0

    def do_activate(self):
        self._createWindow()

    def do_open(self, files, n_files, hint):
        self._createWindow()
        self._main_win.openVm(files[0].get_path())

    def getVmEnvironment(self, vmDir):
        vmEnv = FvpVmEnvironment()
        vmEnv.load(vmDir)
        return vmEnv

    def saveVmEnvironment(self, vmDir, vmEnv):
        pass

    def _createWindow(self):
        self._main_win = FvpWindow(self, self.param)
        self.add_window(self._main_win)
        self._main_win.show_all()
