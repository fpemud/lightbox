#!/usr/bin/python3.4
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import shutil
import subprocess
import time
import grp
import pwd
import socket
import re


class FvpUtil:

    @staticmethod
    def getHostArch():
        # Code copied from /usr/src/linux/Makefile
        ret = FvpUtil.shell("/usr/bin/uname -m | /bin/sed -e s/i.86/i386/ -e s/sun4u/sparc64/" +
                            "                             -e s/arm.*/arm/ -e s/sa110/arm/" +
                            "                             -e s/s390x/s390/ -e s/parisc64/parisc/" +
                            "                             -e s/ppc.*/powerpc/ -e s/mips.*/mips/" +
                            "                             -e s/sh.*/sh/", "stdout")
        ret = ret.replace("\n", "")
        return ret

    @staticmethod
    def str2bool(value):
        """in function bool() of python, "" => False, all others => True, it's strange"""

        if value == "True":
            return True
        elif value == "False":
            return False
        else:
            assert False

    @staticmethod
    def risePriviledge():
        os.setegid(0)
        os.seteuid(0)

    @staticmethod
    def dropPriviledge():
        assert os.geteuid() == 0 and os.getegid() == 0
        os.setegid(os.getresgid()[2])
        os.seteuid(os.getresuid()[2])

    @staticmethod
    def copyToDir(srcFilename, dstdir, mode=None):
        """Copy file to specified directory, and set file mode if required"""

        if not os.path.isdir(dstdir):
            os.makedirs(dstdir)
        fdst = os.path.join(dstdir, os.path.basename(srcFilename))
        shutil.copy(srcFilename, fdst)
        if mode is not None:
            FvpUtil.shell("/bin/chmod " + mode + " \"" + fdst + "\"")

    @staticmethod
    def copyToFile(srcFilename, dstFilename, mode=None):
        """Copy file to specified filename, and set file mode if required"""

        if not os.path.isdir(os.path.dirname(dstFilename)):
            os.makedirs(os.path.dirname(dstFilename))
        shutil.copy(srcFilename, dstFilename)
        if mode is not None:
            FvpUtil.shell("/bin/chmod " + mode + " \"" + dstFilename + "\"")

    @staticmethod
    def readFile(filename):
        """Read file, returns the whold content"""

        f = open(filename, 'r')
        buf = f.read()
        f.close()
        return buf

    @staticmethod
    def writeFile(filename, buf, mode=None):
        """Write buffer to file"""

        f = open(filename, 'w')
        f.write(buf)
        f.close()
        if mode is not None:
            FvpUtil.shell("/bin/chmod " + mode + " \"" + filename + "\"")

    @staticmethod
    def mkDirAndClear(dirname):
        FvpUtil.forceDelete(dirname)
        os.mkdir(dirname)

    @staticmethod
    def touchFile(filename):
        assert not os.path.exists(filename)
        f = open(filename, 'w')
        f.close()

    @staticmethod
    def forceDelete(filename):
        if os.path.islink(filename):
            os.remove(filename)
        elif os.path.isfile(filename):
            os.remove(filename)
        elif os.path.isdir(filename):
            shutil.rmtree(filename)

    @staticmethod
    def forceSymlink(source, link_name):
        if os.path.exists(link_name):
            os.remove(link_name)
        os.symlink(source, link_name)

    @staticmethod
    def getFreeSocketPort(portType, portStart=-1, portEnd=-1):
        if portType == "tcp":
            sType = socket.SOCK_STREAM
        elif portType == "udp":
            assert False
        else:
            assert False

        if portStart == -1:
            portStart = 10000
        if portEnd == -1:
            portEnd = 65535
        assert portStart <= portEnd

        for port in range(portStart, portEnd + 1):
            s = socket.socket(socket.AF_INET, sType)
            try:
                s.bind((('', port)))
                return port
            except socket.error:
                continue
            finally:
                s.close()
        raise Exception("No valid %s port in [%d,%d]." % (portType, portStart, portEnd))

    @staticmethod
    def shell(cmd, flags=""):
        """Execute shell command"""

        assert cmd.startswith("/")

        # Execute shell command, throws exception when failed
        if flags == "":
            retcode = subprocess.Popen(cmd, shell=True).wait()
            if retcode != 0:
                raise Exception("Executing shell command \"%s\" failed, return code %d" % (cmd, retcode))
            return

        # Execute shell command, throws exception when failed, returns stdout+stderr
        if flags == "stdout":
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            out = proc.communicate()[0]
            if proc.returncode != 0:
                raise Exception("Executing shell command \"%s\" failed, return code %d" % (cmd, proc.returncode))
            return out

        # Execute shell command, returns (returncode,stdout+stderr)
        if flags == "retcode+stdout":
            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            out = proc.communicate()[0]
            return (proc.returncode, out)

        assert False

    @staticmethod
    def ipMaskToLen(mask):
        """255.255.255.0 -> 24"""

        netmask = 0
        netmasks = mask.split('.')
        for i in range(0, len(netmasks)):
            netmask *= 256
            netmask += int(netmasks[i])
        return 32 - (netmask ^ 0xFFFFFFFF).bit_length()

    @staticmethod
    def loadKernelModule(modname):
        """Loads a kernel module."""

        FvpUtil.shell("/sbin/modprobe %s" % (modname))

    @staticmethod
    def initLog(filename):
        FvpUtil.forceDelete(filename)
        FvpUtil.writeFile(filename, "")

    @staticmethod
    def printLog(filename, msg):
        f = open(filename, 'a')
        if msg != "":
            f.write(time.strftime("%Y-%m-%d %H:%M:%S  ", time.localtime()))
            f.write(msg)
            f.write("\n")
        else:
            f.write("\n")
        f.close()

    @staticmethod
    def getUsername():
        return pwd.getpwuid(os.getuid())[0]

    @staticmethod
    def getGroups():
        """Returns the group name list of the current user"""

        uname = pwd.getpwuid(os.getuid())[0]
        groups = [g.gr_name for g in grp.getgrall() if uname in g.gr_mem]
        gid = pwd.getpwnam(uname).pw_gid
        groups.append(grp.getgrgid(gid).gr_name)            # --fixme, should be prepend
        return groups

    @staticmethod
    def encodePath(src_path):
        """Use the convert algorithm of systemd:
           Some unit names reflect paths existing in the file system namespace.
           Example: a device unit dev-sda.device refers to a device with the device node /dev/sda in the file system namespace.
           If this applies, a special way to escape the path name is used, so that the result is usable as part of a filename.
           Basically, given a path, "/" is replaced by "-", and all unprintable characters and the "-" are replaced by C-style
           "\x20" escapes. The root directory "/" is encoded as single dash, while otherwise the initial and ending "/" is
           removed from all paths during transformation. This escaping is reversible.

           Note:
           1. src_path must be a normalized path, we don't accept path like "///foo///bar/"
           2. the encoding of src_path is a bit messy
           3. what about path like "/foo\/bar/foobar2"?
        """

        assert os.path.isabs(src_path)

        if src_path == "/":
            return "-"

        newPath = ""
        for c in src_path.strip("/"):
            if c == "/":
                newPath.append("-")
            elif re.match("[a-zA-Z0-9:_\\.", c) is not None:
                newPath.append(c)
            else:
                newPath.append("\\x%02x" % (ord(c)))
        return newPath

    @staticmethod
    def decodePath(dst_path):

        if dst_path == "-":
            return "/"

        newPath = ""
        for i in range(0, len(dst_path)):
            if dst_path[i] == "-":
                newPath.append("/")
            elif dst_path[i] == "\\":
                m = re.match("^\\\\x([0-9])+", dst_path[i:])
                if m is None:
                    raise ValueError("encoded path is invalid")
                newPath.append(chr(int(m.group(1))))
            else:
                newPath.append(dst_path[i])
        return "/" + newPath

