
"""
Build software before packaging
"""

import os
import sys
import logging

import org.wayround.utils.log
import org.wayround.utils.error

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.buildtools


FUNCTIONS_LIST = [
    'extract',
    'configure',
    'build',
    'distribute',
    'prepack'
    ]

FUNCTIONS_SET = frozenset(FUNCTIONS_LIST)

FUNCTIONS_TEXTS_SET = {
    'extract': ('extractor', 'extracting', 'extraction'),
    'configure': ('configurer', 'configuring', 'configuration'),
    'build': ('builder', 'building', 'building'),
    'distribute': ('distributer', 'distributing', 'distribution'),
    'prepack': ('prepackager', 'prepackaging', 'prepackaging')
    }

def help_texts(name):

    ret = None

    if name == 'extract':
        ret = """\
Extract software source
"""

    elif name == 'configure':
        ret = """\
Configures software accordingly to info
"""

    elif name == 'build':
        ret = """\
Builds software accordingly to info
"""

    elif name == 'distribute':
        ret = """\
Creates normal software distribution
"""

    elif name == 'prepack':
        ret = """\
Do prepackaging actions
"""



    if isinstance(ret, str):
        ret = """\
{text}
    [DIRNAME]

    DIRNAME - set building site. Default is current directory
""".format(text=ret)

    return ret


def exported_commands():

    commands = {}

    for i in FUNCTIONS_SET:
        commands[i] = eval("build_{}".format(i))

    commands['complete'] = build_complete

    return commands

def commands_order():
    return ['complete'] + FUNCTIONS_LIST

def _build_x(opts, args, action):

    if not action in FUNCTIONS_SET:
        raise ValueError("Wrong action parameter")

    ret = 0

    dir_name = '.'
    args_l = len(args)


    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        ret = general_tool_function(action, dir_name)

    return ret

for i in FUNCTIONS_SET:
    exec("""\
def build_{name}(opts, args):
    return _build_x(opts, args, '{name}')

build_{name}.__doc__ = help_texts('{name}')
""".format(name=i))


def build_complete(opts, args):
    """
    Configures, builds, distributes and prepares software accordingly to info

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """

    ret = 0

    dir_name = '.'
    args_l = len(args)


    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        ret = complete(dir_name)

    return ret


def complete(dirname):
    ret = 0

    package_info = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, ret_on_error=None
        )

    if package_info == None:
        logging.error("Error reading package info from dir `{}'".format(dirname))
        ret = 1
    else:

        actions_sequance = []
        try:
            actions_sequance = package_info['pkg_buildinfo']['build_sequance']
        except:
            logging.exception("Can't get action sequence")
            ret = 2
        else:

            for i in actions_sequance:
                if not i in FUNCTIONS_LIST:
                    logging.error("Requested action `{}' not supported".format(i))
                    ret = 3
                    break

            if not 'build_tools' in package_info['pkg_buildinfo']:
                logging.error("No 'build_tools' in package_info['pkg_buildinfo']")
                ret = 4

            if ret == 0:
                for i in actions_sequance:
                    if not i in package_info['pkg_buildinfo']['build_tools']:
                        logging.error("`{}' not found in package_info['pkg_buildinfo']['build_tools']")
                        ret = 5
                        break

            if ret == 0:
                for i in list(package_info['pkg_buildinfo']['build_tools'].keys()):
                    tool_functions = (
                        org.wayround.aipsetup.buildtools.get_tool_functions(
                            package_info['pkg_buildinfo']['build_tools'][i]
                            )
                        )
                    if not isinstance(tool_functions, dict):
                        logging.error(
                            "Can't get tool `{}' functions".format(
                                package_info['pkg_buildinfo']['build_tools'][i]
                                )
                            )
                        ret = 7
                    else:
                        if not i in tool_functions:
                            logging.error(
                                "`{}' not found in `{}' exported functions".format(
                                    i, package_info['pkg_buildinfo']['build_tools'][i]
                                    )
                                )
                            ret = 6
                            break

            if ret == 0:
                for i in actions_sequance:
                    if general_tool_function(i, dirname) != 0:
                        logging.error("Building error on stage `{}'".format(i))
                        ret = 5
                        break

    return ret


def general_tool_function(action_name, dirname):

    process = FUNCTIONS_TEXTS_SET[action_name][2]
    whatdoes = FUNCTIONS_TEXTS_SET[action_name][1]

    ret = 0

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(dirname),
        process
        )

    log.info("=========[{}]=========".format(whatdoes.capitalize()))

    package_info = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, ret_on_error=None
        )

    if package_info == None:
        log.error("Error getting information about `{}'".format(process))
        ret = 1
    else:
        try:
            tool = package_info['pkg_buildinfo']['build_tools'][action_name]
        except:
            log.error(
                "Error getting tool name for function `{}'".format(action_name)
                )
            ret = 2

        else:

            tool_list = org.wayround.aipsetup.buildtools.list_build_tools()
            if not tool in tool_list:
                log.error(
                    ("Package desires `{}' tool which is not found by current aipsetup system".format(tool))
                    )
                ret = 3
            else:
                tool_functions = org.wayround.aipsetup.buildtools.get_tool_functions(tool)
                if not isinstance(tool_functions, dict):
                    logging.error(
                        "Can't get tool `{}' functions".format(
                            package_info['pkg_buildinfo']['build_tools'][i]
                            )
                        )
                else:
                    if not action_name in tool_functions or not callable(tool_functions[action_name]):
                        log.error("Function `{}' is not exported by `{}' tool".format(action_name, tool))
                        ret = 5
                    else:

                        if tool_functions[action_name](log, dirname) != 0:
                            log.error(
                                ("Tool {} could not perform {}".format(tool, process))
                                )
                            ret = 4
                        else:
                            log.info("{} complited".format(process.capitalize()))

    log.stop()

    return ret

