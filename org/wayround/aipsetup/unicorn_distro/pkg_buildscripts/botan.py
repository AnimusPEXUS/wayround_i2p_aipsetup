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
        ['extract', 'fix', 'configure', 'build', 'distribute'],
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

        if 'fix' in actions and ret == 0:

            f = open(os.path.join(src_dir, 'src', 'build-data', 'botan-config.in'))
            lines = f.read().splitlines()
            f.close()

            for i in range(len(lines)):
                if lines[i] == 'prefix=':
                    lines[i] = 'prefix=/usr'

            f = open(os.path.join(src_dir, 'src', 'build-data', 'botan-config.in'), 'w')
            f.write('\n'.join(lines))
            f.close()


        if 'configure' in actions and ret == 0:
            p = subprocess.Popen(['./configure.py', '--prefix=/usr'], cwd=src_dir)

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
                    'DESTDIR=' + os.path.join(dst_dir, 'usr')
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

    return ret
