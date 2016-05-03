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

    class HardwareInfo:
        qemuVmType = None                            # str        "pc", "q35"
        cpuArch = None                                # str
        cpuNumber = None                            # int
        memorySize = None                            # int        unit: MB
        mainDiskInterface = None                    # str        "virtio-blk" => "ide", '=>' means 'can fallback to'
        mainDiskFormat = None                        # str        "raw-sparse" => "qcow2"
        mainDiskSize = None                            # int        unit: MB
        graphicsAdapterInterface = None                # str        "qxl" => "vga"
        graphicsAdapterPciSlot = None                # int
        soundAdapterInterface = None                # str        "ac97" => ""
        soundAdapterPciSlot = None                    # int
        networkAdapterInterface = None                # str        "virtio" => "user" => ""
        networkAdapterPciSlot = None                # int
        balloonDeviceSupport = None                    # bool
        balloonDevicePciSlot = None                    # int
        vdiPortDeviceSupport = None                    # bool
        vdiPortDevicePciSlot = None                    # int
        shareDirectoryNumber = None                    # int
        shareDirectoryHotplugSupport = None            # bool
        shareUsbNumber = None                        # int
        shareUsbHotplugSupport = None                # bool
        shareScsiNumber = None                        # int
        shareScsiHotplugSupport = None                # bool

    hwInfo = HardwareInfo()

    def checkValid(self):
        """if FvmConfigHardware object is invalid, raise exception"""

        validQemuVmType = ["pc", "q35"]
        validArch = ["x86", "amd64"]
        validDiskInterface = ["virtio-blk", "ide"]
        validDiskFormat = ["raw-sparse", "qcow2"]
        validGraphicsAdapterInterface = ["qxl", "vga"]
        validSoundAdapterInterface = ["ac97", ""]
        validNetworkAdapterInterface = ["virtio", "user", ""]

        if self.hwInfo.qemuVmType is None or not isinstance(self.hwInfo.qemuVmType, str):
            raise Exception("qemuVmType is invalid")
        if self.hwInfo.qemuVmType not in validQemuVmType:
            raise Exception("qemuVmType is invalid")

        if self.hwInfo.cpuArch is None or not isinstance(self.hwInfo.cpuArch, str):
            raise Exception("cpuArch is invalid")
        if self.hwInfo.cpuArch not in validArch:
            raise Exception("cpuArch is invalid")

        if self.hwInfo.cpuNumber is None or not isinstance(self.hwInfo.cpuNumber, int):
            raise Exception("cpuNumber is invalid")
        if self.hwInfo.cpuNumber <= 0:
            raise Exception("cpuNumber is invalid")

        if self.hwInfo.memorySize is None or not isinstance(self.hwInfo.memorySize, int):
            raise Exception("memorySize is invalid")
        if self.hwInfo.memorySize <= 0:
            raise Exception("memorySize is invalid")

        if self.hwInfo.mainDiskInterface is None or not isinstance(self.hwInfo.mainDiskInterface, str):
            raise Exception("mainDiskInterface is invalid")
        if self.hwInfo.mainDiskInterface not in validDiskInterface:
            raise Exception("mainDiskInterface is invalid")

        if self.hwInfo.mainDiskFormat is None or not isinstance(self.hwInfo.mainDiskFormat, str):
            raise Exception("mainDiskFormat is invalid")
        if self.hwInfo.mainDiskFormat not in validDiskFormat:
            raise Exception("mainDiskFormat is invalid")

        if self.hwInfo.mainDiskSize is None or not isinstance(self.hwInfo.mainDiskSize, int):
            raise Exception("mainDiskSize is invalid")
        if self.hwInfo.mainDiskSize <= 0:
            raise Exception("mainDiskSize is invalid")

        if self.hwInfo.graphicsAdapterInterface is None or not isinstance(self.hwInfo.graphicsAdapterInterface, str):
            raise Exception("graphicsAdapterInterface is invalid")
        if self.hwInfo.graphicsAdapterInterface not in validGraphicsAdapterInterface:
            raise Exception("graphicsAdapterInterface is invalid")

        if self.hwInfo.graphicsAdapterPciSlot is None or not isinstance(self.hwInfo.graphicsAdapterPciSlot, int):
            raise Exception("graphicsAdapterPciSlot is invalid")

        if self.hwInfo.soundAdapterInterface is None or not isinstance(self.hwInfo.soundAdapterInterface, str):
            raise Exception("soundAdapterInterface is invalid")
        if self.hwInfo.soundAdapterInterface not in validSoundAdapterInterface:
            raise Exception("soundAdapterInterface is invalid")

        if self.hwInfo.soundAdapterInterface != "":
            if self.hwInfo.soundAdapterPciSlot is None or not isinstance(self.hwInfo.soundAdapterPciSlot, int):
                raise Exception("soundAdapterPciSlot is invalid")

        if self.hwInfo.networkAdapterInterface is None or not isinstance(self.hwInfo.networkAdapterInterface, str):
            raise Exception("networkAdapterInterface is invalid")
        if self.hwInfo.networkAdapterInterface not in validNetworkAdapterInterface:
            raise Exception("networkAdapterInterface is invalid")

        if self.hwInfo.networkAdapterInterface != "":
            if self.hwInfo.networkAdapterPciSlot is None or not isinstance(self.hwInfo.networkAdapterPciSlot, int):
                raise Exception("networkAdapterPciSlot is invalid")

        if self.hwInfo.balloonDeviceSupport is None or not isinstance(self.hwInfo.balloonDeviceSupport, bool):
            raise Exception("balloonDeviceSupport is invalid")

        if self.hwInfo.balloonDeviceSupport:
            if self.hwInfo.balloonDevicePciSlot is None or not isinstance(self.hwInfo.balloonDevicePciSlot, int):
                raise Exception("balloonDevicePciSlot is invalid")

        if self.hwInfo.vdiPortDeviceSupport is None or not isinstance(self.hwInfo.vdiPortDeviceSupport, bool):
            raise Exception("vdiPortDeviceSupport is invalid")

        if self.hwInfo.vdiPortDeviceSupport:
            if self.hwInfo.vdiPortDevicePciSlot is None or not isinstance(self.hwInfo.vdiPortDevicePciSlot, int):
                raise Exception("vdiPortDevicePciSlot is invalid")

        if self.hwInfo.shareDirectoryNumber is None or not isinstance(self.hwInfo.shareDirectoryNumber, int):
            raise Exception("shareDirectoryNumber is invalid")
        if self.hwInfo.shareDirectoryNumber < 0:
            raise Exception("shareDirectoryNumber is invalid")

        if self.hwInfo.shareDirectoryHotplugSupport is None or not isinstance(self.hwInfo.shareDirectoryHotplugSupport, bool):
            raise Exception("shareDirectoryHotplugSupport is invalid")

        if self.hwInfo.shareUsbNumber is None or not isinstance(self.hwInfo.shareUsbNumber, int):
            raise Exception("shareUsbNumber is invalid")
        if self.hwInfo.shareUsbNumber < 0:
            raise Exception("shareUsbNumber is invalid")

        if self.hwInfo.shareUsbHotplugSupport is None or not isinstance(self.hwInfo.shareUsbHotplugSupport, bool):
            raise Exception("shareUsbHotplugSupport is invalid")

        if self.hwInfo.shareScsiNumber is None or not isinstance(self.hwInfo.shareScsiNumber, int):
            raise Exception("shareScsiNumber is invalid")
        if self.hwInfo.shareScsiNumber < 0:
            raise Exception("shareScsiNumber is invalid")

        if self.hwInfo.shareScsiHotplugSupport is None or not isinstance(self.hwInfo.shareScsiHotplugSupport, bool):
            raise Exception("shareScsiHotplugSupport is invalid")

    def readFromDisk(self, vmDir):
        """read object from disk"""

        cfg = configparser.SafeConfigParser()
        cfg.read(os.path.join(vmDir, "fqemu.hw"))

        self.hwInfo.qemuVmType = cfg.get("hardware", "qemuVmType")
        self.hwInfo.cpuArch = cfg.get("hardware", "cpuArch")
        self.hwInfo.cpuNumber = cfg.getint("hardware", "cpuNumber")
        self.hwInfo.memorySize = cfg.getint("hardware", "memorySize")
        self.hwInfo.mainDiskInterface = cfg.get("hardware", "mainDiskInterface")
        self.hwInfo.mainDiskFormat = cfg.get("hardware", "mainDiskFormat")
        self.hwInfo.mainDiskSize = cfg.getint("hardware", "mainDiskSize")
        self.hwInfo.graphicsAdapterInterface = cfg.get("hardware", "graphicsAdapterInterface")
        self.hwInfo.graphicsAdapterPciSlot = cfg.getint("hardware", "graphicsAdapterPciSlot")
        self.hwInfo.soundAdapterInterface = cfg.get("hardware", "soundAdapterInterface")
        self.hwInfo.soundAdapterPciSlot = cfg.getint("hardware", "soundAdapterPciSlot")
        self.hwInfo.networkAdapterInterface = cfg.get("hardware", "networkAdapterInterface")
        self.hwInfo.networkAdapterPciSlot = cfg.getint("hardware", "networkAdapterPciSlot")
        self.hwInfo.balloonDeviceSupport = cfg.getboolean("hardware", "balloonDeviceSupport")
        self.hwInfo.balloonDevicePciSlot = cfg.getint("hardware", "balloonDevicePciSlot")
        self.hwInfo.vdiPortDeviceSupport = cfg.getboolean("hardware", "vdiPortDeviceSupport")
        self.hwInfo.vdiPortDevicePciSlot = cfg.getint("hardware", "vdiPortDevicePciSlot")
        self.hwInfo.shareDirectoryNumber = cfg.getint("hardware", "shareDirectoryNumber")
        self.hwInfo.shareDirectoryHotplugSupport = cfg.getboolean("hardware", "shareDirectoryHotplugSupport")
        self.hwInfo.shareUsbNumber = cfg.getint("hardware", "shareUsbNumber")
        self.hwInfo.shareUsbHotplugSupport = cfg.getboolean("hardware", "shareUsbHotplugSupport")
        self.hwInfo.shareScsiNumber = cfg.getint("hardware", "shareScsiNumber")
        self.hwInfo.shareScsiHotplugSupport = cfg.getboolean("hardware", "shareScsiHotplugSupport")


