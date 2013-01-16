
"""
Build software before packaging

This module provides functions for building package using building script (see
:mod:`buildscript<org.wayround.aipsetup.buildscript>` module for more info on
building scripts)
"""

import logging
import copy

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.buildscript

import org.wayround.utils.path


def cli_name():
    """
    aipsetup CLI interface part
    """
    return 'bd'

def exported_commands():
    """
    aipsetup CLI interface part
    """
    return {
        's': build_script,
        'complete': build_complete,
        }

def commands_order():
    """
    aipsetup CLI interface part
    """
    return [
        's',
        'complete'
        ]

def build_script(opts, args):
    """
    Starts named action from script applied to current building site

    [-b=DIR] action_name
    
    -b - set building site
    
    if action name ends with + (plus) all remaining actions will be also started
    (if not error will occur)
    """

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
    """
    Run all building script commands on selected building site

    See :func:`start_building_script`
    """
    return start_building_script(building_site, action=None)


def start_building_script(building_site, action=None):
    """
    Run selected action on building site using particular building script.

    :param building_site: path to building site directory

    :param action: can be None or concrete name of action in building script.
        if action name ends with + (plus) all remaining actions will be also
        started (if not error will occur)

    :rtype: 0 - if no error occurred
    """


    building_site = org.wayround.utils.path.abspath(building_site)

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

            try:
                ret = script['main'](building_site, action)
            except KeyboardInterrupt:
                raise
            except:
                logging.exception(
                    "Error starting `main' function in `{}'".format(
                        package_info['pkg_info']['buildscript']
                        )
                    )
                ret = 3

    return ret


