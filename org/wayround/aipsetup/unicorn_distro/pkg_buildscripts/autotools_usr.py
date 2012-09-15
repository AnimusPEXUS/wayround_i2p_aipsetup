#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.buildtools
import org.wayround.aipsetup.buildingsite

def build_script(building_site, log, constitution=None):

    autotools = org.wayround.aipsetup.buildtools.get_tool_functions('autotools')

    if not constitution:
        constitution = org.wayround.aipsetup.constitution.read_constitution()

    ret = {
        'actions': [
            # TODO: 'Extract' must be not in autotools?
            dict(
                name='extract',
                desc='extracting sources',
                func=autotools['extract'],
                args=(),
                kwargs={}
            ),
#            dict(
#                name='patch',
#                desc='patching sources',
#                func=autotools['patch'],
#                args=(),
#                kwargs={}
#            ),
            dict(
                name='configure',
                desc='configuring sources',
                func=autotools['configure'],
                args=(),
                kwargs={
                    'settings': {
                        'separate_build_dir': True,
                        'config_dir': '.',
                        'script_name': 'configure'
                        },
                    'env_opts': {
                        'mode': 'copy'      # can be copy or clean
                        },
                    'env': {
                        # # example
                        # # this will add new or rewrite old
                        # 'NAME': 'VALUE',
                        # # this  will delete
                        # 'NAME': None
                        },
                    'opts': {
                        'prefix': '/usr',
                        'mandir': '/usr/share/man',
                        'sysconfdir': '/etc',
                        'localstatedir': '/var',
                        'enable-shared': None,
                        'host': '{arch}-{type}-{syst}'.format_map({
                            'arch': constitution['host_arch'],
                            'type': constitution['host_type'],
                            'syst': constitution['host_system']
                            }),
                        'build': '{arch}-{type}-{syst}'.format_map({
                            'arch': constitution['build_arch'],
                            'type': constitution['build_type'],
                            'syst': constitution['build_system']
                            }),
                        'target': '{arch}-{type}-{syst}'.format_map({
                            'arch': constitution['target_arch'],
                            'type': constitution['target_type'],
                            'syst': constitution['target_system']
                            })
                        },
                    }
            ),
            dict(
                name='build',
                desc='building software',
                func=autotools['make'],
                args=(),
                kwargs={
                    'settings': {
                        'make_file_name': 'Makefile'
                        },
                    'args': [
                        ],
                    'env_opts': {
                        'mode': 'copy'      # can be copy or clean
                        },

                    'env': {
                        # # example
                        # # this will add new or rewrite old
                        # 'NAME': 'VALUE',
                        # # this  will delete
                        # 'NAME': None
                        },
                    }
            ),
            dict(
                name='distribute',
                desc='distributing software',
                func=autotools['make'],
                args=(),
                kwargs={
                    'settings': {
                        'make_file_name': 'Makefile',
                        },

                    'args': [
                        'install',
                        'DESTDIR=' + org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(building_site)
                        ],

                    'env_opts': {
                        'mode': 'copy'      # can be copy or clean
                        },

                    'envs': {
                        # # example
                        # # this will add new or rewrite old
                        # 'NAME': 'VALUE',
                        # # this  will delete
                        # 'NAME': None
                        }
                    }
            ),
#            dict(
#                name='prepack',
#                desc='prepackaging software',
#                func=autotools['prepack'],
#                args=(),
#                kwargs={}
#            ),

            ],

        # Do not remove this, as it's used on also with configure less
        # makes

        }

    return ret
