
"""
aipsetup configuration manipulations
"""

import os.path
import copy
import logging
import pprint


import org.wayround.utils.error

CONFIG_FULL_SAMPLE = {
    'editor'             : 'emacs',

    'unicorn_root'            : '/mnt/sda3/home/agu/_UNICORN',

    # non-configurable parameters -- always in unicorn root!!
    # also, unicorn root must be writable for aipsetup
    'constitution'       : '/mnt/sda3/home/agu/_UNICORN/system_constitution.py',
    'buildinfo'          : '/mnt/sda3/home/agu/_UNICORN/pkg_buildinfo',
    'buildtools'         : '/mnt/sda3/home/agu/_UNICORN/pkg_buildtools',
    'info'               : '/mnt/sda3/home/agu/_UNICORN/pkg_info',
    'repository_index'   : '/mnt/sda3/home/agu/_UNICORN/index_repository.lst',
    'source_index'       : '/mnt/sda3/home/agu/_UNICORN/index_source.lst',

    # configurable
    'repository'         : '/mnt/sda3/home/agu/_UNICORN/pkg_repository',
    'source'             : '/mnt/sda3/home/agu/_UNICORN/pkg_source',
    'buildingsites'      : '/mnt/sda3/home/agu/_UNICORN/pkg_buildingsites',


    # DB config
    'sqlalchemy_engine_string': 'sqlite:////mnt/sda3/home/agu/_UNICORN/pkgindex.sqlite',



    # client and server config stuff 

    # server is for serving localy
    'server_ip'          : '127.0.0.1',
    'server_port'        : '8005',
    'server_prefix'      : '/',
    'server_password'    : '123456789',

    # client is to designate remote server from which to catch updates 
    # and other things
    'client_proto'       : 'http',
    'client_host'        : '127.0.0.1',
    'client_port'        : '8005',
    'client_prefix'      : '/',

    # this will be used relatively to install.py destdir parameters
    'installed_pkg_dir': '/var/log/packages',

    # this two are non-configurable and will be in `installed_pkg_dir' always 
    'installed_pkg_dir_buildlogs': '/var/log/packages/buildlogs',
    'installed_pkg_dir_sums': '/var/log/packages/sums'
    }

CONFIG_ALL_PARAMETERS = frozenset(
    CONFIG_FULL_SAMPLE.keys()
    )

CONFIG_ALLOWED_PARAMETERS = frozenset([
    'editor',
    'unicorn_root',
    'repository',
    'source',
    'buildingsites',
    'sqlalchemy_engine_string',
    'server_ip',
    'server_port',
    'server_prefix',
    'server_password',
    'client_proto',
    'client_host',
    'client_port',
    'client_prefix',
    'installed_pkg_dir'
    ])

CONFIG_REQUIRED_PARAMETERS = CONFIG_ALLOWED_PARAMETERS

config = {}


class ConfigParameterMissing(Exception): pass
class ConfigWrongParameter(Exception): pass
class ConfigCheckProgrammingError(Exception): pass
class ConfigSaveError(Exception): pass
class ConfigLoadError(Exception): pass



def exported_commands():
    return {
        'create_example': config_create_example,
        'check_config': config_check_config,
        'print_config': config_print_config
        }

def commands_order():
    return [
        'create_example',
        'check_config',
        'print_config'
        ]


def config_create_example(opts, args):
    """
    Create example aipsetup.conf file -- /etc/aipsetup.conf.example
    """
    filename = '/etc/aipsetup.conf.example'

    if len(args) == 1:
        filename = args[0]

    ret = create_example_config(filename)

    return ret

def config_check_config(opts, args):
    """
    Check current configuration and report errors
    """
    filename = '/etc/aipsetup.conf'

    if len(args) == 1:
        filename = args[0]

    ret = check_config(filename)

    return ret

def config_print_config(opts, args):
    """
    Print current configuration
    """
    filename = '/etc/aipsetup.conf'

    if len(args) == 1:
        filename = args[0]

    ret = print_config(filename)

    return ret


def check_config(filename):
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
    c = load_config(filename)
    print(format_config(c))
    cc = {}
    for i in CONFIG_ALL_PARAMETERS - CONFIG_ALLOWED_PARAMETERS:
        cc[i] = c[i]

    print("Additionally {} non-configurable parameters:".format(len(cc)))
    print(pprint.pformat(cc))

def execution_fuse():
    ret = 0

    filename = '/etc/aipsetup.conf'

    if check_config(filename) != 0:
        ret = 1

    return ret

def format_config(config):
    return """\

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
    'server_prefix'      : '{server_prefix}',
    'server_password'    : '{server_password}',

    # client is to designate remote server from which to catch updates
    # and other things
    'client_proto'       : '{client_proto}',
    'client_host'        : '{client_host}',
    'client_port'        : '{client_port}',
    'client_prefix'      : '{client_prefix}',


    # this will be used relatively to install.py destdir parameters
    'installed_pkg_dir'  : '{installed_pkg_dir}',

    # where sources and complete packages retains
    'source'             : '{source}',
    'repository'         : '{repository}',

    # where to build stuff
    'buildingsites'      : '{buildingsites}',


    # sql settings
    'sqlalchemy_engine_string': '{sqlalchemy_engine_string}'

 }}
""".format_map(config)

def create_example_config(filename):
    logging.info("Saving example to `{}'".format(filename))
    save_config(filename, copy.copy(CONFIG_FULL_SAMPLE))

def config_check_after_load(indict):
    """
    Configuration checker

    Configures non-configurable parameters
    Error on wrong parameters
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
        ('constitution'    , 'system_constitution.py'),
        ('buildinfo'       , 'pkg_buildinfo'),
        ('buildtools'      , 'pkg_buildtools'),
        ('info'            , 'pkg_info'),
        ('repository_index', 'index_repository.lst'),
        ('source_index'    , 'index_source.lst')
        ]:
        indict[i] = os.path.abspath(
            os.path.join(indict['unicorn_root'], j)
            )

    for i, j in [
        ('installed_pkg_dir_buildlogs', 'buildlogs'),
        ('installed_pkg_dir_sums', 'sums')
        ]:
        indict[i] = os.path.abspath(
            os.path.join(indict['installed_pkg_dir'], j)
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
    Prepares config dict before saving
    """

    config_keys = list(indict.keys())

    for i in config_keys:
        if not i in CONFIG_ALLOWED_PARAMETERS:
            del indict[i]


def load_config(filename):
    ret = {}

    try:
        f = open(filename, 'r')
    except:
        logging.exception(
            "Can't read config file {}".format(filename)
            )
        raise
    else:
        try:
            text = f.read()

            conf_dict = {}

            try:
                conf_dict = eval(text, {}, {})
            except:
                logging.exception(
                    "Can't load config file contents {}".format(filename)
                    )
                raise
            else:
                try:
                    config_check_after_load(conf_dict)
                except:
                    logging.exception(
                        "Errors found while checking loadable config {}".format(filename)
                        )
                    raise
                else:
                    ret = conf_dict

        finally:
            f.close()

    return ret




def save_config(filename, config):

    try:
        config_check_before_saving(config)
    except:
        logging.exception("Errors found while checking loadable config {}".format(filename))
        raise
    else:
        try:
            f = open(filename, 'w')
        except:
            raise
        else:
            f.write(format_config(config))

