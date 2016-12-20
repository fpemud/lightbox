#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

class LbVmrPlugin:

    def get_os_type_list(self):
        return [
            "MSWINXP_X86",
            "MSWIN7_X86",
            "MSWIN7_AMD64",
        ]

    def update_vm_config(self, os_type, vm_config):
        if os_type == "MSWINXP_X86":
            vm_config.qemuVmType = "pc"
            vm_config.cpuArch = "x86"
            vm_config.cpuNumber = 1
            vm_config.memorySize = 1024                       # 1GB
            vm_config.mainDiskInterface = "virtio-blk"
            vm_config.graphicsAdapterInterface = "qxl"
            vm_config.graphicsAdapterPciSlot = 7
            vm_config.soundAdapterInterface = "ac97"
            vm_config.soundAdapterPciSlot = 6
            vm_config.networkAdapterInterface = "virtio"
            vm_config.networkAdapterPciSlot = 5
            vm_config.balloonDeviceSupport = True
            vm_config.balloonDevicePciSlot = 4
            vm_config.vdiPortDeviceSupport = True
            vm_config.vdiPortDevicePciSlot = 3
        elif os_type == "MSWIN7_X86":
            vm_config.qemuVmType = "q35"
            vm_config.cpuArch = "x86"
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
        elif os_type == "MSWIN7_AMD64":
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
        else:
            assert False

    def get_main_disk_size(self, os_type):
        if os_type == "MSWINXP_X86":
            return 10000                                    # 10GB
        elif os_type == "MSWIN7_X86":
            return 20000                                    # 20GB
        elif os_type == "MSWIN7_AMD64":
            return 20000                                    # 20GB
        else:
            assert False
