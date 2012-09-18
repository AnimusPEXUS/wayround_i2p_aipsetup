#!/usr/bin/python

import logging

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    pkg_info = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite
        )

    ret = 0

    if not isinstance(pkg_info, dict):
        logging.error("Can't read package info")
        ret = 1
    else:

        actions = ['extract', 'configure', 'build', 'distribute']

        if action == 'help':
            print("help")
            ret = 2
        else:

            r = org.wayround.aipsetup.build.build_actions_selector(
                actions,
                action
                )

            if isinstance(r, tuple):
                actions, action = r

            if action != None and not (isinstance(action, str) and isinstance(r, tuple)):
                logging.error("Wrong command")
                ret = 3
            else:

                if not isinstance(actions, list):
                    logging.error("Wrong action `{}' ({})".format(action, actions))
                    ret = 3

                else:

                    if 'extract' in actions:
                        ret = autotools.extract_high(
                            buildingsite,
                            pkg_info['pkg_info']['basename']
                            )

                    if 'configure' in actions and ret == 0:
                        ret = autotools.configure_high(
                            buildingsite,
                            options=[
                                '--prefix=' + pkg_info['constitution']['paths']['usr'],
                                '--mandir=' + pkg_info['constitution']['paths']['man'],
                                '--sysconfdir=' + pkg_info['constitution']['paths']['config'],
                                '--localstatedir=' + pkg_info['constitution']['paths']['var'],
                                '--enable-shared=' + 'yes',
                                '--host=' + pkg_info['constitution']['host'],
                                '--build=' + pkg_info['constitution']['build'],
                                '--target=' + pkg_info['constitution']['target']
                                ],
                            arguments=['configure'],
                            environment={},
                            environment_mode='copy',
                            source_configure_reldir='.',
                            use_separate_buildding_dir=True,
                            script_name='configure'
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