class FvpVmObject(GObject.GObject):

    """A virtual machine
       The real path (absolute path) of the virtual machine is the object key"""

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

        self.vmCfg = FvpVmConfig()
        self.vmCfg.readFromDisk(self.vmDir)
        self.vmCfg.checkValid()

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

        self.state = FvpVmObject.STATE_POWER_OFF

    def release(self):
        assert self.state == FvpVmObject.STATE_POWER_OFF
        assert len(self.peripheralDict) == 0
        self.elemObj.close()

    def getVmDir(self):
        return self.vmDir

    def getElemInfo(self):
        return self.elemObj.get_info()

    def getVmCfg(self):
        return self.vmCfg

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

            self.vmTmpDir = tempfile.mkdtemp(prefix="virt-player.vm.")

            self.vsVmResSetId = dbusObj.NewVmResSet(dbus_interface='org.fpemud.VirtService')
            resSetObj = dbus.SystemBus().get_object('org.fpemud.VirtService', '/org/fpemud/VirtService/%d/VmResSets/%d' % (os.getuid(), self.vsVmResSetId))
            if self.vmCfg.hwInfo.networkAdapterInterface == "virtio":
                # resSetObj.AddTapIntf(self.vmEnv.getVirtioNetworkType())
                resSetObj.AddTapIntf("nat")

            self.vsVmId = dbusObj.AttachVm(self.vmDir, self.vsVmResSetId)
            self.vsTapIfName = resSetObj.GetTapIntf()
            self.vsMacAddr = resSetObj.GetVmMacAddr()
            self.vsIpAddr = resSetObj.GetVmIpAddr()

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
            dbusObj.DetachVm(self.vsVmId)
            self.vsVmId = None

        if self.vsVmResSetId is not None:
            dbusObj.DeleteVmResSet(self.vsVmResSetId)
            self.vsVmResSetId = None

        if self.vmTmpDir is not None:
            shutil.rmtree(self.vmTmpDir)
            self.vmTmpDir = None

        self.maxDriveId = 0

        if not inException:
            self.state = FvpVmObject.STATE_POWER_OFF
            self.notify("state")

    def _generateQemuCommand(self):
        """pci slot allcation:
                slot 0x0.0x0:    host bridge
                slot 0x1.0x0:    ISA bridge
                slot 0x1.0x1;    IDE controller
                slot 0x1.0x2:    USB controller
                slot 0x2.0x0:    VGA controller
                slot 0x3.0x0:    SCSI controller, main-disk"""

        if self.vmCfg.hwInfo.qemuVmType == "pc":
            pciBus = "pci.0"
        elif self.vmCfg.hwInfo.qemuVmType == "q35":
            pciBus = "pcie.0"
        else:
            assert False

        cmd = "/usr/bin/qemu-system-x86_64"
        cmd += " -name \"%s\"" % (self.elemObj.get_info().get_name())
        cmd += " -enable-kvm"
        cmd += " -no-user-config"
        cmd += " -nodefaults"
        cmd += " -machine %s,usb=on" % (self.vmCfg.hwInfo.qemuVmType)

        # platform device
        cmd += " -cpu host"
        cmd += " -smp 1,sockets=1,cores=%d,threads=1" % (self.vmCfg.hwInfo.cpuNumber)
        cmd += " -m %d" % (self.vmCfg.hwInfo.memorySize)
        cmd += " -rtc base=localtime"

        # main-disk
        if True:
            if self.vmCfg.hwInfo.mainDiskFormat == "raw-sparse":
                cmd += " -drive \'file=%s,if=none,id=main-disk,format=%s\'" % (os.path.join(self.vmDir, "disk-main.img"), "raw")
            else:
                cmd += " -drive \'file=%s,if=none,id=main-disk,format=%s\'" % (os.path.join(self.vmDir, "disk-main.img"), "qcow2")
            if self.vmCfg.hwInfo.mainDiskInterface == "virtio-blk":
                cmd += " -device virtio-blk-pci,scsi=off,bus=%s,addr=0x03,drive=main-disk,id=main-disk,bootindex=1" % (pciBus)
            elif self.vmCfg.hwInfo.mainDiskInterface == "virtio-scsi":
                cmd += " -device virtio-blk-pci,scsi=off,bus=%s,addr=0x03,drive=main-disk,id=main-disk,bootindex=1" % (pciBus)        # fixme
            else:
                cmd += " -device ide-hd,bus=ide.0,unit=0,drive=main-disk,id=main-disk,bootindex=1"

        # graphics device
        if self.vmCfg.hwInfo.graphicsAdapterInterface == "qxl":
            assert self.spicePort != -1
            cmd += " -spice port=%d,addr=127.0.0.1,disable-ticketing,agent-mouse=off" % (self.spicePort)
            cmd += " -vga qxl -global qxl-vga.ram_size_mb=64 -global qxl-vga.vram_size_mb=64"
