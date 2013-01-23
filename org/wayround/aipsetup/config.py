
"""
aipsetup configuration manipulations
"""

import os.path
import copy
import logging
import pprint

import org.wayround.utils.path

CONFIG_FULL_SAMPLE = {
    'editor'             : 'emacs',

    'unicorn_root'       : '/mnt/sda3/home/agu/_UNICORN',

    # non-configurable parameters -- always in unicorn root!!
    # also, unicorn root must be writable for aipsetup
    'constitution'       : '/mnt/sda3/home/agu/_UNICORN/system_constitution.py',
    'buildscript'        : '/mnt/sda3/home/agu/_UNICORN/pkg_buildscripts',
    'info'               : '/mnt/sda3/home/agu/_UNICORN/pkg_info',
    'server_files'       : '/mnt/sda3/home/agu/_UNICORN/server_files',
    'garbage'            : '/mnt/sda3/home/agu/_UNICORN/garbage',
    'snapshots'          : '/mnt/sda3/home/agu/_UNICORN/snapshots',
    'source_index'       : 'sqlite:////mnt/sda3/home/agu/_UNICORN/sources.sqlite',
    'tags'               : '/mnt/sda3/home/agu/_UNICORN/tags.json',

    # configurable
    'repository'         : '/mnt/sda3/home/agu/_UNICORN/pkg_repository',
    'source'             : '/mnt/sda3/home/agu/_UNICORN/pkg_source',
    'buildingsites'      : '/mnt/sda3/home/agu/_UNICORN/pkg_buildingsites',


    # other non-configurable
    'acceptable_src_file_extensions':['.tar.gz', '.tar.bz2', '.zip',
         '.7z', '.tgz', '.tar.xz', '.tar.lzma',
         '.tbz2'],

    # DB config
    'package_index_db_config'       : 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkgindex.sqlite',
    'package_info_db_config'        : 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkginfo.sqlite',
    'package_latest_db_config'      : 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkglatest.sqlite',
    'package_tags_db_config'        : 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkgtags.sqlite',



    # client and server config stuff

    # server is for serving localy
    'server_ip'          : '127.0.0.1',
    'server_port'        : '8005',
    'server_path'        : '/',
    'server_password'    : '123456789',

    # client is to designate remote server from which to catch updates
    # and other things
    'client_proto'       : 'http',
    'client_host'        : '127.0.0.1',
    'client_port'        : '8005',
    'client_path'        : '/',

    # this will be used relatively to install.py destdir parameters
    'installed_pkg_dir': '/var/log/packages',

    # this two are non-configurable and will be in `installed_pkg_dir' always
    'installed_pkg_dir_buildlogs': '/var/log/packages/buildlogs',
    'installed_pkg_dir_sums': '/var/log/packages/sums'
    }
"""
Full configuration sample. Parameters allowed to be configured through config
file are in list (set) :data:`CONFIG_ALLOWED_PARAMETERS`.

If You interested in subject of how nocconfigurable parameters are calculated,
see :func:`config_check_after_load` function source.
"""

CONFIG_ALL_PARAMETERS = frozenset(
    CONFIG_FULL_SAMPLE.keys()
    )
'all parameters set'

CONFIG_ALLOWED_PARAMETERS = frozenset([
    'editor',
    'unicorn_root',
    'repository',
    'tags',
    'source',
    'buildingsites',
    'package_index_db_config',
    'package_info_db_config',
    'package_latest_db_config',
    'package_tags_db_config',
    'server_ip',
    'server_port',
    'server_path',
    'server_password',
    'client_proto',
    'client_host',
    'client_port',
    'client_path',
    'installed_pkg_dir'
    ])
'allowed parameters set'

CONFIG_REQUIRED_PARAMETERS = CONFIG_ALLOWED_PARAMETERS
'all allowed parameters are all required parameters'

config = {}
"""
here aipsetup runtime configuration is stored. all modules uses it. it is loaded
at time of aipsetup initialization
"""


