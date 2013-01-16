#!/usr/bin/python

import os.path
import logging

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build

from org.wayround.aipsetup.buildtools import autotools
from org.wayround.aipsetup.buildtools import cmake


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.buildscript.build_script_wrap(
            buildingsite,
            ['extract', 'cmake', 'build', 'distribute'],
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

        if 'cmake' in actions and ret == 0:
            ret = cmake.cmake_high(
                buildingsite,
                options=[
                    '-DCMAKE_INSTALL_PREFIX=/usr/lib/mysql',
                    '-DWITH_SSL=yes',
                    '-DWITH_READLINE=yes',
                    '-DWITH_EXTRA_CHARSETS=all',
                    '-DWITH_EMBEDDED_SERVER=yes',
                    '-DWITH_CHARSET=utf8'
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_subdir=source_configure_reldir,
                build_in_separate_dir=separate_build_dir
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

    return ret