#            cmd += " -device qxl-vga,bus=%s,addr=0x04,ram_size_mb=64,vram_size_mb=64"%(pciBus)                        # see https://bugzilla.redhat.com/show_bug.cgi?id=915352
        else:
            assert self.spicePort != -1
            cmd += " -spice port=%d,addr=127.0.0.1,disable-ticketing,agent-mouse=off" % (self.spicePort)
            cmd += " -device VGA,bus=%s,addr=0x04" % (pciBus)

        # sound device
        if self.vmCfg.hwInfo.soundAdapterInterface == "ac97":
            cmd += " -device AC97,id=sound0,bus=%s,addr=0x%x" % (pciBus, self.vmCfg.hwInfo.soundAdapterPciSlot)

        # network device
        if self.vmCfg.hwInfo.networkAdapterInterface == "virtio":
            cmd += " -netdev tap,id=eth0,ifname=%s,script=no,downscript=no" % (self.vsTapIfName)
            cmd += " -device virtio-net-pci,netdev=eth0,mac=%s,bus=%s,addr=0x%x,romfile=" % (self.vsMacAddr, pciBus, self.vmCfg.hwInfo.networkAdapterPciSlot)
        elif self.vmCfg.hwInfo.networkAdapterInterface == "user":
            cmd += " -netdev user,id=eth0"
            cmd += " -device rtl8139,netdev=eth0,bus=%s,addr=0x%x,romfile=" % (pciBus, self.vmCfg.hwInfo.networkAdapterPciSlot)

        # balloon device
        if self.vmCfg.hwInfo.balloonDeviceSupport:
            cmd += " -device virtio-balloon-pci,id=balloon0,bus=%s,addr=0x%x" % (pciBus, self.vmCfg.hwInfo.balloonDevicePciSlot)

        # vdi-port
        if self.vmCfg.hwInfo.vdiPortDeviceSupport:
            cmd += " -device virtio-serial-pci,id=vdi-port,bus=%s,addr=0x%x" % (pciBus, self.vmCfg.hwInfo.vdiPortDevicePciSlot)

            # usb redirection
