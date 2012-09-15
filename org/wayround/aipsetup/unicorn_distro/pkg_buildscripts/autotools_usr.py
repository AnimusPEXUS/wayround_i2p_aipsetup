#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.buildtools
import org.wayround.aipsetup.buildingsite

def build_script(building_site, constitution=None):

    autotools = org.wayround.aipsetup.buildtools.get_tool_functions('autotools')

    if not constitution:
        constitution = org.wayround.aipsetup.constitution.read_constitution()

    ret = {
        'actions': [
            # TODO: 'Extract' must be not in autotools?
            dict(
                name='extract',
                words=('extractor', 'extracting', 'extraction'),
                desc='extracting sources',
                func=autotools['extract'],
                data={}
            ),
#            dict(
#                name='patch',
#                desc='patching sources',
#                func=autotools['patch'],
#                data={}
#            ),
            dict(
                name='configure',
                words=('configurer', 'configuring', 'configuration'),
                desc='configuring sources',
                func=autotools['configure'],
                data={
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
                        'host': constitution['host'],
                        'build': constitution['build'],
                        'target': constitution['target']
                        },
                    }
            ),
            dict(
                name='build',
                words=('builder', 'building', 'building'),
                desc='building software',
                func=autotools['make'],
                data={
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
                words=('distributer', 'distributing', 'distribution'),
                desc='distributing software',
                func=autotools['make'],
                data={
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
#                words=('prepackager', 'prepackaging', 'prepackaging'),
#                desc='prepackaging software',
#                func=autotools['prepack'],
#                data={}
#            ),

            ],

        # Do not remove this, as it's used on also with configure less
        # makes

        }

    return ret
