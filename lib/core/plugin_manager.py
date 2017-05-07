#!/usr/bin/python3.4
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os


class FvpVmbPlugin:

    """Virtual machine builder plugin"""

    def get_os_name_list(self):
        pass

    def get_os_icon(self, os_name):
        pass

    def create_setup_iso_async(self, tmp_dir, os_name, progress_callback):
        pass

    def create_setup_iso_cancel(self):
        pass

    def create_setup_iso_finish(self):
        pass

    def update_vm_config(self, os_name, vm_config):
        pass

    def get_main_disk_size(self, os_name):
        pass


class FvpPluginManager:

    def __init__(self, param):
        self.param = param

    def getPluginList(self):
        ret = []
        for fn in os.listdir(os.path.join(self.param.libDir, "plugins")):
            if not fn.startswith("vmb_plugin_") or not fn.endswith(".py"):
                continue
            fn = fn[:-3]
            exec("from plugins import %s" % (fn))
            plugin = eval("%s.LbVmbPlugin()" % (fn))
            ret.append(plugin)
        return ret

    def getPlugin(self, os_name):
        for fn in os.listdir(os.path.join(self.param.libDir, "plugins")):
            if not fn.startswith("vmb_plugin_") or not fn.endswith(".py"):
                continue
            fn = fn[:-3]
            exec("from plugins import %s" % (fn))
            plugin = eval("%s.LbVmbPlugin()" % (fn))
            if os_name in plugin.get_os_name_list():
                return plugin
        return None
