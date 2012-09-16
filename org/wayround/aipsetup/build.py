
"""
Build software before packaging
"""

import os.path
import logging
import subprocess

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.buildscript
import org.wayround.aipsetup.config
import org.wayround.utils.log


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


def start_building_script(building_site, opts=None, args=None):
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

        script = (
            org.wayround.aipsetup.buildscript.load_buildscript(
                package_info['pkg_info']['buildscript']
                )
            )

#        buildscript_file = os.path.abspath(
#            org.wayround.aipsetup.config.config['buildscript'] +
#            os.path.sep +
#
#            )

        ret = script['main'](building_site, opts, args)

#        p = subprocess.Popen([buildscript_file], cwd=building_site)
#        ret = p.wait()

    return ret
