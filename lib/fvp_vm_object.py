#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import re
import dbus
import time
import copy
import shutil
import tempfile
import elemlib
import configparser
import qmp
from gi.repository import GObject
from gi.repository import GLib
from fvp_util import FvpUtil


class FvpVmConfig:

    def __init__(self):
        self.qemuVmType = None                            # str        "pc", "q35"
        self.cpuArch = None                                # str
        self.cpuNumber = None                            # int
        self.memorySize = None                            # int        unit: MB
        self.mainDiskInterface = None                    # str        "virtio-blk" => "ide", '=>' means 'can fallback to'
        self.graphicsAdapterInterface = None                # str        "qxl" => "vga"
        self.graphicsAdapterPciSlot = None                # int
        self.soundAdapterInterface = None                # str        "ac97" => ""
        self.soundAdapterPciSlot = None                    # int
        self.networkAdapterInterface = None                # str        "virtio" => "user" => ""
        self.networkAdapterPciSlot = None                # int
        self.balloonDeviceSupport = None                    # bool
        self.balloonDevicePciSlot = None                    # int
        self.vdiPortDeviceSupport = None                    # bool
        self.vdiPortDevicePciSlot = None                    # int
        self.shareDirectoryNumber = None                    # int
        self.shareDirectoryHotplugSupport = None            # bool
        self.shareUsbNumber = None                        # int
        self.shareUsbHotplugSupport = None                # bool
        self.shareScsiNumber = None                        # int
        self.shareScsiHotplugSupport = None                # bool


