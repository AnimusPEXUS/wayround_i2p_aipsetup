
"""
This module is for tools for creating and running virtual building hosts,
to minimize possible negative impact on distribution developer working system
"""

import os.path
import wayround_org.utils.path


class VirtualBuildingHost:

    def __init__(self):
        self.path = os.path.expand('~/_LAILALO/virtual_building_host')
        self.actual_user_name = None
        self.run_under_user_name = None
        return

    def _check_actual_user_name(self):

        if not isinstance(self.actual_user_name, str):
            raise TypeError("actual_user_name must be str")

        if (not self.actual_user_name.isidentifier()
                or not self.actual_user_name.islower()):
            raise ValueError("invalid actual_user_name value")

        return

    def _check_run_under_user_name(self):

        if not isinstance(self.run_under_user_name, str):
            raise TypeError("run_under_user_name must be str")

        if (not self.run_under_user_name.isidentifier()
                or not self.run_under_user_name.islower()):
            raise ValueError("invalid run_under_user_name value")

        return

    def _check_inst_settings_before_any_work(self):
        self._check_actual_user_name()
        self._check_run_under_user_name()
        return

    def set_working_dir(self, path):
        self.path = path
        return

    def create_vbh_directory(self):
        os.makedirs(self.path, exist_ok=True)
        return

    def create_vbh_starting_script(self)
        script = """\
#!/bin/env python3

import subprocess

p = subprocess.Popen(
    [
        'qemu-system-x86_64',
        '-m', '2048',
        '-vga', 'virtio',
        '-display', 'sdl,gl=on',
        '-enable-kvm',
        '-drive', 'file=drive.bin,index=0,media=disk,format=raw',
        # '-drive, 'file=boot.bin,index=1,media=disk,format=raw',
        '-soundhw', 'hda',
        '-net', 'user,hostfwd=tcp:127.0.0.1:10022-:22',
        '-net', 'nic',
        '-boot', 'order=c',

        #    -device vfio-pci,host=01:00.0,multifunction=on \
        #    -device vfio-pci,host=01:00.1

        #    -nographic \

        # -vga virtio \
        # -display sdl,gl=on \
        # -hdb sdc1/d.bin
        # -drive file=/home/agu/_local/_installers/windows/Windows.7.SP1.ENG.x86-x64.ACTiVATED.iso,media=cdrom \

        # -device vfio-pci,host=01:00.0,bus=root.1,addr=00.0,multifunction=on,x-vga=on,romfile=$HOME/Asus.HD6850.1024.110616.rom \
        # -device vfio-pci,host=01:00.1,bus=pcie.0 \
        ]
    )

exit(p.wait())

"""

        j = wayround_org.utils.path.join(self.path, 'start')

        with open(j, 'w') as f:
            f.write(script)

        return

    def init(self):
        self._check_inst_settings_before_any_work()

        self.create_vbh_directory()
        self.create_vbh_starting_script()
        self.create_vbh_hdd_image()
        return

    def populate_with_basic_system(self):
        self._check_inst_settings_before_any_work()
        return

    def run(self):
        self._check_inst_settings_before_any_work()
        return
