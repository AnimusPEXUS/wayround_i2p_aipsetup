#!/usr/bin/python

import os.path
import logging

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'build', 'distribute', 'distribute2'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)

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

#        if 'configure' in actions and ret == 0:
#            ret = autotools.configure_high(
#                buildingsite,
#                options=[
#                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
#                    '--mandir=' + pkg_info['constitution']['paths']['man'],
#                    '--sysconfdir=' + pkg_info['constitution']['paths']['config'],
#                    '--localstatedir=' + pkg_info['constitution']['paths']['var'],
#                    '--enable-shared',
#                    '--host=' + pkg_info['constitution']['host'],
#                    '--build=' + pkg_info['constitution']['build'],
#                    '--target=' + pkg_info['constitution']['target']
#                    ],
#                arguments=[],
#                environment={},
#                environment_mode='copy',
#                source_configure_reldir=source_configure_reldir,
#                use_separate_buildding_dir=separate_build_dir,
#                script_name='configure'
#                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'PREFIX=' + pkg_info['constitution']['paths']['usr'],
                    'SHARED=yes',
                    ],
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
                    'DESTDIR=' + (
                        org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            )
                        ),
                    'PREFIX=' + pkg_info['constitution']['paths']['usr'],
                    'SHARED=yes',
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute2' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install-lib',
                    'DESTDIR=' + (
                        org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            )
                        ),
                    'PREFIX=' + pkg_info['constitution']['paths']['usr'],
                    'SHARED=yes',
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

    return ret