class ConfigParameterMissing(Exception): pass
class ConfigWrongParameter(Exception): pass
class ConfigCheckProgrammingError(Exception): pass
class ConfigSaveError(Exception): pass
class ConfigLoadError(Exception): pass



def exported_commands():
    """
    Part of aipsetup CLI interface
    """
    return {
        'check_config': config_check_config,
        'print_example': config_print_example,
        'print_config': config_print_config,
        }

def commands_order():
    """
    Part of aipsetup CLI interface
    """
    return [
        'check_config',
        'print_example',
        'print_config',
        ]

def cli_name():
    """
    Part of aipsetup CLI interface
    """
    return 'config'


def config_print_example(opts, args):
    """
    Print example aipsetup.conf file

    Interface for :func:`print_example_config`
    """

    print_example_config()

    return 0

def config_check_config(opts, args):
    """
    Check current configuration file (/etc/aipsetup.conf) and report errors

    :rtype: ``0`` - if no errors.

    uses :func:`check_config`
    """
    filename = '/etc/aipsetup.conf'

    if len(args) == 1:
        filename = args[0]

    ret = check_config(filename)

    return ret

def config_print_config(opts, args):
    """
    Print current configuration and calculated unconfigurable parameters
    """
    filename = '/etc/aipsetup.conf'

    if len(args) == 1:
        filename = args[0]

    ret = print_config(filename)

    return ret


def check_config(filename):
    """
    Checks named file is it truly aipsetup configuration file

    :rtype: ``0`` if no error
    """
    ret = 0
    try:
        load_config(filename)
    except:
        logging.exception("Configuration errors found")
        ret = 1
    else:
        logging.info("No configuration errors found")
        ret = 0
    return ret

def print_config(filename):
    """
    Prints current configuration and calculated unconfigurable parameters
    """
    ret = 0

    c = None

    try:
        c = load_config(filename)
    except:
        ret = 1
    else:

        print(format_config(c))
        cc = {}
        for i in CONFIG_ALL_PARAMETERS - CONFIG_ALLOWED_PARAMETERS:
            cc[i] = c[i]

        print("Additionally {} non-configurable parameters:".format(len(cc)))
        print(pprint.pformat(cc))

    return ret

def execution_fuse():
    ret = 0

    filename = '/etc/aipsetup.conf'

    if check_config(filename) != 0:
        ret = 1

    return ret

def format_config(config):
    """
    Formats and returns text for configuration described with config parameter
    """
    return """\
#!/usr/bin/python3

# This aipsetup config file, is a python dict record,
# example can be generated by command `aipsetup3.py config create_example'.

# See aipsetup config -- help for more info.

{{
    'editor'             : '{editor}',

    'unicorn_root'       : '{unicorn_root}',

    # client and server config stuff

    # server is for serving localy
    'server_ip'          : '{server_ip}',
    'server_port'        : '{server_port}',
    'server_path'        : '{server_path}',
    'server_password'    : '{server_password}',

    # client is to designate remote server from which to catch updates
    # and other things
    'client_proto'       : '{client_proto}',
    'client_host'        : '{client_host}',
    'client_port'        : '{client_port}',
    'client_path'        : '{client_path}',


    # this will be used relatively to install.py destdir parameters
    'installed_pkg_dir'  : '{installed_pkg_dir}',

    # where sources and complete packages retains
    'source'             : '{source}',
    'repository'         : '{repository}',

    # where to build stuff
    'buildingsites'      : '{buildingsites}',

    # tags.json
    'tags':              : '{tags}'


    # sql settings
    'package_index_db_config'    : '{package_index_db_config}',
    'package_info_db_config'     : '{package_info_db_config}',
    'package_latest_db_config'   : '{package_latest_db_config}',
    'package_tags_db_config'     : '{package_tags_db_config}'

 }}
""".format_map(config)

