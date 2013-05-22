#!/usr/bin/python

import os.path
import logging
import subprocess

import org.wayround.utils.file

import org.wayround.aipsetup.build
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'configure', 'build', 'distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

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

#    RUN[$j]='export CFLAGS=" -march=i486 -mtune=i486  " ; export CXXFLAGS=" -march=i486 -mtune=i486  " #'
        if 'configure' in actions and ret == 0:
            p = subprocess.Popen(
                ['./configure'] +
                    [
    #                    '-system-nas-sound',
                    '-opensource',
                    '-prefix', '/usr/lib/qt_w_toolkit',
                    '-sysconfdir', pkg_info['constitution']['paths']['config'],
                    '-bindir', '/usr/bin',
                    '-libdir', '/usr/lib',
                    '-headerdir', '/usr/include',
    #                    '--host=' + pkg_info['constitution']['host'],
    #                    '--build=' + pkg_info['constitution']['build'],
    #                    '--target=' + pkg_info['constitution']['target']
                    ],
                stdin=subprocess.PIPE,
                cwd=src_dir
                )
            p.communicate(input=b'yes\n')
            ret = p.wait()


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
                    'INSTALL_ROOT=' + (
                        org.wayround.aipsetup.build.getDIR_DESTDIR(
                            buildingsite
                            )
                        )
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

    return ret
