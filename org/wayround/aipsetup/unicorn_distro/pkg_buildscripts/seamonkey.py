#!/usr/bin/python

import os.path
import logging

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action = None):

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

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                if org.wayround.utils.file.cleanup_dir(src_dir) != 0:
                    logging.error("Some error while cleaning up source dir")
                    ret = 1

            if ret == 0:

                ret = autotools.extract_high(
                    buildingsite,
                    pkg_info['pkg_info']['basename'],
                    unwrap_dir = True,
                    rename_dir = False
                    )


        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options = [
                    '--with-system-nspr',
                    '--with-system-nss',
                    '--enable-shared',
                    '--enable-optimize',
                    '--enable-default-toolkit=cairo-gtk2',
                    '--enable-xft',
                    '--enable-freetype2',
                    '--enable-application=suite',
                    '--enable-calendar',
                    '--enable-shared-js',
                    '--enable-safe-browsing',
                    '--enable-storage',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' + pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' + pkg_info['constitution']['paths']['var'],
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build']
                    ],
                arguments = [],
                environment = {},
                environment_mode = 'copy',
                source_configure_reldir = '.',
                use_separate_buildding_dir = separate_build_dir,
                script_name = 'configure',
                run_script_not_bash = False,
                relative_call = False
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options = [],
                arguments = [],
                environment = {},
                environment_mode = 'copy',
                use_separate_buildding_dir = separate_build_dir,
                source_configure_reldir = '.'
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options = [],
                arguments = [
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment = {},
                environment_mode = 'copy',
                use_separate_buildding_dir = separate_build_dir,
                source_configure_reldir = '.'
                )


            inc_dir = os.path.join(dst_dir, 'usr', 'include')

            lst = os.listdir(inc_dir)

            sea_inc_dir = None

            if not len(lst) == 1:
                logging.error("Can't find seamonkey includes dir in {}".format(inc_dir))
                ret = 30
            else:
                sea_inc_dir = lst[0]

                os.symlink(sea_inc_dir, os.path.join(inc_dir, 'npapi'))

    return ret
