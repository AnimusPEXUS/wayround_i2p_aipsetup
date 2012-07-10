
import sys
import logging

import org.wayround.utils.log

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.buildtools


FUNCTIONS = frozenset([
    'extract',
    'configure',
    'build',
    'distribute',
    'prepack'
    ])

FUNCTIONS_TEXTS_SET = {
    'extract': ('extractor', 'extracting', 'extraction'),
    'configure': ('configurer', 'configuring', 'configuration'),
    'build': ('builder', 'building', 'building'),
    'distribute': ('distributer', 'distributing', 'distribution'),
    'prepack': ('prepackager', 'prepackaging', 'prepackaging')
    }


def help_text():
    return """\
{aipsetup} {command} command

    extract [DIRNAME]

        Extract source in buildingsite which is baseo on DIRNAME.
        If DIRNAME not given assume current working dir.


    configure [SITEDIR]
       configures SITEDIR accordingly to info

    build [SITEDIR]
       builds SITEDIR accordingly to info

    install [SITEDIR]
       creates destdir in SITEDIR accordingly to info

    postinstall [SITEDIR]
       postinstallation processings for SITEDIR accordingly to info

    complite [SITEDIR]
       configures, builds and installs SITEDIR accordingly to info

 See also aipsetup pack help
"""




def router(opts, args):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        logging.error("Command Not Given")
        ret = 1
    else:


        if args[0] in list(FUNCTIONS):

            d = '.'

            if args_l > 1:
                d = args[1]

            ret = general_tool_function(args[0], d)

        elif args[0] == 'complete':

            d = '.'

            if args_l > 1:
                d = args[1]

            ret = complete(d)

        else:
            logging.error("Wrong Command")

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
            logging.error("Can't get action sequence")
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
