#!/usr/bin/python

import os.path
import logging
import glob
import shutil

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'configure', 'build', 'distribute', 'wrapper'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
            buildingsite
            )

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

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' + pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' + pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    '--target=' + pkg_info['constitution']['target']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir,
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

        if 'wrapper' in actions and ret == 0:
            os.makedirs(
                dst_dir +
                    os.path.sep + 'etc' + os.path.sep +
                    'profile.d' + os.path.sep + 'SET',
                exist_ok=True
                )

            os.makedirs(
                dst_dir +
                    os.path.sep + 'usr' + os.path.sep + 'share' + os.path.sep +
                    'mc' + os.path.sep + 'bin',
                exist_ok=True
                )

            files = glob.glob(
                src_dir + os.path.sep + 'contrib' + os.path.sep + '*.sh'
                )

            for i in files:
                shutil.copy(
                    i,
                    dst_dir +
                        os.path.sep + 'usr' + os.path.sep + 'share' + os.path.sep +
                        'mc' + os.path.sep + 'bin'
                    )

            f = open(
                dst_dir +
                    os.path.sep + 'etc' + os.path.sep +
                    'profile.d' + os.path.sep + 'SET' + os.path.sep + '009.mc',
                'w'
                )
            f.write(
"""\
#!/bin/bash

alias mc=". /usr/share/mc/bin/mc-wrapper.sh"

"""
                )
            f.close()

    return ret