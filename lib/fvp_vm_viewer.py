#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import SpiceClientGLib
from gi.repository import SpiceClientGtk


class FvpVmViewer(Gtk.HBox):

    """A virtual machine viewer"""

    STATE_NONE = 1
    STATE_CONNECTING = 2
    STATE_RUNNING = 3

    def __init__(self):
        super(FvpVmViewer, self).__init__()

        self.spSession = None
        self.spChNewHandler = -1
        self.spChDestroyHandler = -1
        self.spChDisplay = None

        self.state = FvpVmViewer.STATE_NONE
        self.destroyHandler = -1
        self.display = None

        self.noneDisplay = Gtk.EventBox()
        self.noneDisplay.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0, 0, 0))
        self.add(self.noneDisplay)

    def connectVm(self, spicePort):
        assert self.state == FvpVmViewer.STATE_NONE

        self.destroyHandler = self.connect("destroy", self.on_destroy)
        self._createSpSession(spicePort)

    def disconnectVm(self):
        self._releaseSpSession()
        self.disconnect(self.destroyHandler)
        self.destroyHandler = -1

    def getstate(self):
        return self.state

    def on_destroy(self, data=None):
        self._releaseSpSession()

    def on_channel_new(self, session, channel):
        if isinstance(channel, SpiceClientGLib.DisplayChannel):
            self.spChDisplay = channel
            self._toStateRunning()
            return

    def on_channel_destroy(self, session, channel):
        assert False		# fixme: never get a destroy event, why?

        if isinstance(channel, SpiceClientGLib.MainChannel):
            self.disconnectVm()
            return

        # fixme: can we only use MainChannel, and delete these code?
        if isinstance(channel, SpiceClientGLib.DisplayChannel):
            self._toStateNone()
            self.spChDisplay = None
            return

    def _createSpSession(self, spicePort):
        assert self.spSession is None
        assert self.spChNewHandler == -1
        assert self.spChDestroyHandler == -1
        assert self.state == FvpVmViewer.STATE_NONE

        # session create
        sess = SpiceClientGLib.Session.new()
        sess.set_property("uri", "spice://127.0.0.1?port=%d" % (spicePort))

        # session connect
        self._toStateConnecting()
        newh = GObject.GObject.connect(sess, "channel-new", self.on_channel_new)
        destroyh = GObject.GObject.connect(sess, "channel-destroy", self.on_channel_destroy)
        ret = sess.connect()
        if not ret:
            self._toStateNone()
            GObject.GObject.disconnect(sess, destroyh)
            GObject.GObject.disconnect(sess, newh)
            raise Exception("Failed to connect to virtual machine by spice")

        # fill variables
        self.spSession = sess
        self.spChNewHandler = newh
        self.spChDestroyHandler = destroyh

    def _releaseSpSession(self):
        if self.spSession is not None:
            self._toStateNone()
            self.spChDisplay = None

            GObject.GObject.disconnect(self.spSession, self.spChDestroyHandler)
            GObject.GObject.disconnect(self.spSession, self.spChNewHandler)
            self.spSession.disconnect()
            self.spChDestroyHandler = -1
            self.spChNewHandler = -1
            self.spSession = None

    def _toStateNone(self):
        if self.state == FvpVmViewer.STATE_CONNECTING:
            self.state = FvpVmViewer.STATE_NONE
            return

        if self.state == FvpVmViewer.STATE_RUNNING:
            self.remove(self.display)
            self.add(self.noneDisplay)
            self.noneDisplay.show()
            self.display.destroy()
            self.display = None
            self.state = FvpVmViewer.STATE_NONE
            return

    def _toStateConnecting(self):
        assert self.state == FvpVmViewer.STATE_NONE

        self.state = FvpVmViewer.STATE_CONNECTING

    def _toStateRunning(self):
        assert self.state == FvpVmViewer.STATE_CONNECTING

        self.display = SpiceClientGtk.Display.new(self.spSession, self.spChDisplay.get_property("channel-id"))			# fixme: why needs ".new" ?
        self.remove(self.noneDisplay)
        self.add(self.display)
        self.display.show()
        self.state = FvpVmViewer.STATE_RUNNING
