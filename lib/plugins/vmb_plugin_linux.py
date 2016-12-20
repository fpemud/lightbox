#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class LbVmbPlugin:

    def __init__(self):
        self.OS_CENTOS_7_X86 = "CentOS.7.X86"
        self.OS_CENTOS_7_AMD64 = "CentOS.7.X86_64"

        self.proc = None
        self.errThread = None
        self.dest = None
        self.progress_callback = None

    def get_os_name_list(self):
        return [
            self.OS_CENTOS_7_X86,
            self.OS_CENTOS_7_AMD64,
        ]

    def os_create_setup_iso_async(self, tmp_dir, os_name, progress_callback):
        assert False

    def os_create_setup_iso_cancel(self):
        assert False

    def os_create_setup_iso_finish(self):
        assert False

    def os_update_vm_config(self, os_name, vm_config):
        vm_config.qemuVmType = "q35"
        vm_config.cpuArch = "amd64"
        vm_config.cpuNumber = 1
        vm_config.memorySize = 1024                       # 1GB
        vm_config.mainDiskInterface = "virtio-blk"
        vm_config.graphicsAdapterInterface = "vga"
        vm_config.graphicsAdapterPciSlot = 7
        vm_config.soundAdapterInterface = "ac97"
        vm_config.soundAdapterPciSlot = 6
        vm_config.networkAdapterInterface = "virtio"
        vm_config.networkAdapterPciSlot = 5
        vm_config.balloonDeviceSupport = True
        vm_config.balloonDevicePciSlot = 4
        vm_config.vdiPortDeviceSupport = True
        vm_config.vdiPortDevicePciSlot = 3

    def get_main_disk_size(self, os_name):
        return 10000                                        # 10GB
