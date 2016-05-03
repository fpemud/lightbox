#!/usr/bin/python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class VmbPluginFpemudUmake:
    
    def getOsList(self):
        osList = self._shell("/usr/bin/fpemud-umake --os '?'").split("\n")
        return osList
        
    def buildSetupIso(self, tmpDir, osName):
        assert osName in self.getOsList()

        vmparam = ""
        vmparam += "arch=%s\n"
        vmparam += "cpu=%d\n"
        vmparam += "memory=%d\n"

        fn = os.path.join(tmpDir, "unattended.iso")
        self._shell("/usr/bin/fpemud-umake --os \"%s\" --media image \"%s\"" % (osName, fn))

        return (fn, vmparam)
    
    def _shell(self, cmd):
        assert cmd.startswith("/")

        # Execute shell command, throws exception when failed, returns stdout+stderr
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        out = proc.communicate()[0]
        if proc.returncode != 0:
            raise Exception("Executing shell command \"%s\" failed, return code %d" % (cmd, proc.returncode))
        return out