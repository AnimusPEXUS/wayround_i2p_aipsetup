
"""
aipsetup configuration manipulations
"""

import configparser
import os.path
import logging
import collections
import pprint

import wayround_org.utils.path


CUR_DIR = wayround_org.utils.path.abspath(os.path.dirname(__file__))
EMBEDDED_DISTRO_DIR = wayround_org.utils.path.join(
    CUR_DIR, 'distro'
    )


DEFAULT_CONFIG = collections.OrderedDict((

    ('general', collections.OrderedDict([
        ('editor', 'emacs'),
        ('acceptable_src_file_extensions',
            '.tar.xz .tar.lzma .tar.bz2 .tar.gz '
            '.txz .tlzma .tbz2 .tgz .7z .zip .jar .tar'),
        ('distro_buildout_dir', EMBEDDED_DISTRO_DIR),
        ('working_dir', ''),
        ])
     ),

    ('system_settings', collections.OrderedDict([
        ('system_title', 'LAILALO'),
        ('system_version', '4.0'),

        ('installed_pkg_dir', '/var/log/packages'),

        ('installed_pkg_dir_buildlogs', '${installed_pkg_dir}/buildlogs'),
        ('installed_pkg_dir_sums', '${installed_pkg_dir}/sums'),
        ('installed_pkg_dir_deps', '${installed_pkg_dir}/deps'),

        ('host', 'x86_64-pc-linux-gnu'),
        ('build', 'x86_64-pc-linux-gnu'),
        ('target', 'x86_64-pc-linux-gnu'),
        ('arch', 'x86_64-pc-linux-gnu'),
        ])
     ),

    ('src_server', collections.OrderedDict([
        ('host', 'localhost'),
        ('port', '8080'),
        ('working_dir', '${general:working_dir}'),
        ('tarball_repository_root', '${working_dir}/pkg_source'),
        ('src_index_db_config', 'sqlite:///${working_dir}/src_index.sqlite'),
        #('src_paths_index_db_config',
        #    'sqlite:///${working_dir}/src_paths_index.sqlite'),
        #('src_paths_json', '${working_dir}/src_paths.json'),
        ('xmpp_admins', 'animus@wayround.org'),
        ('xmpp_account', ''),
        ('xmpp_password', ''),
        ('acceptable_src_file_extensions',
            '${general:acceptable_src_file_extensions}')
        ])
     ),

    ('src_client', collections.OrderedDict([
        ('server_url', 'http://localhost:8080/'),
        ('acceptable_src_file_extensions',
            '${general:acceptable_src_file_extensions}')
        ])
     ),

    ('pkg_server', collections.OrderedDict([
        ('host', 'localhost'),
        ('port', '8081'),
        ('source_server_url', 'http://localhost:8080/'),
        ('working_dir', '${general:working_dir}'),
        ('snapshot_dir', '${working_dir}/pkg_snapshots'),
        ('repository_dir', '${working_dir}/pkg_repository'),
        ('repository_dir_index_db_config',
            'sqlite:///${working_dir}/pkg_index.sqlite'),
        ('garbage_dir', '${working_dir}/pkg_garbage'),
        ('info_json_dir', '${working_dir}/pkg_info'),
        ('info_db_config', 'sqlite:///${working_dir}/pkg_info.sqlite'),
        #('tags_db_config', 'sqlite:///${working_dir}/pkg_tags.sqlite'),
        ('tags_json', '${working_dir}/tags.json'),
        ('xmpp_admins', 'animus@wayround.org'),
        ('xmpp_account', ''),
        ('xmpp_password', ''),
        ('acceptable_src_file_extensions',
            '${general:acceptable_src_file_extensions}')
        ])
     ),

    ('pkg_client', collections.OrderedDict([
        ('server_url', 'http://localhost:8081/'),
        ('working_dir', '${general:working_dir}'),
        ('downloads_dir', '${working_dir}/downloads'),
        ('acceptable_src_file_extensions',
            '${general:acceptable_src_file_extensions}')
        ])
     ),

    ('local_build', collections.OrderedDict([
        ('working_dir', '${general:working_dir}'),
        ('building_sites_dir', '${working_dir}/b'),
        ('multiple_host_build', '${system_settings:host}'),
        ('multiple_arch_build', '${system_settings:host}'),
        ])
     ),

    ))


def load_config(filename):

    cfg = configparser.ConfigParser(
        interpolation=configparser.ExtendedInterpolation()
        )
#    cfg.read_dict(DEFAULT_CONFIG)
    try:
        cfg.read(filename)
    except:
        logging.exception("Error reading configuration file")
        cfg = None

    return cfg


def save_config(filename, config):

    if not isinstance(config, (configparser.ConfigParser, dict)):
        raise TypeError("config must be dict or configparser.ConfigParser")

    if isinstance(config, dict):
        cfg = configparser.ConfigParser()
        print("DEFAULT_CONFIG: \n{}".format(pprint.pformat(DEFAULT_CONFIG)))
        cfg.read_dict(DEFAULT_CONFIG)
        cfg.read_dict(config)
        config = cfg

    f = open(filename, 'w')
    config.write(f)
    f.close()

    return
