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

    r = org.wayround.aipsetup.buildscript.build_script_wrap(
            buildingsite,
            ['extract', 'bootstrap', 'build', 'distribute'],
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

        if 'bootstrap' in actions and ret == 0:
            ret = subprocess.Popen(
                ['bash', './bootstrap.sh', '--prefix=/usr'],
                cwd=src_dir
                ).wait()

        if 'build' in actions and ret == 0:
            ret = subprocess.Popen(
                [
                    os.path.join(src_dir, 'bjam'),
                    '--prefix=' + os.path.join(
                        org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            ),
                        'usr'
                        ),
                    'stage',
                    'threading=multi',
                    'link=shared'
                    ],
                    cwd=src_dir
                    ).wait()

        if 'distribute' in actions and ret == 0:
            ret = subprocess.Popen(
                [
                    os.path.join(src_dir, 'bjam'),
                    '--prefix=' + os.path.join(
                        org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            ),
                        'usr'
                        ),
                    'install',
                    'threading=multi',
                    'link=shared'
                    ],
                    cwd=src_dir
                    ).wait()

    return ret
