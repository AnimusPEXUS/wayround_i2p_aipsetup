
"""
Build software before packaging
"""

import sys
import logging

import org.wayround.utils.log

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

def general_tool_function(action_name, dirname):

    process = FUNCTIONS_TEXTS_SET[action_name][2]
    whatdoes = FUNCTIONS_TEXTS_SET[action_name][1]

    ret = 0

    log = org.wayround.utils.log.Log(dirname, process)

    log.info("=========[{}]=========".format(whatdoes.capitalize()))

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, ret_on_error=None
        )

    if pi == None:
        log.error("Error getting information about `{}'".format(process))
        ret = 1
    else:
        try:
            tool = pi['pkg_buildinfo'][action_name]
        except:
            log.error("Error getting tool name for action `{}'".format(action_name))
            log.write(
                org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )
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
                tool_actions = org.wayround.aipsetup.buildtools.get_tool_functions(tool)
                if not action_name in tool_actions or not callable(tool_actions[action_name]):
                    log.error("`{}' action is not exported by `{}' tool".format(action_name, tool))
                    ret = 5
                else:

                    if tool_actions[action_name](log, dirname) != 0:
                        log.error(
                            ("Tool {} could not perform {}".format(tool, process))
                            )
                        ret = 4
                    else:
                        log.info("{} complited".format(process.capitalize()))

    log.stop()

    return ret

def complete(dirname):
    ret = 0

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, ret_on_error=None
        )

    if pi == None:
        logging.error("Error reading package info in dir {}".format(dirname))
        ret = 1
    else:

        act_seq = []
        try:
            act_seq = pi['pkg_buildinfo']['build_sequance']
        except:
            logging.exception("Can't get action sequence")
            ret = 2
        else:

            for i in act_seq:

                if not i in ['extract', 'configure',
                             'build', 'destribut',
                             'prepack']:
                    logging.error("Requested action not supported")
                    ret = 3
                else:

                    general_tool_function(i, dirname)
                    if eval("%(name)s(dirname)" % {
                            'name': i
                            }) != 0:
                        logging.error("Building error on stage {}".format(i))
                        ret = 5
                        break

    return ret
