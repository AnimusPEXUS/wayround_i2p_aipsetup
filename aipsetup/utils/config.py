# -*- coding: utf-8 -*-

import os
import os.path
import ConfigParser

default_config = {
    'aipsetup_dir': '/mnt/sda3/home/agu/p/aipsetup/aipsetup-3',

    'editor'             : 'emacs',

    'uhtroot'            : '/mnt/sda3/home/agu/_UHT',

    'constitution'       : '/mnt/sda3/home/agu/_UHT/system_constitution.py',

    'builders'           : '/mnt/sda3/home/agu/_UHT/pkg_builders',
    'buildinfo'          : '/mnt/sda3/home/agu/_UHT/pkg_buildinfo',
    'repository'         : '/mnt/sda3/home/agu/_UHT/pkg_repository',
    'source'             : '/mnt/sda3/home/agu/_UHT/pkg_source',
    'info'               : '/mnt/sda3/home/agu/_UHT/pkg_info',
    'buildingsites'      : '/mnt/sda3/home/agu/_UHT/pkg_buildingsites',

    'repository_index'   : '/mnt/sda3/home/agu/_UHT/index_repository.lst',
    'source_index'       : '/mnt/sda3/home/agu/_UHT/index_source.lst',

    'sqlalchemy_engine_string': 'sqlite:////mnt/sda3/home/agu/_UHT/pkgindex.sqlite',

    'server_ip'          : '127.0.0.1',
    'server_port'        : '8005',
    'server_prefix'      : '/',
    'server_password'    : '123456789',

    'client_local_proto'       : 'http',
    'client_local_host'        : '127.0.0.1',
    'client_local_port'        : '8005',
    'client_local_prefix'      : '/',

    'client_remote_proto'      : 'http',
    'client_remote_host'       : '127.0.0.1',
    'client_remote_port'       : '8005',
    'client_remote_prefix'     : '/',

    # thous will be used relatively to install.py destdir parameters
    'installed_pkg_dir': '/var/log/packages',
    'installed_pkg_dir_buildlogs': '/var/log/packages/buildlogs',
    'installed_pkg_dir_sums': '/var/log/packages/sums'
    }

actual_config = None


def load_config():
    global actual_config

    ret = None

    if actual_config != None:
        ret = actual_config

    else:

        if os.path.isfile('/etc/aipsetup.conf'):
            r = get_configuration(
                default_config,
                '/etc/aipsetup.conf')

            if isinstance(r, dict):
                ret = r
            else:
                ret = None

        actual_config = ret

    return ret


def get_configuration(defaults, filename='/etc/aipsetup.conf'):

    ret = defaults

    cp = ConfigParser.RawConfigParser()

    f = None

    try:
        f = open(filename, 'r')
    except:
        print "-e- Can't open %(file)s" % {'file': filename}
        ret = None
    else:
        try:
            cp.readfp(f)
        except:
            print "-e- Can't read %(file)s" % {'file': filename}
            ret = None
        else:

            if isinstance(ret, dict):
                if cp.has_section('main'):

                    for i in defaults:
                        if cp.has_option('main', i):
                            ret[i] = cp.get('main', i)

        f.close()

    del(cp)
    return ret
