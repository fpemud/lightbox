#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import threading
from fvp_util import FvpUtil
from fvp_vm_object import FvpVmObject


class FvpVmbPlugin:

    def get_os_name_list(self):
        pass

    def os_get_type(self, os_name):
        pass

    def os_create_setup_iso_async(self, tmp_dir, os_name):
        pass

    def os_create_setup_iso_cancel(self):
        pass

    def os_create_setup_iso_finish(self):
        pass


class FvpVmBuilder:

    def __init__(self, param):
        self.param = param
        self.thread = None

    def build_async(self, dstdir, vm_name, vm_description, os_name, params):
        try:
            # get plugin
            plugin = None
            for fn in os.listdir(os.path.join(self.param.libDir, "plugins")):
                if not fn.endswith(".py"):
                    continue
                fn = fn[:-3]
                exec("import %s" % (fn))
                plugin = eval("%s.Plugin()" % (fn))
                if os_name in plugin.get_os_name_list():
                    break
            if plugin is None:
                raise Exception("the specified operating system is not supported")

            # get os type
            os_type = eval("FvpVmObject.%s" % (plugin.os_get_type(os_name)))

            # start build thread
            self.thread = _BuildThread()
            self.thread.dstdir = dstdir
            self.thread.vm_name = vm_name
            self.thread.vm_description = vm_description
            self.thread.os_name = os_name
            self.thread.params = params
            self.thread.plugin = plugin
            self.thread.os_type = os_type
            self.thread.r_pipe, self.thread.w_pipe = os.pipe()
            self.thread.start()

            return self.thread.r_pipe
        except:
            if self.thread is not None:
                if hasattr(self.thread, "w_pipe"):
                    self.thread.w_pipe.close()
                if hasattr(self.thread, "r_pipe"):
                    self.thread.r_pipe.close()
            raise

    def build_cancel(self):
        try:
            self.thread.stop = True
            self.thread.join()
        finally:
            self.thread.r_pipe.close()
            self.thread = None

    def build_finish(self):
        try:
            self.thread.join()
        finally:
            self.thread.r_pipe.close()
            self.thread = None


class _BuildThread(threading.Thread):

    def __init__(self):
        super(_BuildThread, self).__init__()
        self.stop = False

    def run(self):
        try:
            if self.stop:
                return

            # create vm directory
            FvpUtil.mkDirAndClear()
            # -- element.ini

            if self.stop:
                return

            # create main disk
            with open(os.path.join(self.dstdir, "disk-main.img"), 'wb') as f:
                f.truncate(self._getMainDiskSizeByOs(self.os_type) * 1024 * 1024)

            if self.stop:
                return

            # create setup iso

            if self.stop:
                return

            # run setup

        finally:
            self.w_pipe.close()

    def _getMainDiskSizeByOs(self, os_type):
        if os_type == FvpVmObject.OS_MSWINXP_X86:
            return 10240                                    # 10GB
        elif os_type == FvpVmObject.OS_MSWIN7_X86:
            return 20480                                    # 20GB
        elif os_type == FvpVmObject.OS_MSWIN7_AMD64:
            return 20480                                    # 20GB
        elif os_type == FvpVmObject.OS_GENTOO_LINUX_X86:
            return 10240                                    # 10GB
        else:
            assert False
