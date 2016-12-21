#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import threading
from fvp_util import FvpUtil
from fvp_vm_object import FvpVmObject


class FvpVmBuilder:

    def __init__(self, param):
        self.param = param
        self.thread = None

    def build_async(self, dstdir, vm_name, vm_description, os_name, params, callback):
        # get plugin
        plugin = self.param.pluginManager.getVmbPlugin(os_name)
        if plugin is None:
            raise Exception("the specified operating system is not supported")

        # start build thread
        self.thread = _BuildThread()
        self.thread.dstdir = dstdir
        self.thread.vm_name = vm_name
        self.thread.vm_description = vm_description
        self.thread.os_name = os_name
        self.thread.params = params
        self.thread.callback = callback
        self.thread.vmb_plugin = plugin
        self.thread.vmr_plugin = self.param.pluginManager.getVmrPlugin(plugin.os_get_type(self.os_name))
        self.thread.start()

    def build_cancel(self):
        try:
            self.thread.stop = True
            self.thread.join()
        finally:
            self.thread = None

    def build_finish(self):
        try:
            self.thread.join()
        finally:
            self.thread = None


class _BuildThread(threading.Thread):

    def __init__(self):
        super(_BuildThread, self).__init__()
        self.stop = False

    def run(self):
        os_type = self.vmb_plugin.os_get_type(self.os_name)

        self.callback(0, "Creating virtual machine directory")
        FvpUtil.mkDirAndClear()
        if self.stop:
            return

        self.callback(0, "Creating virtual machine configuration file")
        if True:
            cfg = ConfigParser.SafeConfigParser()
            cfg.optionxform = str                                # make option names case-sensitive
            cfg.add_section("Element Entry")
            cfg.set("Element Entry", "Name", self.vm_name)
            cfg.set("Element Entry", "Comment", self.vm_description)
            cfg.set("Element Entry", "Type", "virtual-machine")
            with open(os.path.join(self.dstdir, "element.ini"), "w") as f:
                cfg.write(f)
        if True:
            cfg = ConfigParser.SafeConfigParser()
            cfg.set("main", "os_type", os_type)
            with open(os.path.join(self.dstdir, "lightbox.ini"), "w") as f:
                cfg.write(f)
            
        if self.stop:
            return

        # create main disk
        with open(os.path.join(self.dstdir, "disk-main.img"), 'wb') as f:
            f.truncate(self.vmr_plugin.get_main_disk_size(os_type) * 1000 * 1000)

        if self.stop:
            return

        # create setup iso
        pass
        
        if self.stop:
            return

        # run setup
        pass