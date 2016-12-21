#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os


class FvpParam:

    """Config directory structure:
         /etc/lightbox
           |--global.conf

       Virt-machine directory structure:
         [vmname]
               |--fqemu.cfg								config file
               |--disk-main.img							system disk image
               |--lock								lock file

       temp directory structure:
         /tmp/lightbox-[uid]-[vmname]
        |--qemu.log								log file
        |--qemu_monitor.log
        |--spice.log"""

    def __init__(self):
        self.uid = os.getuid()
        self.gid = os.getgid()
        self.pwd = os.getcwd()

        self.libDir = "/usr/lib/lightbox"
        self.tmpDir = None
        self.keepTmpDir = False

        self.macOuiVm = "00:50:02"
        self.mac4 = self.uid / 256
        self.mac5 = self.uid % 256

        self.spicePortStart = 5910
        self.spicePortEnd = 5999
        self.tapIdStart = 0
        self.tapIdEnd = 100

        self.pluginManager = None
