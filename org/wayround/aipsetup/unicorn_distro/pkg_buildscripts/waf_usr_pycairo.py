#!/usr/bin/python
# -*- coding: utf-8 -*-

import org.wayround.aipsetup.constitution

def build_script():


    constitution = org.wayround.aipsetup.constitution.read_constitution()

    ret = {
        'build_tools': {
            'extract'    : 'autotools',
            #'patch'      : 'autotools',
            'configure'  : 'waf',
            'build'      : 'waf',
            'distribute' : 'waf',
            'prepack'    : 'autotools',
            },

        'build_sequance': [
            'extract',
            'configure',
            'build',
            'distribute',
            'prepack',
            ],

        # Do not remove this, as it's used on also with configure less
        # makes
        'waf_configure_opts': {
            'separate_build_dir': False,
            'config_dir': '.',
            'script_name': 'waf'
            },

        'waf_configure_env_opts': {
            'mode': 'copy'      # can be copy or clean
            },

        'waf_configure_envs': {
            'PYTHON': '/usr/bin/python3'
            },

        'waf_configure_params': {
            'prefix': '/usr',
            'mandir': '/usr/share/man',
            'sysconfdir': '/etc',
            'localstatedir': '/var'
            },

        'waf_build_opts': {
            'make_file_name': 'Makefile'
            },

        'waf_build_params': {
            },

        'waf_build_env_opts': {
            'mode': 'copy'      # can be copy or clean
            },

        'waf_build_envs': {
            # # example
            # # this will add new or rewrite old
            # 'NAME': 'VALUE',
            # # this  will delete
            # 'NAME': None
            },

        'autotools_distribute_opts': {
            'make_file_name': 'Makefile',
            'DESTDIR_opt_name': 'DESTDIR'
            },

        'autotools_distribute_params': {
            },

        'autotools_distribute_env_opts': {
            'mode': 'copy'      # can be copy or clean
            },

        'autotools_distribute_envs': {
            # # example
            # # this will add new or rewrite old
            # 'NAME': 'VALUE',
            # # this  will delete
            # 'NAME': None
            }

        }

    return ret
