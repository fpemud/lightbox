#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import threading
import configparser
from fvp_util import FvpUtil


class FvpVmBuilder:

    def __init__(self, param):
        self.param = param
        self.thread = None

    def build_async(self, dstdir, vm_name, vm_description, os_name, params, callback):
        # get plugin
        plugin = self.param.pluginManager.getPlugin(os_name)
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
        self.thread.plugin = plugin
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
        self.callback(0, "Creating virtual machine directory")
        FvpUtil.mkDirAndClear()
        if self.stop:
            return

        self.callback(0, "Creating virtual machine configuration file")
        if True:
            cfg = configparser.SafeConfigParser()
            cfg.optionxform = str                                # make option names case-sensitive
            cfg.add_section("Element Entry")
            cfg.set("Element Entry", "Name", self.vm_name)
            cfg.set("Element Entry", "Comment", self.vm_description)
            cfg.set("Element Entry", "Type", "virtual-machine")
            with open(os.path.join(self.dstdir, "element.ini"), "w") as f:
                cfg.write(f)
        if True:
            cfg = configparser.SafeConfigParser()
            cfg.set("main", "os_name", self.os_name)
            with open(os.path.join(self.dstdir, "lightbox.ini"), "w") as f:
                cfg.write(f)

        if self.stop:
            return

        # create main disk
        with open(os.path.join(self.dstdir, "disk-main.img"), 'wb') as f:
            f.truncate(self.plugin.get_main_disk_size(self.os_name) * 1000 * 1000)

        if self.stop:
            return

        # create setup iso
        pass

        if self.stop:
            return

        # run setup
        pass
