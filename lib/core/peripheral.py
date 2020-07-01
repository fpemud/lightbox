#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class FvpPeripheral:

    """Peripheral can only be hot plugged after virtual machine starts."""
    """There's some types of device that cann't be used as peripheral:
         1. CPU: auto-allocate, no need to be a peripheral.
         2. memory: auto-allocate, no need to be a peripheral.
         3. network adapter: Windows recognizes network adapter by pci slot, so it can't be insert or pullout freely.
         4. graphics adapter: ??"""
    """Option path has variable substituions, these are:
         %H - the home directory of the current user"""

    _validTypeList = ["usb-dev",                                # DESCRIPTION: USB device, passthrough method
                                                                # PARAM:       "dev-id" = "8087:0024"
                                                                #              "dev-bus" = "001.002"
                                                                #              "dev-file" = "/dev/sdc"

                      "pci-dev",                                # DESCRIPTION: PCI device, passthrough access
                                                                # PARAM:       "host" = "0000:00:1b.0" | "00:1b.0"

                      "scsi-dev",                               # DESCRIPTION: SCSI device, passthrough access
                                                                # PARAM:

                      "block-dev",

                      "char-dev"

                      "usb-port",                               # DESCRIPTION: any USB device connected to this port will be belong to the VM
                                                                # PARAM:       "port" = "bus01.port2.port1"

                      "file",                                   # DESCRIPTION: used as usb-storage, cdrom or harddisk by VM
                                                                # PARAM:       "path" = "%H/my-cdrom.iso"
                                                                #              "dev-type" = "cdrom"
                                                                #              "readonly" = True | False

                      "folder",                                 # DESCRIPTION: used as usb-storage, harddisk or network-share by VM
                                                                # PARAM:       "path" = "%H/.gvfs/data"
                                                                #              "dev-type" = "network-share"
                                                                #              "readonly" = True | False
                      ]

    def __init__(self):
        self.pType = ""
        self.pName = ""
        self.paramDict = dict()

    def checkValid(self):
        """if FvpPeripheral object is invalid, raise exception"""

        if self.pType not in self._validTypeList:
            raise Exception("pType is invalid")
