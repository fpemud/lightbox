#!/usr/bin/python3.4
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import traceback
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from autodrawer import AutoDrawer
from core.vm_object import FvpVmObject
from fvp_view_run import FvpViewRun


class FvpWindow(Gtk.ApplicationWindow):

    def __init__(self, param, app):
        Gtk.Window.__init__(self, application=app)

        self.param = param
        self.application = app

        self.gtkBuilder = Gtk.Builder()
        self.gtkBuilder.add_from_file(os.path.join(self.param.libDir, "fvp_window.ui"))

        self.mainVBox = self.gtkBuilder.get_object("main-vbox")
        self.fullscreenVBox = self.gtkBuilder.get_object("fullscreen-vbox")
        self.vmVBox = self.gtkBuilder.get_object("vm-vbox")
        self.actionGroupApp = self.gtkBuilder.get_object("actiongroup-app")
        self.actionGroupView = self.gtkBuilder.get_object("actiongroup-view")
        self.actionGroupVm = self.gtkBuilder.get_object("actiongroup-vm")
        self.actionViewFullscreen = self.gtkBuilder.get_object("action-view-fullscreen")

        self.vmViewer = FvpViewRun()
        self.vmViewer.set_size_request(640, 480)
        self.vmVBox.add(self.vmViewer)

        self.add(self.mainVBox)
        self.gtkBuilder.connect_signals(self)

        self.fullscreenDrawer = AutoDrawer()
        self.fullscreenDrawer.set_active(False)
        self.fullscreenDrawer.set_over(self.fullscreenVBox)
        # self.fullscreenDrawer.set_under(scroll)
        self.fullscreenDrawer.set_offset(-1)
        self.fullscreenDrawer.set_fill(False)
        self.fullscreenDrawer.set_overlap_pixels(1)
        self.fullscreenDrawer.set_nooverlap_pixels(0)
        self.fullscreenDrawer.show_all()

        self.connect("destroy", self.on_destroy)

        self.vmEnv = None
        self.vmObj = None

        self._updateActionState()

    def on_destroy(self, data=None):
        self.closeVm()
        self.fullscreenDrawer.destroy()
        self.fullscreenDrawer = None

    def on_action_quit(self, data=None):
        assert False
        print("on_action_app_quit")

    def on_action_vm_new(self, data=None):
        pass

    def on_action_vm_open(self, data=None):
        try:
            self.openVm()
        except:
            self._showException()

    def on_action_vm_power(self, data=None):
        assert self.vmObj is not None           # action should be in disable state when self.vmObj is None
        try:
            self.vmObj.powerButtonClicked()
        except:
            self._showException()

    def on_action_vm_reset(self, data=None):
        assert self.vmObj is not None           # action should be in disable state when self.vmObj is None
        try:
            self.vmObj.resetButtonClicked()
        except:
            self._showException()

    def on_action_view_fullscreen_toggled(self, data=None):
        if self.actionViewFullscreen.get_active():
            self.fullscreen()
            # self.fullscreenDrawer.set_active(True)
        else:
            # self.fullscreenDrawer.set_active(False)
            self.unfullscreen()

    def on_action_view_toolbar_toggled(self, data=None):
        assert False

    def on_vm_state_changed(self, vmObj, prop):
        try:
            if vmObj.get_property("state") == FvpVmObject.STATE_POWER_ON:
                self.vmViewer.connectVm(vmObj.getSpicePort())
                for pInfo in self.vmEnv.getPeripheralList():
                    if pInfo.connectWhenStart:
                        vmObj.addPeripheral(pInfo.obj)
            else:
                self.vmViewer.disconnectVm()		# fixme: can't get channel-destroy event in fvp_vm_viewer, so disconnect here.
        except:
            self._showException()

    def newVm(self):
        try:
            if self.vmObj is not None and self.vmObj.get_property("state") == FvpVmObject.STATE_POWER_ON:
                raise Exception("Please power off the curret virtual machine")

            if self.vmObj is not None:
                self.vmObj.release()
                self.vmObj = None
                self.vmEnv = None
        except:
            self._showException()

    def openVm(self, vmDir):
        try:
            if self.vmObj is not None and self.vmObj.get_property("state") == FvpVmObject.STATE_POWER_ON:
                raise Exception("Please power off the curret virtual machine")

            if self.vmObj is not None:
                self.vmObj.release()

            self.vmObj = FvpVmObject(self.param, vmDir)
            self.vmEnv = self.application.getVmEnvironment(self.vmObj.getVmDir())

            self.vmObj.connect("notify::state", self.on_vm_state_changed)
            self._updateActionState()
        except:
            self._showException()

    def closeVm(self):
        try:
            if self.vmEnv is not None:
                self.vmEnv = None
            if self.vmObj is not None:
                self.vmObj.powerDown()
                self.vmObj.release()
                self.vmObj = None
            self._updateActionState()
        except:
            self._showException()

    def _updateActionState(self):
        if self.vmObj is not None:
            self.actionGroupVm.set_sensitive(True)
        else:
            self.actionGroupVm.set_sensitive(False)

    def _showException(self):
        dialog = Gtk.MessageDialog(parent=self, flags=Gtk.DialogFlags.MODAL, type=Gtk.MessageType.ERROR,
                                   buttons=Gtk.ButtonsType.OK, message_format=traceback.format_exc())

        def _response(widget, response_id):
            widget.destroy()
        dialog.connect("response", _response)

        dialog.run()
