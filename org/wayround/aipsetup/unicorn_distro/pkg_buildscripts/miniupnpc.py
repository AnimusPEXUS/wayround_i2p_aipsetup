#!/usr/bin/python

import os.path
import logging
import glob
import shutil

import org.wayround.utils.file

import org.wayround.aipsetup.build

from org.wayround.aipsetup.buildtools import autotools
from org.wayround.aipsetup.buildtools import cmake


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
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

        if 'cmake' in actions and ret == 0:
            ret = cmake.cmake_high(
                buildingsite,
                options=[
                    '-DCMAKE_INSTALL_PREFIX=' +
                        pkg_info['constitution']['paths']['usr'],
#                    '--mandir=' + pkg_info['constitution']['paths']['man'],
#                    '--sysconfdir=' + pkg_info['constitution']['paths']['config'],
#                    '--localstatedir=' + pkg_info['constitution']['paths']['var'],
#                    '--enable-shared',
#                    '--host=' + pkg_info['constitution']['host'],
#                    '--build=' + pkg_info['constitution']['build'],
#                    '--target=' + pkg_info['constitution']['target']
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

            hs = glob.glob(org.wayround.utils.path.join(src_dir, '*.h'))
            for i in hs:
                dst_fpn = org.wayround.utils.path.join(
                    dst_dir, 'usr', 'include', 'miniupnpc', os.path.basename(i)
                    )
                shutil.copy(i, dst_fpn)

    return ret