class FvpVmObject(GObject.GObject):
    """A virtual machine
       The real path (absolute path) of the virtual machine is the object key"""

    OS_MIN = 1
    OS_MSWINXP_X86 = 1
    OS_MSWIN7_X86 = 2
    OS_MSWIN7_AMD64 = 3
    OS_GENTOO_LINUX_X86 = 4
    OS_MAX = 4

    STATE_MIN = 1
    STATE_POWER_OFF = 1
    STATE_POWER_ON = 2
    STATE_MAX = 2

    __gproperties__ = {
        'state': (GObject.TYPE_INT,                         # type
                  'state',                                  # nick name
                  'state of the virtual machine',           # description
                  STATE_MIN,                                # minimum value
                  STATE_MAX,                                # maximum value
                  STATE_MIN,                                # default value
                  GObject.PARAM_READABLE),                  # flags
    }

    def __init__(self, param, vmDir):
        GObject.GObject.__init__(self)

        self.param = param
        self.vmDir = os.path.realpath(vmDir)

        try:
            self.elemObj = elemlib.open_element(self.vmDir, "rw")
        except elemlib.ElementAccessError as e:
            e.message = "The specified virtual machine has been already opened by another program."
            raise e

        self.os_type = None
        if True:
            cfg = configparser.SafeConfigParser()
            cfg.read(os.path.join(vmDir, "lightbox.ini"))
            ret = cfg.get("main", "os_type")
            if not ret.startswith("OS_") or not hasattr(FvpVmObject, ret):
                raise Exception("The specified virtual machine has an invalid operating system")
            self.os_type = getattr(FvpVmObject, ret)

        self.peripheralDict = dict()

        self.qmpPort = -1
        self.qmpObj = None

        self.spicePort = -1

        self.vmPid = None
        self.vmPidWatch = None

        self.vmTmpDir = None

        self.vsVmResSetId = None
        self.vsVmId = None
        self.vsTapIfName = None
        self.vsMacAddr = None
        self.vsIpAddr = None

        self.maxDriveId = 0

        self.vmCfg = self._getVmCfgByOs()
        self.state = FvpVmObject.STATE_POWER_OFF

    def release(self):
        assert self.state == FvpVmObject.STATE_POWER_OFF
        assert len(self.peripheralDict) == 0
        self.elemObj.close()

    def getVmDir(self):
        return self.vmDir

    def getElemInfo(self):
        return self.elemObj.get_info()

    def getSpicePort(self):
        assert self.spicePort != -1
        return self.spicePort

    def powerButtonClicked(self):
        if self.state == FvpVmObject.STATE_POWER_ON:
            self.qmpObj.cmd_quit()
        elif self.state == FvpVmObject.STATE_POWER_OFF:
            self._vmUpOperation()
        else:
            assert False

    def resetButtonClicked(self):
        if self.state == FvpVmObject.STATE_POWER_ON:
            self.qmpObj.cmd_system_reset()
        elif self.state == FvpVmObject.STATE_POWER_OFF:
            pass
        else:
            assert False

    def powerDown(self):
        if self.state == FvpVmObject.STATE_POWER_ON:
            GLib.source_remove(self.vmPidWatch)
            self.vmPidWatch = None
            self.qmpObj.cmd_quit()
            os.waitpid(self.vmPid, 0)
            self.vmPid = None
            self._vmDownOperation()
        elif self.state == FvpVmObject.STATE_POWER_OFF:
            pass
        else:
            assert False

    def addPeripheral(self, peripheralObj):
        """need to put some new property in peripheralObj, so copy it first
           the add operation is done in sub functions"""

        assert peripheralObj.pName not in self.peripheralDict

        peripheralObj = copy.deepcopy(peripheralObj)

        if peripheralObj.pType == "usb-dev":
            assert False
        elif peripheralObj.pType == "pci-dev":
            assert False
        elif peripheralObj.pType == "scsi-dev":
            assert False
        elif peripheralObj.pType == "block-dev":
            assert False
        elif peripheralObj.pType == "char-dev":
            assert False
        elif peripheralObj.pType == "usb-port":
            self._addPeripheralUsbPort(peripheralObj)
        elif peripheralObj.pType == "file":
            self._addPeripheralFile(peripheralObj)
        elif peripheralObj.pType == "folder":
            self._addPeripheralFolder(peripheralObj)
        else:
            assert False

    def removePeripheral(self, peripheralName):
        """the del operation is this function"""

        peripheralObj = self.peripheralDict[peripheralName]

        if peripheralObj.pType == "usb-dev":
            assert False
        elif peripheralObj.pType == "pci-dev":
            assert False
        elif peripheralObj.pType == "scsi-dev":
            assert False
        elif peripheralObj.pType == "block-dev":
            assert False
        elif peripheralObj.pType == "char-dev":
            assert False
        elif peripheralObj.pType == "usb-port":
            self._removePeripheralUsbPort(peripheralObj)
        elif peripheralObj.pType == "file":
            self._removePeripheralFile(peripheralObj)
        elif peripheralObj.pType == "folder":
            self._removePeripheralFolder(peripheralObj)
        else:
            assert False

        # delete object here
        del self.peripheralDict[peripheralName]

    def getPeripheralList(self):
        return self.peripheralDict.keys()

    def isPeripheralConnected(self, peripheralName):
        return (peripheralName in self.peripheralDict)

    def do_get_property(self, prop):
        if prop.name == 'state':
            return self.state
        else:
            raise AttributeError('unknown property %s' % prop.name)

    def onVmExit(self, pid, condition):
        assert self.vmPid is not None and pid == self.vmPid
        self.vmPid = None
        self._vmDownOperation()

    def _vmUpOperation(self):
        assert self.vmPid is None

        dbusObj = dbus.SystemBus().get_object('org.fpemud.VirtService', '/org/fpemud/VirtService')
        try:
            self.maxDriveId = 0

            self.vmTmpDir = tempfile.mkdtemp(prefix="lightbox.vm.")

            self.vsVmResSetId = dbusObj.NewVmResSet(dbus_interface='org.fpemud.VirtService')
            resSetObj = dbus.SystemBus().get_object('org.fpemud.VirtService', '/org/fpemud/VirtService/%d/VmResSets/%d' % (os.getuid(), self.vsVmResSetId))
            if self.vmCfg.networkAdapterInterface == "virtio":
                # resSetObj.AddTapIntf(self.vmEnv.getVirtioNetworkType())
                resSetObj.AddTapIntf("nat", dbus_interface='org.fpemud.VirtService.VmResSet')

            self.vsVmId = dbusObj.AttachVm(self.vmDir, self.vsVmResSetId, dbus_interface='org.fpemud.VirtService')
            self.vsTapIfName = resSetObj.GetTapIntf(dbus_interface='org.fpemud.VirtService.VmResSet')
            self.vsMacAddr = resSetObj.GetVmMacAddr(dbus_interface='org.fpemud.VirtService.VmResSet')
            self.vsIpAddr = resSetObj.GetVmIpAddr(dbus_interface='org.fpemud.VirtService.VmResSet')

            self.spicePort = FvpUtil.getFreeSocketPort("tcp", self.param.spicePortStart, self.param.spicePortEnd)
            self.qmpPort = FvpUtil.getFreeSocketPort("tcp")

            qemuCmd = self._generateQemuCommand()

            mycwd = os.getcwd()
            os.chdir(self.vmDir)
            try:
                targc, targv = GLib.shell_parse_argv(qemuCmd)
                ret = GLib.spawn_async(targv, flags=GLib.SpawnFlags.DO_NOT_REAP_CHILD)
                self.vmPid = ret[0]
                self.vmPidWatch = GLib.child_watch_add(self.vmPid, self.onVmExit)
                time.sleep(1)                        # fixme: should change fvp_vm_view, repeat connect
            finally:
                os.chdir(mycwd)

            self.qmpObj = qmp.QmpClient()
            self.qmpObj.connect_tcp("127.0.0.1", self.qmpPort)

            self.state = FvpVmObject.STATE_POWER_ON
            self.notify("state")
        except:
            self._vmDownOperation(True, dbusObj)
            raise

    def _vmDownOperation(self, inException=False, dbusObj=None):
        if not inException:
            dbusObj = dbus.SystemBus().get_object('org.fpemud.VirtService', '/org/fpemud/VirtService')
        else:
            assert dbusObj is not None

        self.peripheralDict.clear()

        if self.qmpObj is not None:
            self.qmpObj.close()
            self.qmpObj = None

        if self.vmPidWatch is not None:
            self.vmPidWatch = GLib.source_remove(self.vmPidWatch)
        if self.vmPid is not None:
            GLib.spawn_close_pid(self.vmPid)
            self.vmPid = None

        self.qmpPort = -1
        self.spicePort = -1

        self.vsIpAddr = None
        self.vsMacAddr = None
        self.vsTapIfName = None

        if self.vsVmId is not None:
            dbusObj.DetachVm(self.vsVmId, dbus_interface='org.fpemud.VirtService')
            self.vsVmId = None

        if self.vsVmResSetId is not None:
            dbusObj.DeleteVmResSet(self.vsVmResSetId, dbus_interface='org.fpemud.VirtService')
            self.vsVmResSetId = None

        if self.vmTmpDir is not None:
            shutil.rmtree(self.vmTmpDir)
            self.vmTmpDir = None

        self.maxDriveId = 0

        if not inException:
            self.state = FvpVmObject.STATE_POWER_OFF
            self.notify("state")

    def _getVmCfgByOs(self):
        ret = FvpVmConfig()

        if self.os_type == self.OS_MSWINXP_X86:
            ret.qemuVmType = "pc"
            ret.cpuArch = "x86"
            ret.cpuNumber = 1
            ret.memorySize = 1024                       # 1GB
            ret.mainDiskInterface = "virtio-blk"
            ret.graphicsAdapterInterface = "qxl"
            ret.graphicsAdapterPciSlot = 7
            ret.soundAdapterInterface = "ac97"
            ret.soundAdapterPciSlot = 6
            ret.networkAdapterInterface = "virtio"
            ret.networkAdapterPciSlot = 5
            ret.balloonDeviceSupport = True
            ret.balloonDevicePciSlot = 4
            ret.vdiPortDeviceSupport = True
            ret.vdiPortDevicePciSlot = 3
        elif self.os_type == self.OS_MSWIN7_X86:
            ret.qemuVmType = "q35"
            ret.cpuArch = "x86"
            ret.cpuNumber = 1
            ret.memorySize = 1024                       # 1GB
            ret.mainDiskInterface = "virtio-blk"
            ret.graphicsAdapterInterface = "vga"
            ret.graphicsAdapterPciSlot = 7
            ret.soundAdapterInterface = "ac97"
            ret.soundAdapterPciSlot = 6
            ret.networkAdapterInterface = "virtio"
            ret.networkAdapterPciSlot = 5
            ret.balloonDeviceSupport = True
            ret.balloonDevicePciSlot = 4
            ret.vdiPortDeviceSupport = True
            ret.vdiPortDevicePciSlot = 3
        elif self.os_type == self.OS_MSWIN7_AMD64:
            ret.qemuVmType = "q35"
            ret.cpuArch = "amd64"
            ret.cpuNumber = 1
            ret.memorySize = 1024                       # 1GB
            ret.mainDiskInterface = "virtio-blk"
            ret.graphicsAdapterInterface = "vga"
            ret.graphicsAdapterPciSlot = 7
            ret.soundAdapterInterface = "ac97"
            ret.soundAdapterPciSlot = 6
            ret.networkAdapterInterface = "virtio"
            ret.networkAdapterPciSlot = 5
            ret.balloonDeviceSupport = True
            ret.balloonDevicePciSlot = 4
            ret.vdiPortDeviceSupport = True
            ret.vdiPortDevicePciSlot = 3
        elif self.os_type == self.OS_GENTOO_LINUX_X86:
            ret.qemuVmType = "q35"
            ret.cpuArch = "amd64"
            ret.cpuNumber = 1
            ret.memorySize = 1024                       # 1GB
            ret.mainDiskInterface = "virtio-blk"
            ret.graphicsAdapterInterface = "vga"
            ret.graphicsAdapterPciSlot = 7
            ret.soundAdapterInterface = "ac97"
            ret.soundAdapterPciSlot = 6
            ret.networkAdapterInterface = "virtio"
            ret.networkAdapterPciSlot = 5
            ret.balloonDeviceSupport = True
            ret.balloonDevicePciSlot = 4
            ret.vdiPortDeviceSupport = True
            ret.vdiPortDevicePciSlot = 3
        else:
            assert False

        return ret

    def _generateQemuCommand(self):
        """pci slot allcation:
                slot 0x0.0x0:    host bridge
                slot 0x1.0x0:    ISA bridge
                slot 0x1.0x1;    IDE controller
                slot 0x1.0x2:    USB controller
                slot 0x2.0x0:    VGA controller
                slot 0x3.0x0:    SCSI controller, main-disk"""

        if self.vmCfg.qemuVmType == "pc":
            pciBus = "pci.0"
            pciSlot = 3
        elif self.vmCfg.qemuVmType == "q35":
            pciBus = "pcie.0"
            pciSlot = 3
        else:
            assert False

        cmd = "/usr/bin/qemu-system-x86_64"
        cmd += " -name \"%s\"" % (self.elemObj.get_info().get_name())
        cmd += " -enable-kvm"
        cmd += " -no-user-config"
        cmd += " -nodefaults"
        cmd += " -machine %s,usb=on" % (self.vmCfg.qemuVmType)

        # platform device
        cmd += " -cpu host"
        cmd += " -smp 1,sockets=1,cores=%d,threads=1" % (self.vmCfg.cpuNumber)
        cmd += " -m %d" % (self.vmCfg.memorySize)
        cmd += " -rtc base=localtime"

        # main-disk
        if True:
            cmd += " -drive \'file=%s,if=none,id=main-disk,format=%s\'" % (os.path.join(self.vmDir, "disk-main.img"), "raw")
            if self.vmCfg.mainDiskInterface == "virtio-blk":
                cmd += " -device virtio-blk-pci,scsi=off,bus=%s,addr=0x%02x,drive=main-disk,id=main-disk,bootindex=1" % (pciBus, pciSlot)
            elif self.vmCfg.mainDiskInterface == "virtio-scsi":
                cmd += " -device virtio-blk-pci,scsi=off,bus=%s,addr=0x%02x,drive=main-disk,id=main-disk,bootindex=1" % (pciBus, pciSlot)        # fixme
            else:
                cmd += " -device ide-hd,bus=ide.0,unit=0,drive=main-disk,id=main-disk,bootindex=1"
            pciSlot += 1

        # graphics device
        if True:
            if self.vmCfg.graphicsAdapterInterface == "qxl":
                assert self.spicePort != -1
                cmd += " -spice port=%d,addr=127.0.0.1,disable-ticketing,agent-mouse=off" % (self.spicePort)
                cmd += " -vga qxl -global qxl-vga.ram_size_mb=64 -global qxl-vga.vram_size_mb=64"
    #            cmd += " -device qxl-vga,bus=%s,addr=0x04,ram_size_mb=64,vram_size_mb=64"%(pciBus)                        # see https://bugzilla.redhat.com/show_bug.cgi?id=915352
            else:
                assert self.spicePort != -1
                cmd += " -spice port=%d,addr=127.0.0.1,disable-ticketing,agent-mouse=off" % (self.spicePort)
                cmd += " -device VGA,bus=%s,addr=0x%02x" % (pciBus, pciSlot)
            pciSlot += 1

        # sound device
        if self.vmCfg.soundAdapterInterface == "ac97":
            cmd += " -device AC97,id=sound0,bus=%s,addr=0x%02x" % (pciBus, pciSlot)
            pciSlot += 1

        # network device
        if True:
            if self.vmCfg.networkAdapterInterface == "virtio":
                cmd += " -netdev tap,id=eth0,ifname=%s,script=no,downscript=no" % (self.vsTapIfName)
                cmd += " -device virtio-net-pci,netdev=eth0,mac=%s,bus=%s,addr=0x%02x,romfile=" % (self.vsMacAddr, pciBus, pciSlot)
            elif self.vmCfg.networkAdapterInterface == "user":
                cmd += " -netdev user,id=eth0"
                cmd += " -device rtl8139,netdev=eth0,bus=%s,addr=0x%02x,romfile=" % (pciBus, pciSlot)
            pciSlot += 1

        # balloon device
        if self.vmCfg.balloonDeviceSupport:
            cmd += " -device virtio-balloon-pci,id=balloon0,bus=%s,addr=0x%02x" % (pciBus, pciSlot)
            pciSlot += 1

        # vdi-port
        if self.vmCfg.vdiPortDeviceSupport:
            cmd += " -device virtio-serial-pci,id=vdi-port,bus=%s,addr=0x%02x" % (pciBus, pciSlot)

            # usb redirection
