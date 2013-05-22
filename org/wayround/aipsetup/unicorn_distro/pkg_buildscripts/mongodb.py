#!/usr/bin/python

import os.path
import logging
import subprocess

import org.wayround.utils.file

import org.wayround.aipsetup.build
import org.wayround.aipsetup.build

from org.wayround.aipsetup.buildtools import autotools
from org.wayround.aipsetup.buildtools import cmake


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'scons', 'distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'scons' in actions and ret == 0:
            p = subprocess.Popen(['scons', 'all'], cwd=src_dir)
            ret = p.wait()


        if 'distribute' in actions and ret == 0:
            p = subprocess.Popen(
                [
                    'scons',
                    '--prefix=' + os.path.join(dst_dir, 'usr'),
                    'install'],
                cwd=src_dir
                )
            ret = p.wait()

    return ret
