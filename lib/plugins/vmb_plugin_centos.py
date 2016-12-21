#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import subprocess
import shutil


class LbVmbPlugin:

    def __init__(self):
        self.OS_CENTOS_6_X86 = "CentOS.6.X86"
        self.OS_CENTOS_6_AMD64 = "CentOS.6.X86_64"
        self.OS_CENTOS_7_X86 = "CentOS.7.X86"
        self.OS_CENTOS_7_AMD64 = "CentOS.7.X86_64"

        self.proc = None
        self.progress_callback = None

    def get_os_name_list(self):
        return [
            self.OS_CENTOS_6_X86,
            self.OS_CENTOS_6_AMD64,
            self.OS_CENTOS_7_X86,
            self.OS_CENTOS_7_AMD64,
        ]

    def create_setup_iso_async(self, tmp_dir, os_name, progress_callback):
        assert self.proc is None and self.errThread is None and self.dest is None

        isoFile = self._getIsoFile(os_name)
        if not os.path.exists(isoFile):
            raise Exception("File \"%s\" does not exist" % (isoFile))

        self.proc = multiprocessing.Process(target=self._createNewIso, args=(tmp_dir, os_name, isoFile, ))
        return self.proc.stdout

    def create_setup_iso_cancel(self):
        assert False

    def create_setup_iso_finish(self):
        assert False

    def update_vm_config(self, os_name, vm_config):
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

    def _getIsoFile(self, os_name):
        if os_name == self.OS_CENTOS_6_X86:
            assert False
        elif os_name == self.OS_CENTOS_6_AMD64:
            assert False
        elif os_name == self.OS_CENTOS_7_X86:
            assert False
        elif os_name == self.OS_CENTOS_7_AMD64:
            return "/usr/share/centos-7-setup-dvd/centos-7-dvd-amd64.iso"
        else:
            assert False

    def _createNewIso(self, tmp_dir, os_name, iso_file):
        dest = os.path.join(tmp_dir, "unattended.iso")
        isoDir = os.path.join(tmp_dir, "iso")

        print(">> Extracting \"%s\"" % (iso_file))
        if True:
            cmd = "/usr/bin/7z x \"%s\" -o\"%s\"" % (iso_file, isoDir)
            proc = subprocess.Popen(cmd, shell=True)
            proc.wait()

        print(">> Generating Kickstart file")
        if True:
            with open(os.path.join(isoDir, "ks.cfg"), "w") as f:
                f.write("")

            cmd = "/bin/sed -i \"s/append initrd=initrd.img/append initrd=initrd.img ks=cdrom:\/ks.cfg/g\" \"%s\"" % (os.path.join(isoDir, "isolinux/isolinux.cfg"))
            proc = subprocess.Popen(cmd, shell=True)
            proc.wait()

        print(">> Creating \"unattended.iso\"")
        if True:
            cmd = "/usr/bin/genisoimage -U -r -v -T -J -joliet-long -V \"RHEL-7\"" + \
                  " -volset \"RHEL-7\" -A \"RHEL-7\" -b isolinux/isolinux.bin -c isolinux/boot.cat" + \
                  " -no-emul-boot -boot-load-size 4 -boot-info-table -eltorito-alt-boot -e images/efiboot.img" + \
                  " -no-emul-boot -o \"%s\" \"%s\"" % (dest, isoDir)
            proc = subprocess.Popen(cmd, shell=True)
            proc.wait()

            # fixme
            shutil.rmtree(isoDir)


# genisoimage -U -r -v -T -J -joliet-long -V "RHEL-6" -volset "RHEL-6" -A "RHEL-6" -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -eltorito-alt-boot -e images/efiboot.img -no-emul-boot -o ../NEWISO.iso .
