
"""
Build software before packaging
"""

import logging
import copy


import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.buildscript

def cli_name():
    return 'bd'

def exported_commands():
    return {
        'script': build_script,
        'complete': build_complete,
        }

def commands_order():
    return [
        'script',
        'complete'
        ]

def build_script(opts, args):

    ret = 0

    args_l = len(args)

    if args_l != 1:
        logging.error("one argument must be")
        ret = 1
    else:

        action = args[0]

        bs = '.'
        if '-b' in opts:
            bs = opts['-b']

        ret = start_building_script(bs, action)

    return ret



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


def complete(building_site):
    return start_building_script(building_site)


def start_building_script(building_site, action=None):
    package_info = org.wayround.aipsetup.buildingsite.read_package_info(
        building_site, ret_on_error=None
        )

    ret = 0

    if package_info == None:
        logging.error(
            "Error getting information "
            "from building site's(`{}') `package_info.json'".format(building_site)
            )
        ret = 1
    else:

        script = (
            org.wayround.aipsetup.buildscript.load_buildscript(
                package_info['pkg_info']['buildscript']
                )
            )

        if not isinstance(script, dict):
            logging.error("Some error while loading script")
            ret = 2
        else:

            ret = script['main'](building_site, action)

    return ret

def build_actions_selector(actions, action):

    continued_action = True

    if isinstance(action, str) and action.endswith('+'):
        continued_action = True
        action = action[:-1]
    else:
        continued_action = False

    if action in actions:

        action_pos = actions.index(action)

        if continued_action:
            actions = actions[action_pos:]
        else:
            actions = [actions[action_pos]]

    ret = (actions, action)

    return ret

def build_script_wrap(buildingsite, desired_actions, action, help_text):

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
            ret = 2
        else:

            r = org.wayround.aipsetup.build.build_actions_selector(
                actions,
                action
                )

            if isinstance(r, tuple):
                actions, action = r

            if action != None and not (isinstance(action, str) and isinstance(r, tuple)):
                logging.error("Wrong command")
                ret = 3
            else:

                if not isinstance(actions, list):
                    logging.error("Wrong action `{}' ({})".format(action, actions))
                    ret = 3

                else:

                    ret = (pkg_info, actions)

    return ret