#            for i in range(0,self.vmCfg.hwInfo.shareUsbNumber):
#                cmd += " -chardev spicevmc,name=usbredir,id=usbredir%d"%(i)
#                cmd += " -device usb-redir,chardev=usbredir%d,id=usbredir%d"%(i,i)

            # vdagent
            cmd += " -chardev spicevmc,id=vdagent,debug=0,name=vdagent"
            cmd += " -device virtserialport,chardev=vdagent,name=com.redhat.spice.0"

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
            rsObj.NewSambaShare(pObj.pName, paPath, paReadonly)
            # fixme: let the vm map the network drive
        else:
            assert False

        # save peripheral
        self.peripheralDict[pObj.pName] = pObj

    def _removePeripheralFolder(self, pObj):
        if pObj.paramDict["dev-type"] == "network-share":
            rsObj = dbus.SystemBus().get_object('org.fpemud.VirtService', '/org/fpemud/VirtService/%d/VmResSets/%d' % (os.getuid(), self.vsVmResSetId))
            # fixme: let the vm unmap the network drive
            rsObj.DeleteSambaShare(pObj.pName)
        else:
            assert False

    def _paPathSubstitute(self, paPath):
        # fixme, its not complete
        return paPath.replace("%H", os.path.expanduser("~"))

GObject.type_register(FvpVmObject)