#            for i in range(0,self.vmCfg.shareUsbNumber):
#                cmd += " -chardev spicevmc,name=usbredir,id=usbredir%d"%(i)
#                cmd += " -device usb-redir,chardev=usbredir%d,id=usbredir%d"%(i,i)

            # vdagent
            cmd += " -chardev spicevmc,id=vdagent,debug=0,name=vdagent"
            cmd += " -device virtserialport,chardev=vdagent,name=com.redhat.spice.0"
            pciSlot += 1

        # monitor interface
        if True:
            assert self.qmpPort != -1
            cmd += " -qmp \"tcp:127.0.0.1:%d,server,nowait\"" % (self.qmpPort)

        return cmd

    def _addPeripheralUsbDev(self, pObj):
        assert False

#        # do job
#        if "dev-id" in pObj.paramDict:
#            ret = self._execQemuMonitorCmd("usb_add \"host:%s\""%(pObj.paramDict["dev-id"]))
#        elif "dev-bus" in pObj.paramDict:
#            ret = self._execQemuMonitorCmd("usb_add \"host:%s\""%(pObj.paramDict["dev-bus"]))
#        elif "dev-file" in pObj.paramDict:
#            realPath = os.realpath(pObj.paramDict["dev-file"]
#        else:
#            assert False
#
#        if ret != "":
#            raise Exception("failed to plug in peripheral \"%s\""%(pObj.pName))
#
#        # get bus.addr of usb device in guest

    def _removePeripheralUsbDev(self, pObj):
        assert False

    def _addPeripheralPciDev(self, pObj):
        assert False

    def _removePeripheralPciDev(self, pObj):
        assert False

    def _addPeripheralUsbPort(self, pObj):
        assert False

    def _removePeripheralUsbPort(self, pObj):
        assert False

    def _addPeripheralFile(self, pObj):
        # get parameter
        paPath = self._paPathSubstitute(pObj.paramDict["path"])
        paDevType = pObj.paramDict["dev-type"]

        # check parameter
        if not (os.path.isfile(paPath) or os.stat(paPath).st_dev == 6):       # fixme, why == 6 ?
            raise Exception("invalid peripheral \"%s\", parameter \"path\" does not exist" % (pObj.pName))
        if paDevType not in ["usb-storage", "cdrom", "harddisk"]:
            raise Exception("invalid peripheral \"%s\", parameter \"dev-type\" illegal" % (pObj.pName))

        # do job
        if paDevType == "usb-storage":
            self.maxDriveId += 1
            try:
                self.qmpObj.cmd_blockdev_add("raw", "drive%d" % (self.maxDriveId), paPath)
                self.qmpObj.cmd_device_add("usb-storage", "drive%d" % (self.maxDriveId))
            except qmp.QmpCmdError as e:
                # fixme: should do blockdev_del
                raise Exception("failed to plug in peripheral \"%s\", %s" % (pObj.pName, e.message))
        elif paDevType in ["cdrom", "harddisk"]:
            if paDevType == "cdrom":
                ret = self._execQemuMonitorCmd("pci_add auto storage file=%s,if=scsi,media=cdrom" % (paPath))        # fixme: i think should use \"%s\", but ...
            else:
                ret = self._execQemuMonitorCmd("pci_add auto storage file=%s,if=virtio" % (paPath))                # fixme: i think should use \"%s\", but ...

            m = re.match("^OK domain ([0-9]+), bus ([0-9]+), slot ([0-9]+), function ([0-9]+)$", ret)
            if m is None:
                raise Exception("failed to plug in peripheral \"%s\"" % (pObj.pName))

            pObj._Domain = int(m.group(1))
            pObj._Bus = int(m.group(2))
            pObj._Slot = int(m.group(3))
            pObj._Function = int(m.group(4))
            assert int(pObj._Domain) == 0 and int(pObj._Function) == 0

        else:
            assert False

        # save peripheral
        self.peripheralDict[pObj.pName] = pObj

    def _removePeripheralFile(self, pObj):
        if pObj.paramDict["dev-type"] == "usb-storage":
            assert False
        elif pObj.paramDict["dev-type"] in ["cdrom", "harddisk"]:
            self._execQemuMonitorCmd("pci_del %d:%d" % (pObj._Bus, pObj._Slot))
        else:
            assert False

    def _addPeripheralFolder(self, pObj):
        # get parameter
        paPath = self._paPathSubstitute(pObj.paramDict["path"])
        paDevType = pObj.paramDict["dev-type"]
        paReadonly = ("readonly" in pObj.paramDict and pObj.paramDict["readonly"])

        # check parameter
        if not os.path.isdir(paPath):
            raise Exception("invalid peripheral \"%s\", the directory specified by parameter \"path\" does not exist" % (pObj.pName))
        if paDevType not in ["network-share"]:
            raise Exception("invalid peripheral \"%s\", parameter \"dev-type\" illegal" % (pObj.pName))

        # do job
        if paDevType == "network-share":
            rsObj = dbus.SystemBus().get_object('org.fpemud.VirtService', '/org/fpemud/VirtService/%d/VmResSets/%d' % (os.getuid(), self.vsVmResSetId))
            rsObj.NewSambaShare(pObj.pName, paPath, paReadonly, dbus_interface='org.fpemud.VirtService.VmResSet')
            # fixme: let the vm map the network drive
        else:
            assert False

        # save peripheral
        self.peripheralDict[pObj.pName] = pObj

    def _removePeripheralFolder(self, pObj):
        if pObj.paramDict["dev-type"] == "network-share":
            rsObj = dbus.SystemBus().get_object('org.fpemud.VirtService', '/org/fpemud/VirtService/%d/VmResSets/%d' % (os.getuid(), self.vsVmResSetId))
            # fixme: let the vm unmap the network drive
            rsObj.DeleteSambaShare(pObj.pName, dbus_interface='org.fpemud.VirtService.VmResSet')
        else:
            assert False

    def _paPathSubstitute(self, paPath):
        # fixme, its not complete
        return paPath.replace("%H", os.path.expanduser("~"))

GObject.type_register(FvpVmObject)
