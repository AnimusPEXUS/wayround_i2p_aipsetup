#!/usr/bin/python
# -*- coding: utf-8 -*-

def build_info(config, package_info):

    constitution = package_info['constitution']

    package_info['pkg_buildinfo'] = {
        'extractor'    : 'autotools',
        'builder'      : 'autotools',
        'installer'    : 'autotools',

        'build_sequance': [
            'extract',
            # 'build',
            'install'
            ],

        'autotools_configure_opts': {
            'separate_build_dir': False,
            'config_dir': '.',
            'script_name': 'configure'
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

    return
