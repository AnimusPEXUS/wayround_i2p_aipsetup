#!/usr/bin/python3.2
# -*- coding: utf-8 -*-

import os.path

import org.wayround.aipsetup.buildtools.autotools
import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.name

import org.wayround.utils.log

def extract(building_site):

    ret = 0

    building_site = os.path.abspath(building_site)

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site),
        'extract'
        )

    pkg_info = org.wayround.aipsetup.buildingsite.read_package_info(
        building_site
        )

    if not isinstance(pkg_info, dict):
        log.error("Can't read package info")
        ret = 1
    else:

        building_site = os.path.abspath(building_site)

        tarball_dir = org.wayround.aipsetup.buildingsite.getDIR_TARBALL(building_site)

        source_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(building_site)

        tarball_dir_files = os.listdir(tarball_dir)

        tarball_dir_files_len = len(tarball_dir_files)

        if tarball_dir_files_len == 0:
            log.error("No Source Tarball Supplied")
            ret = 1
        else:

            tarball = None
            for i in tarball_dir_files:
                parsed = org.wayround.aipsetup.name.source_name_parse(
                    i, mute=True
                    )
                if isinstance(parsed, dict):
                    if parsed['groups']['name'] == pkg_info['pkg_info']['basename']:
                        tarball = tarball_dir + os.path.sep + tarball_dir_files[0]
                        break

            if not tarball:
                log.error("Couldn't find acceptable tarball for current building site")
                ret = 2
            else:

                ret = org.wayround.aipsetup.buildtools.autotools.extract(
                    log,
                    building_site,
                    tarball,
                    source_dir,
                    unwrap_dir=True
                    )

    log.close()

    return ret


def configure(building_site):

    ret = 0

    building_site = os.path.abspath(building_site)


    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site),
        'configure'
        )

    pkg_info = org.wayround.aipsetup.buildingsite.read_package_info(
        building_site
        )

    if not isinstance(pkg_info, dict):
        log.error("Can't read package info")
        ret = 1
    else:



        opts = org.wayround.aipsetup.buildtools.autotools.determine_configure_parameters(
                {
                    'prefix': pkg_info['constitution']['paths']['usr'],
                    'mandir': pkg_info['constitution']['paths']['man'],
                    'sysconfdir': pkg_info['constitution']['paths']['config'],
                    'localstatedir': pkg_info['constitution']['paths']['var'],
                    'enable-shared': None,
                    'host': pkg_info['constitution']['host'],
                    'build': pkg_info['constitution']['build'],
                    'target': pkg_info['constitution']['target']
                    }
            )


        ret = org.wayround.aipsetup.buildtools.autotools.configure(
            log, building_site, opts, separate_build, env, env_mode, config_dir, script_name
            )


    log.close()

    return ret

def build(building_site):
    pass

def check(building_site):
    pass

def distribute(building_site):
    pass

#def build_script(building_site, constitution=None):
#
#    ret = 0
#
#    log = org.wayround.utils.log.Log(
#        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site),
#        'main_building_script'
#        )
#
#
#
#
#    if not constitution:
#        constitution = org.wayround.aipsetup.constitution.read_constitution()
#
#
#        ret = {
#            'actions': [
#                # TODO: 'Extract' must be not in autotools?
#                dict(
#                    name='extract',
#                    words=('extractor', 'extracting', 'extraction'),
#                    desc='extracting sources',
#                    args=(
#                        ),
#                    kwargs=dict(
#                        unwrap_dir=True
#                        ),
#
#                    {
#                        'settings':{
#                            'tarball':'tarball',
#                            'unwrap_subdir': True,
#                            'output_dir': ''
#                            }
#                        }
#                ),
#    #            dict(
#    #                name='patch',
#    #                desc='patching sources',
#    #                func=autotools['patch'],
##                    args=(),
#    #                data={}
#    #            ),
#                dict(
#                    name='configure',
#                    words=('configurer', 'configuring', 'configuration'),
#                    desc='configuring sources',
#                    func=autotools['configure'],
#                    args=(),
#                    kwargs={
#                        'settings': {
#                            'separate_build_dir': True,
#                            'config_dir': '.',
#                            'script_name': 'configure'
#                            },
#                        'env_opts': {
#                            'mode': 'copy'      # can be copy or clean
#                            },
#                        'env': {
#                            # # example
#                            # # this will add new or rewrite old
#                            # 'NAME': 'VALUE',
#                            # # this  will delete
#                            # 'NAME': None
#                            },
#                        'opts': {
#                            'prefix': '/usr',
#                            'mandir': '/usr/share/man',
#                            'sysconfdir': '/etc',
#                            'localstatedir': '/var',
#                            'enable-shared': None,
#                            'host': constitution['host'],
#                            'build': constitution['build'],
#                            'target': constitution['target']
#                            },
#                        }
#                ),
#                dict(
#                    name='build',
#                    words=('builder', 'building', 'building'),
#                    desc='building software',
#                    func=autotools['make'],
#                    args=(),
#                    kwargs={
#                        'settings': {
#                            'make_file_name': 'Makefile'
#                            },
#                        'args': [
#                            ],
#                        'env_opts': {
#                            'mode': 'copy'      # can be copy or clean
#                            },
#
#                        'env': {
#                            # # example
#                            # # this will add new or rewrite old
#                            # 'NAME': 'VALUE',
#                            # # this  will delete
#                            # 'NAME': None
#                            },
#                        }
#                ),
#                dict(
#                    name='distribute',
#                    words=('distributer', 'distributing', 'distribution'),
#                    desc='distributing software',
#                    func=autotools['make'],
#                    args=(),
#                    kwargs={
#                        'settings': {
#                            'make_file_name': 'Makefile',
#                            },
#
#                        'args': [
#                            'install',
#                            'DESTDIR=' + org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(building_site)
#                            ],
#
#                        'env_opts': {
#                            'mode': 'copy'      # can be copy or clean
#                            },
#
#                        'envs': {
#                            # # example
#                            # # this will add new or rewrite old
#                            # 'NAME': 'VALUE',
#                            # # this  will delete
#                            # 'NAME': None
#                            }
#                        }
#                ),
#    #            dict(
#    #                name='prepack',
#    #                words=('prepackager', 'prepackaging', 'prepackaging'),
#    #                desc='prepackaging software',
#    #                func=autotools['prepack'],
##                    args=(),
#    #                kwargs={}
#    #            ),
#
#                ],
#
#            # Do not remove this, as it's used on also with configure less
#            # makes
#
#            }
#
#    return ret

def main(buildingsite, opts, args):
    extract('.')
