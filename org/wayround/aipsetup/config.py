
"""
aipsetup configuration manipulations
"""

import configparser
import os.path
import logging
import collections

import org.wayround.utils.path


CUR_DIR = org.wayround.utils.path.abspath(os.path.dirname(__file__))
EMBEDDED_DISTRO_DIR = org.wayround.utils.path.join(
        CUR_DIR, 'distro'
        )


DEFAULT_CONFIG = collections.OrderedDict(
    [
     ('general', collections.OrderedDict([
        ('editor', 'emacs'),
        ('acceptable_src_file_extensions',
            '.tar.xz .tar.lzma .tar.bz2 .tar.gz '
            '.txz .tlzma .tbz2 .tgz .7z .zip .jar .tar'),
        ('distro_buildout_dir', EMBEDDED_DISTRO_DIR)
        ])
      ),

    ('system_settings', collections.OrderedDict([
        ('system_title', 'UNICORN'),
        ('system_version', '3.0'),

        ('installed_pkg_dir', '/var/log/packages'),

        ('installed_pkg_dir_buildlogs', '${installed_pkg_dir}/buildlogs'),
        ('installed_pkg_dir_sums', '${installed_pkg_dir}/sums'),
        ('installed_pkg_dir_deps', '${installed_pkg_dir}/deps'),

        ('host', 'i486-pc-linux-gnu'),
        ('build', 'i486-pc-linux-gnu'),
        ('target', 'i486-pc-linux-gnu')
        ])
     ),

    ('system_paths', collections.OrderedDict([
        ('root', '/'),
        ('usr', '/usr'),

        ('basic_bin', '/bin'),
        ('basic_sbin', '/sbin'),
        ('bin', '/usr/bin'),
        ('sbin', '/usr/sbin'),

        ('basic_lib', '/lib'),
        ('lib', '/usr/lib'),

        ('man', '/usr/share/man'),
        ('include', '/usr/include'),

        ('devices', '/dev'),
        ('config', '/etc'),
        ('daemons', '/daemons'),
        ('var', '/var'),
        ('temp', '/tmp')
        ])
     ),

    ('src_server', collections.OrderedDict([
        ('host', 'localhost'),
        ('port', '8080'),
        ('working_dir', '/mnt/sda3/home/agu/_UNICORN'),
        ('tarball_repository_root', '${working_dir}/pkg_source'),
        ('src_index_db_config', 'sqlite:///${working_dir}/src_index.sqlite'),
        ('src_paths_index_db_config',
            'sqlite:///${working_dir}/src_paths_index.sqlite'),
        ('src_paths_json', '${working_dir}/src_paths.json'),
        ('xmpp_admins', 'animus@wayround.org animus@wayround.org'),
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
        ('working_dir', '/mnt/sda3/home/agu/_UNICORN'),
        ('bundles_dir', '${working_dir}/pkg_bundles'),
        ('repository_dir', '${working_dir}/pkg_repository'),
        ('repository_dir_index_db_config',
            'sqlite:///${working_dir}/pkg_index.sqlite'),
        ('garbage_dir', '${working_dir}/pkg_garbage'),
        ('info_json_dir', '${working_dir}/pkg_info'),
        ('info_db_config', 'sqlite:///${working_dir}/pkg_info.sqlite'),
        ('tags_db_config', 'sqlite:///${working_dir}/pkg_tags.sqlite'),
        ('tags_json', '${working_dir}/tags.json'),
        ('xmpp_admins', 'animus@wayround.org animus@wayround.org'),
        ('xmpp_account', ''),
        ('xmpp_password', ''),
        ('acceptable_src_file_extensions',
            '${general:acceptable_src_file_extensions}')
        ])
     ),

    ('pkg_client', collections.OrderedDict([
        ('server_url', 'http://localhost:8081/'),
        ('working_dir', '/mnt/sda3/home/agu/_UNICORN'),
        ('downloads_dir', '${working_dir}/downloads'),
        ('acceptable_src_file_extensions',
            '${general:acceptable_src_file_extensions}')
        ])
     ),

    ('local_build', collections.OrderedDict([
        ('working_dir', '/mnt/sda3/home/agu/_UNICORN'),
        ('building_scripts_dir', '${working_dir}/pkg_buildscripts'),
        ('building_sites_dir', '${working_dir}/b')
        ])
     ),

#    ('server_package_repo', collections.OrderedDict([
#        ('base_dir', '${general:distro_buildout_dir}'),
#        ('index_db_config', 'sqlite:///${base_dir}/pkgindex.sqlite'),
#        ('dir', '${base_dir}/pkg_repository'),
#        ('snapshots_dir', '${base_dir}/snapshots'),
#        ('garbage_dir', '${base_dir}/garbage')
#        ])
#     ),
#
#    ('designer_settings', collections.OrderedDict([
#        ('base_dir', '${general:distro_buildout_dir}'),
#        ('index_db_config', 'sqlite:///${base_dir}/pkgindex.sqlite'),
#        ('dir', '${base_dir}/pkg_repository'),
#        ('snapshots_dir', '${base_dir}/snapshots'),
#        ('garbage_dir', '${base_dir}/garbage')
#        ])
#     ),
#
#    ('server_sources_repo', collections.OrderedDict([
#        ('base_dir', '${general:distro_buildout_dir}'),
#        ('index_db_config', 'sqlite:///${base_dir}/sources.sqlite'),
#        ('dir', '${base_dir}/pkg_source')
#        ])
#     ),
#
#    ('info_repo', collections.OrderedDict([
#        ('base_dir', '${general:distro_buildout_dir}'),
#        ])
#     ),
#
#    ('latest_repo', collections.OrderedDict([
#        ('base_dir', '${general:distro_buildout_dir}'),
#        ('index_db_config', 'sqlite:///${base_dir}/pkglatest.sqlite')
#        ])
#     ),
#
#    ('builder_repo', collections.OrderedDict([
#        ('base_dir', '${general:distro_buildout_dir}'),
#        ('building_scripts_dir', '${base_dir}/pkg_buildscripts'),
#        ('building_sites_dir', '${base_dir}/b')
#        ])
#     ),
#
#    ('web_server_config', collections.OrderedDict([
#        ('ip'          , '127.0.0.1'),
#        ('port'        , '8005'),
#        ('path_prefix' , '/')
#        ])
#     ),
#
#    ('web_client_config', collections.OrderedDict([
#        ('server_url'  , 'http://127.0.0.1:8005/')
#        ])
#     )

    ]
    )


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
        cfg.read_dict(DEFAULT_CONFIG)
        cfg.read_dict(config)
        config = cfg

    f = open(filename, 'w')
    config.write(f)
    f.close()

    return
