#!/usr/bin/python3.4
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-


class LbVmbPlugin:

    def __init__(self):
        pass

    def get_os_name_list(self):
        return []

    def get_os_icon(self, os_name):
        return None

    def create_setup_iso_async(self, tmp_dir, os_name, progress_callback):
        pass

    def create_setup_iso_cancel(self):
        pass

    def create_setup_iso_finish(self):
        pass

    def update_vm_config(self, os_name, vm_config):
        pass

    def get_main_disk_size(self, os_name):
        pass

        