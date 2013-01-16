
"""
Perform actions on building scripts

List them or edit with editor configured in aipsetup config file.
"""

import copy
import logging
import os.path

import org.wayround.utils.path

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config


def exported_commands():
    """
    aipsetup CLI interface part
    """
    return {
        'list': buildscript_list_files,
        'edit': buildscript_edit_file
        }

def commands_order():
    """
    aipsetup CLI interface part
    """
    return ['list', 'edit']

def cli_name():
    """
    aipsetup CLI interface part
    """
    return 'sc'


def buildscript_list_files(opts, args):
    """
    List building scripts files
    """
    return org.wayround.aipsetup.info.info_list_files(
        opts, args, 'buildscript', mask='*.py'
        )

def buildscript_edit_file(opts, args):
    """
    Edit building script

    FILENAME
    """
    return org.wayround.aipsetup.info.info_edit_file(opts, args, 'buildscript')


def load_buildscript(name):
    """
    Loads building script with exec function and returns it's global dictionary.
    ``None`` is returned in case of error.
    """

    ret = None

    buildscript_filename = org.wayround.utils.path.abspath(
        os.path.join(
            org.wayround.aipsetup.config.config['buildscript'],
            '{}.py'.format(name)
            )
        )

    if not os.path.isfile(buildscript_filename):
        logging.error(
            "Can't find building script `{}'".format(buildscript_filename)
            )
        ret = 1

    else:

        txt = ''
        try:
            f = open(buildscript_filename, 'r')
        except:
            logging.exception(
                "Can't read file `{}'".format(buildscript_filename)
                )
            ret = 2
        else:
            txt = f.read()
            f.close()

            globals_dict = {}
            locals_dict = globals_dict

            try:
                exec(
                    compile(
                        txt,
                        buildscript_filename,
                        'exec'
                        ),
                    globals_dict,
                    locals_dict
                    )

            except:
                logging.exception(
                    "Can't load building script `{}'".format(
                        buildscript_filename
                        )
                    )
                ret = 3

            else:

                try:
                    ret = globals_dict
                except:
                    logging.exception(
                        "Error while calling for build_script() from `{}'".format(
                            buildscript_filename
                            )
                        )
                    ret = 5

                else:
                    logging.info(
                        "Loaded building script: `{}'".format(
                            buildscript_filename
                            )
                        )

    return ret


def build_script_wrap(buildingsite, desired_actions, action, help_text):
    """
    Used by building scripts for parsing action command

    :param buildingsite: path to building site
    :param desired_actions: list of possible actions
    :param action: action selected by building script user
    :param help_text: if action == 'help', help_text is text to show before list
        of available actions
    :rtype: ``int`` if error. ``tuple`` (package_info, actions), where
        ``package_info`` is package info readen from building site package info
        file, ``actions`` - list of actions, needed to be run by building script
    """

    pkg_info = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite
        )

    ret = 0

    if not isinstance(pkg_info, dict):
        logging.error("Can't read package info")
        ret = 1
    else:

        actions = copy.copy(desired_actions)

        if action == 'help':
            print(help_text)
            print("")
            print("Available actions: {}".format(actions))
            ret = 2
        else:

            r = build_actions_selector(
                actions,
                action
                )

            if not isinstance(r, tuple):
                logging.error("Wrong command 1")
                ret = 2
            else:

                actions, action = r

                if action != None and not isinstance(action, str):
                    logging.error("Wrong command 2")
                    ret = 3
                else:

                    if not isinstance(actions, list):
                        logging.error("Wrong command 3")
                        ret = 3

                    else:

                        ret = (pkg_info, actions)

    return ret

def build_actions_selector(actions, action):
    """
    Used by :func:`build_script_wrap` to build it's valid return action list

    :rtype: ``None`` if error. tuple (actions, action), where ``action = None`` if
        ``action == 'complete'``. If ``action == 'help'``, both values returned
        without changes. If action is one of actions, ``actions = [action]``. If
        action is one of actions and action ends with + sign, ``actions =
        actions[(action position):]``
    """

    ret = None

    actions = copy.copy(actions)

    if action == 'complete':
        action = None

    # action == None - indicates all actions! equals to 'complete'
    if action in [None, 'help']:
        ret = (actions, action)

    else:

        continued_action = True

        if isinstance(action, str) and action.endswith('+'):

            continued_action = True
            action = action[:-1]

        else:
            continued_action = False

        # if not action available - return error
        if not action in actions:

            ret = 2

        else:

            action_pos = actions.index(action)

            if continued_action:
                actions = actions[action_pos:]
            else:
                actions = [actions[action_pos]]

            ret = (actions, action)

    return ret
