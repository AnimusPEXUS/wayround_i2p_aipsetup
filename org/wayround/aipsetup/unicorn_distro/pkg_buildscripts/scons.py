#!/usr/bin/python

import os.path
import logging
import subprocess

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'bootstrap', 'build_and_distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)
        dst_dir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

        python = 'python2'

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

        if 'bootstrap' in actions and ret == 0:
            ret = subprocess.Popen(
                [python, 'bootstrap.py', os.path.join(src_dir, 'build', 'scons')],
                cwd=src_dir
                ).wait()

        if 'build_and_distribute' in actions and ret == 0:
            ret = subprocess.Popen(
                [python, 'setup.py', 'install', '--prefix=' + os.path.join(dst_dir, 'usr')],
                cwd=os.path.join(src_dir, 'build', 'scons')
                ).wait()

    return ret