def print_example_config():
    """
    Prints example config file using :func:`format_config` function for it's
    formatting
    """

    print(format_config(copy.copy(CONFIG_FULL_SAMPLE)))

    return

def config_check_after_load(indict):
    """
    Configuration checker

    Configures non-configurable parameters

    Raises exceptions on wrong parameters

    Print info on wrong parameters
    """

    config_keys = list(indict.keys())

    for i in config_keys:
        if not i in CONFIG_ALLOWED_PARAMETERS:
            raise ConfigWrongParameter(
                "Wrong parameter `{paramname}'".format(
                    paramname=i
                    )
                )

    for i in CONFIG_REQUIRED_PARAMETERS:
        if not i in config_keys:
            raise ConfigParameterMissing(
                "Missing parameter `{paramname}'".format(
                    paramname=i
                    )
                )

    for i, j in [
        ('constitution'     , 'system_constitution.py'),
        ('buildscript'      , 'pkg_buildscripts'),
        ('info'             , 'pkg_info'),
        ('server_files'     , 'server_files'),
        ('tags'             , 'tags.json'),
        ('garbage'          , 'garbage'),
        ('snapshots'        , 'snapshots')
        ]:
        indict[i] = org.wayround.utils.path.abspath(
            os.path.join(indict['unicorn_root'], j)
            )

    for i, j in [
        ('source_index'    , 'sources.sqlite')
        ]:
        indict[i] = 'sqlite:///{path}'.format(
            path=org.wayround.utils.path.abspath(
                os.path.join(indict['unicorn_root'], j)
                )
            )

    for i, j in [
        ('installed_pkg_dir_buildlogs', 'buildlogs'),
        ('installed_pkg_dir_sums', 'sums')
        ]:
        indict[i] = org.wayround.utils.path.abspath(
            os.path.join(indict['installed_pkg_dir'], j)
            )

    indict['acceptable_src_file_extensions'] = copy.copy(
        CONFIG_FULL_SAMPLE['acceptable_src_file_extensions']
        )

    ck_set = set(list(indict.keys()))

    if not CONFIG_ALL_PARAMETERS == ck_set:
        raise ConfigCheckProgrammingError(
            """
Needed parameters:
{needed_parameters}

Provided parameters:
{settparameters}

Spare parameters:
{spare_parameters}

Missing parameters:
{missing_parameters}
""".format(
           needed_parameters=CONFIG_ALL_PARAMETERS,
           settparameters=ck_set,
           spare_parameters=ck_set - CONFIG_ALL_PARAMETERS,
           missing_parameters=CONFIG_ALL_PARAMETERS - ck_set
           )
            )

    return


def config_check_before_saving(indict):
    """
    Prepares config dict before it's saving to file
    """

    config_keys = list(indict.keys())

    for i in config_keys:
        if not i in CONFIG_ALLOWED_PARAMETERS:
            del indict[i]


def load_config(filename):
    """
    Loads configuration from named file and returns it as dict. Exception is
    raised in case of error.
    """
    ret = {}

    try:
        f = open(filename, 'r')
    except:
        raise Exception("Can't read config file {}".format(filename))
    else:
        try:
            text = f.read()

            conf_dict = {}

            try:
                conf_dict = eval(text, {}, {})
            except:
                raise Exception(
                    "Can't load config file contents {}".format(filename)
                    )
            else:
                try:
                    config_check_after_load(conf_dict)
                except:
                    raise Exception(
                        "Errors found while checking loadable config {}".format(
                            filename
                            )
                        )
                else:
                    ret = conf_dict

        finally:
            f.close()

    return ret




def save_config(filename, config):
    """
    Save configuration to named file

    Raise exception on error.
    """

    try:
        config_check_before_saving(config)
    except:
        raise Exception(
            "Errors found while checking loadable config {}".format(filename)
            )
    else:
        try:
            f = open(filename, 'w')
        except:
            raise
        else:
            f.write(format_config(config))

    return
