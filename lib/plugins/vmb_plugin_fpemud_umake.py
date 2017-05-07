#!/usr/bin/python3.4
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import subprocess
import threading


class LbVmbPlugin:

    def __init__(self):
        self.OS_MSWINXP_X86 = "Fpemud's Windows.XP (X86)"
        self.OS_MSWIN7_X86 = "Fpemud's Windows.7 (X86)"
        self.OS_MSWIN7_AMD64 = "Fpemud's Windows.7 (X86_64)"

        self.proc = None
        self.errThread = None
        self.dest = None
        self.progress_callback = None

    def get_os_name_list(self):
        return [
            self.OS_MSWINXP_X86,
            self.OS_MSWIN7_X86,
            self.OS_MSWIN7_AMD64,
        ]

    def get_os_icon(self):
        return None

    def create_setup_iso_async(self, tmp_dir, os_name, progress_callback):
        assert self.proc is None and self.errThread is None and self.dest is None
        self.dest = os.path.join(tmp_dir, "unattended.iso")
        cmd = "/usr/bin/fpemud-umake --os \"%s\" --media image --dot-progress \"%s\"" % (os_name, self.dest)
        self.proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.errThread = _ErrThread(self.proc)
        self.errThread.start()
        self.progress_callback = progress_callback
        return self.proc.stdout

    def create_setup_iso_cancel(self):
        try:
            self.proc.terminate()
            self.proc.communicate()
            self.errThread.join()
        finally:
            self.proc = None
            self.errThread = None
            self.dest = None
            self.progress_callback = None

    def create_setup_iso_finish(self):
        try:
            self.proc.wait()
            self.errThread.join()
            if self.proc.returncode != 0:
                raise Exception(self.errThread.errmsg)
            return self.dest
        finally:
            self.proc = None
            self.errThread = None
            self.dest = None
            self.progress_callback = None

    def _getHostArch(self):
        # Code copied from /usr/src/linux/Makefile
        cmd = "/usr/bin/uname -m | /bin/sed -e s/i.86/i386/ -e s/sun4u/sparc64/" + \
              "                             -e s/arm.*/arm/ -e s/sa110/arm/" + \
              "                             -e s/s390x/s390/ -e s/parisc64/parisc/" + \
              "                             -e s/ppc.*/powerpc/ -e s/mips.*/mips/" + \
              "                             -e s/sh.*/sh/"
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        if proc.returncode != 0:
            raise Exception("Get host architecture failed, %s" % (err))
        return out.replace("\n", "")


class _ErrThread(threading.Thread):

    def __init__(self, proc):
        super(_ErrThread, self).__init__()
        self.proc = proc
        self.errmsg = None

    def run(self):
        self.errmsg = self.proc.stderr.read().decode("utf-8")
