#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

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

    def __init__(self):
        pass

    def build_async(self, os_name, dstdir, vm_name, vm_description, params):
        pass

    def build_cancel(self):
        pass

    def build_finish(self):
        pass

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
