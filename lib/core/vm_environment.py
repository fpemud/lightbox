#!/usr/bin/python3.4
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import configparser
from core.util import FvpUtil
from core.peripheral import FvpPeripheral


class FvpVmEnvironment:

    class NetworkInfo:
        virtioNetworkType = None                    # str        "bridge", "nat", "route" => ""

    class PeripheralInfo:
        obj = None                                  # reference to FvpPeripheral object
        persistent = None                           # bool
        connectWhenStart = None                     # bool
        uiShortcut = None                           # bool

    def __init__(self):
        self.networkInfo = FvpVmEnvironment.NetworkInfo()
        self.peripheralInfoList = []

    def checkValid(self):
        """if FvpVmEnvironment object is invalid, raise exception"""

        validVirtioNetworkType = ["bridge", "nat", "route", ""]

        if self.networkInfo.virtioNetworkType is None or self.networkInfo.virtioNetworkType not in validVirtioNetworkType:
            raise Exception("virtioNetworkType is invalid")

        for p in self.peripheralInfoList:
            try:
                p.obj.checkValid()
            except Exception as e:
                raise Exception("peripheral \"%s\" is invalid, %s" % (p.obj.pName, e.strerror))

    def getVirtioNetworkType(self):
        return self.networkInfo.virtioNetworkType

    def addPeripheral(self, peripheralObj, persistent, connectWhenStart, uiShortcut):
        # forbid name duplication
        for pInfo in self.peripheralInfoList:
            assert pInfo.obj.pName != peripheralObj.pName

        # add data
        pInfo = self.PeripheralInfo()
        pInfo.obj = peripheralObj
        pInfo.persistent = persistent
        pInfo.connectWhenStart = connectWhenStart
        pInfo.uiShortcut = uiShortcut
        self.peripheralInfoList.append(pInfo)

    def getPeripheralList(self):
        return self.peripheralInfoList

#    def remove(self, peripheralName):
#        pass
#
#
#    def getObj(self, peripheralName):
#        return self.objDict[peripheralName]
#
#    def setPersistent(self, peripheralName, flag):
#        self.infoDict[peripheralName].persistent = flag
#
#    def isPersistent(self, peripheralName):
#        return self.infoDict[peripheralName].persistent
#
#    def setConnectWhenStart(self, peripheralName, flag):
#        self.infoDict[peripheralName].connectWhenStart = flag
#
#    def isConnectWhenStart(self, peripheralName):
#        return self.infoDict[peripheralName].connectWhenStart

    def load(self, vmDir):
        fileName = os.path.join(vmDir, "fqemu.env")

        # clear self
        self.networkInfo.virtioNetworkType = ""
        self.peripheralInfoList = []

        # check file
        if not os.path.exists(fileName):
            return

        # read from cfg file
        cfg = configparser.RawConfigParser()
        cfg.read(os.path.join(vmDir, "fqemu.env"))

        self.networkInfo.virtioNetworkType = cfg.get("networkInfo", "virtioNetworkType")

        for secName in cfg.sections():
            if secName.startswith("peripheral"):
                p = FvpVmEnvironment.PeripheralInfo()

                p.obj = FvpPeripheral()
                p.obj.pType = cfg.get(secName, "pType")
                p.obj.pName = cfg.get(secName, "pName")
                for (name, value) in cfg.items(secName):
                    if name.startswith("param_"):
                        p.obj.paramDict[name[6:]] = value

                p.connectWhenStart = bool(cfg.get(secName, "connectWhenStart"))
                p.uiShortcut = False                                                    # fixme
                p.persistent = True

                self.peripheralInfoList.append(p)

        # type conversion
        for p in self.peripheralInfoList:
            if p.obj.pType == "file":
                if "readonly" in p.obj.paramDict:
                    p.obj.paramDict["readonly"] = FvpUtil.str2bool(p.obj.paramDict["readonly"])
            elif p.obj.pType == "folder":
                if "readonly" in p.obj.paramDict:
                    p.obj.paramDict["readonly"] = FvpUtil.str2bool(p.obj.paramDict["readonly"])

    def save(self, vmDir):
        fileName = os.path.join(vmDir, "fqemu.env")

        # save config file
        cfg = configparser.RawConfigParser()

        # save network parameter
        cfg.add_section("networkInfo")
        cfg.set("networkInfo", "virtioNetworkType", self.networkInfo.virtioNetworkType)

        # save peripheral list
        i = 0
        for p in self.peripheralInfoList:
            if not p.persistent:
                continue
            secName = "peripheral%d" % (i)
            cfg.add_section(secName)
            cfg.set(secName, "pType", p.obj.pType)
            cfg.set(secName, "pName", p.obj.pName)
            for k, v in p.paramDict:
                cfg.set(secName, "param_%s" % (k), str(v))
            cfg.set(secName, "connectWhenStart", str(p.connectWhenStart))
            i = i + 1

        cfg.write(open(fileName, "w"))
