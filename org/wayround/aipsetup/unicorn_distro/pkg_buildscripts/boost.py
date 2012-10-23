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
            ['extract', 'bjam_bootstrap', 'build_and_distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)

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

        if 'bjam_bootstrap' in actions and ret == 0:
            ret = subprocess.Popen(
                ['bash', './bootstrap.sh'],
                cwd=src_dir
                ).wait()

        if 'build_and_distribute' in actions and ret == 0:
            ret = subprocess.Popen(
                [
                    os.path.join(src_dir, 'bjam'),
                    '--prefix=' + os.path.join(
                        org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            ),
                        'usr'
                        ),
                    'install'
                    ],
                    cwd=src_dir
                    ).wait()

    return ret
