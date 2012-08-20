#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.constitution

def build_info():


    constitution = org.wayround.aipsetup.constitution.read_constitution()

    ret = {
        'build_tools': {
            'extract'    : 'autotools',
            'patch'      : 'autotools',
            'configure'  : 'autotools',
            'build'      : 'autotools',
            'distribute' : 'autotools',
            'prepack'    : 'autotools'
            },

        'build_sequance': [
            'extract',
            'configure',
            'build',
            'distribute',
            'prepack'
            ],

        # Do not remove this, as it's used on also with configure less
        # makes
        'autotools_configure_opts': {
            'separate_build_dir': True,
            'config_dir': '.',
            'script_name': 'configure'
            },

        'autotools_configure_env_opts': {
            'mode': 'copy'      # can be copy or clean
            },

        'autotools_configure_envs': {
            # # example
            # # this will add new or rewrite old
            # 'NAME': 'VALUE',
            # # this  will delete
            # 'NAME': None
            },

        'autotools_configure_params': {
            'prefix': '/usr',
            'mandir': '/usr/share/man',
            'sysconfdir': '/etc',
            'localstatedir': '/var',
            'enable-shared': None,
            'host': '%(arch)s-%(type)s-%(kenl)s-%(name)s' % {
                'arch': constitution['host_arch'],
                'type': constitution['host_type'],
                'kenl': constitution['host_kenl'],
                'name': constitution['host_name']
                },
            'build': '%(arch)s-%(type)s-%(kenl)s-%(name)s' % {
                'arch': constitution['host_arch'],
                'type': constitution['host_type'],
                'kenl': constitution['host_kenl'],
                'name': constitution['host_name']
                }
            },

        'autotools_build_opts': {
            'make_file_name': 'Makefile'
            },

        'autotools_build_params': {
            },

        'autotools_build_env_opts': {
            'mode': 'copy'      # can be copy or clean
            },

        'autotools_build_envs': {
            # # example
            # # this will add new or rewrite old
            # 'NAME': 'VALUE',
            # # this  will delete
            # 'NAME': None
            },

        'autotools_install_opts': {
            'make_file_name': 'Makefile',
            'DESTDIR_opt_name': 'DESTDIR'
            },

        'autotools_install_params': {
            },

        'autotools_install_env_opts': {
            'mode': 'copy'      # can be copy or clean
            },

        'autotools_install_envs': {
            # # example
            # # this will add new or rewrite old
            # 'NAME': 'VALUE',
            # # this  will delete
            # 'NAME': None
            }

        }

    return ret
