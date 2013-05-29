
"""
aipsetup configuration manipulations
"""

import os.path
import copy
import logging
import pprint
import configparser

import org.wayround.utils.path

DEFAULT_CONFIG = {
    'general': {
        'editor': 'emacs',
        'acceptable_src_file_extensions':
            '.tar.gz .tar.bz2 .zip .7z .tgz .tar.xz .tar.lzma .tbz2',
        },

    'system_settings': {
        'system_title': 'UNICORN',
        'system_version': '2.0',

        'installed_pkg_dir': '/var/log/packages',

        'installed_pkg_dir_buildlogs': '%(installed_pkg_dir)s/buildlogs',
        'installed_pkg_dir_sums': '%(installed_pkg_dir)s/sums',
        'installed_pkg_dir_deps': '%(installed_pkg_dir)s/deps',

        'host': 'i486-pc-linux-gnu',
        'build': 'i486-pc-linux-gnu',
        'target': 'i486-pc-linux-gnu'
        },

    'system_paths': {
        'root'              :   '/',
        'usr'               :   '/usr',

        'basic_bin'         :   '/bin',
        'basic_sbin'        :   '/sbin',
        'bin'               :   '/usr/bin',
        'sbin'              :   '/usr/sbin',

        'basic_lib'         :   '/lib',
        'lib'               :   '/usr/lib',

        'man'               :   '/usr/share/man',
        'include'           :   '/usr/include',

        'devices'           :   '/dev',
        'config'            :   '/etc',
        'daemons'           :   '/daemons',
        'var'               :   '/var',
        'temp'              :   '/tmp'
        },

    'package_repo': {
        'index_db_config':
            'sqlite:////mnt/sda3/home/agu/_UNICORN/pkgindex.sqlite',
        'dir':
            '/mnt/sda3/home/agu/_UNICORN/pkg_repository',
        'snapshots_dir': '/mnt/sda3/home/agu/_UNICORN/snapshots',
        'garbage_dir': '/mnt/sda3/home/agu/_UNICORN/garbage',
        },

    'sources_repo': {
        'index_db_config':
            'sqlite:////mnt/sda3/home/agu/_UNICORN/sources.sqlite',
        'dir':
            '/mnt/sda3/home/agu/_UNICORN/pkg_source',
        },

    'info_repo': {
        'index_db_config': 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkginfo.sqlite',
        'dir':'/mnt/sda3/home/agu/_UNICORN/pkg_info',
        'tags_db_config': 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkgtags.sqlite',
        'tags_json': '/mnt/sda3/home/agu/_UNICORN/tags.json',
        },

    'latest_repo': {
        'index_db_config': 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkglatest.sqlite',
        },

    'builder_repo': {
        'building_scripts_dir': '/mnt/sda3/home/agu/_UNICORN/pkg_buildscripts',
        'building_sites_dir': '/mnt/sda3/home/agu/_UNICORN/b'
        },

    'web_server_config': {
        'ip'          : '127.0.0.1',
        'port'        : '8005',
        'path_prefix' : '/',
        },

    'web_client_config': {
        'server_url'  : 'http://127.0.0.1:8005/'
        },

    }



def load_config(filename):

    cfg = configparser.ConfigParser()
    cfg.read_dict(DEFAULT_CONFIG)
    cfg.read(filename)

    return cfg


def save_config(filename, config):

    if not isinstance(config, (configparser.ConfigParser, dict,)):
        raise TypeError("config must be dict or configparser.ConfigParser")

    if isinstance(config, dict):
        cfg = configparser.ConfigParser()
        cfg.read_dict(DEFAULT_CONFIG)
        cfg.read_dict(config)
        config = cfg

    f = open(filename, 'w')
    config.write(f)
    f.close()

    return
