
"""
Build software before packaging
"""

import logging


import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.buildscript



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
    pass


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
    return use_build_script(building_site, script_action=None)



def use_build_script(building_site, script_action=None):

    ret = 0

    script_action_started = True
    script_action_continuer = False

    # paranoid mood...
    if isinstance(script_action, str):
        if script_action.endswith('+'):
            script_action = script_action[-1:]
            script_action_started = False
            script_action_continuer = True
        else:
            script_action = script_action
            script_action_started = False
            script_action_continuer = False
    else:
        script_action = None
        script_action_started = True
        script_action_continuer = True


    package_info = org.wayround.aipsetup.buildingsite.read_package_info(
        building_site, ret_on_error=None
        )

    if package_info == None:
        logging.error(
            "Error getting information "
            "from building site's(`{}') `package_info.py'".format(building_site)
            )
        ret = 1
    else:
        buildscript_func = org.wayround.aipsetup.buildscript.load_buildscript(
            package_info['pkg_info']['buildscript']
            )

        buildscript = buildscript_func()

        for i in buildscript['actions']:
            if script_action and i['name'] == script_action:
                script_action_started = True

            if script_action_started:

                r = i['func'](building_site, i)
                if r != 0:
                    ret = r
                    break

            if script_action and (
                i['name'] != script_action and not script_action_continuer
                ):
                script_action_started = False

    return ret
