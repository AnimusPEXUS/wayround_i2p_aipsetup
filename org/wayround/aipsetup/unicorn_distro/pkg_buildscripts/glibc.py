#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path
import logging
import time

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.buildscript.build_script_wrap(
            buildingsite,
            ['extract', 'extract2', 'configure', 'build', 'distribute'],
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

        if 'extract2' in actions:
            ret = autotools.extract_high(
                buildingsite,
                'glibc-ports',
                unwrap_dir=False,
                rename_dir='ports'
                )
            if ret != 0:
                logging.warning("glibc-ports are not found. this is Ok starting from glibc-2.17")
                logging.info("sleeping for 10 seconds and continuing")
                time.sleep(10)
                ret = 0


        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-obsolete-rpc',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' + pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' + pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    '--target=' + pkg_info['constitution']['target'],
                    '--enable-kernel=2.6.39.3',
                    '--enable-tls',
                    '--with-elf',
                    '--enable-multi-arch'
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir='.',
                use_separate_buildding_dir=True,
                script_name='configure',
                run_script_not_bash=False,
                relative_call=False
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=True,
                source_configure_reldir='.'
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + (
                        org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            )
                        )
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=True,
                source_configure_reldir='.'
                )

    return ret