# class SubProcess:
#    """We maintain a "readBuf" because the system buffer of Popen.stdout is limited
#       This class is thread-safe"""
#
#    class Callback:
#        def onProcExit(self):
#            pass
#
#    class CommThread(threading.Thread):
#        def __init__(self, pObj):
#            super(SubProcess.CommThread, self).__init__()
#            self.pObj = pObj
#
#        def run(self):
#            print "CommThread run"
#
#            while self.pObj.proc.poll() is None:
#
#                print "CommThread run debug 1"
#
#                infds_c,outfds_c,errfds_c = select.select([self.pObj.proc.stdout],[],[])
#                if len(infds_c) > 0:
#                    self.pObj.ioLock.acquire()
#                    try:
#                        msg = self.pObj.proc.stdout.read()
#                        self.pObj.readBuf += msg
#                        self.pObj._writeLogFile(msg)
#                    finally:
#                        self.pObj.ioLock.release()
#
#            print "CommThread run debug 2"
#
#            if self.pObj.callbackObj is not None:
#                self.pObj.callbackObj.onProcExit()
#
#            print "CommThread run end"
#
#    def __init__(self, cmdLine, callbackObj=None, logFile=None):
#        self.proc = subprocess.Popen(cmdLine, shell = True, stdin = subprocess.PIPE, stdout = subprocess.PIPE)
#        #fl = fcntl.fcntl(proc.stdout.fileno(), fcntl.F_GETFL)
#        #fcntl.fcntl(proc.stdout.fileno(), fcntl.F_SETFL, fl | os.O_NONBLOCK)
#
#        self.callbackObj = callbackObj
#        self.logFile = logFile
#
#        self.ioLock = threading.Lock()
#        self.waitThread = self.CommThread(self)
#        self.readBuf = ""
#
#        self.waitThread.start()
#
#    def isAlive(self):
#        return (self.proc.poll() is None)
#
#    def waitToStop(self):
#        self.proc.wait()
#
#    def readFromStdout(self):
#        self.ioLock.acquire()
#        try:
#            ret = self.readBuf
#            self.readBuf = ""
#            return ret
#        finally:
#            self.ioLock.release()
#
#    def writeToStdin(self, msg):
#        self.ioLock.acquire()
#        try:
#            self._writeLogFile(msg)
#            self.proc.stdin.write(msg)            # if stdin is closed, raise exception? no doc on web
#        finally:
#            self.ioLock.release()
#
#    def _writeLogFile(self, msg):
#        if self.logFile is not None:
#            logf = open(self.logFile, "a")
#            logf.write(msg)
#            logf.close()
#
