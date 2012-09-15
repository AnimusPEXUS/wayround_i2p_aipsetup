
"""
Perform actions on buildscript scripts
"""

import os.path
import logging
import inspect

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config


def exported_commands():
    return {
        'list': buildscript_list_files,
        'edit': buildscript_edit_file
        }

def commands_order():
    return ['list', 'edit']

def buildscript_list_files(opts, args):
    """
    List buildscript files

    [FILEMASK]

    Default FILEMASK is *.py
    """
    return org.wayround.aipsetup.info.info_list_files(
        opts, args, 'buildscript', mask='*.py'
        )

def buildscript_edit_file(opts, args):
    """
    Edit buildscript script

    FILENAME
    """
    return org.wayround.aipsetup.info.info_edit_file(opts, args, 'buildscript')

def load_buildscript(name):

    ret = None

    buildscript_filename = os.path.abspath(
        os.path.join(
            org.wayround.aipsetup.config.config['buildscript'],
            '{}.py'.format(name)
            )
        )

    if not os.path.isfile(buildscript_filename):
        logging.error(
            "Can't find buildscript Python script `{}'".format(buildscript_filename)
            )
        ret = 1

    else:

        txt = ''
        try:
            f = open(buildscript_filename, 'r')
        except:
            logging.exception("Can't read file `{}'".foamrt(buildscript_filename))
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
                logging.exception("Can't load buildscript Python script `%(name)s'" % {
                    'name': buildscript_filename
                    })
                ret = 3

            else:

                if (
                    not 'build_script' in locals_dict
                    or
                    not inspect.isfunction(locals_dict['build_script'])
                    ):

                    logging.error(
                        "Module `{}' doesn't have function `build_script'".format(
                            buildscript_filename
                            )
                        )
                    ret = 4

                else:

                    try:
#                        ret = module.build_script()
                        ret = locals_dict['build_script']()
                    except:
                        logging.exception(
                            "Error while calling for build_script() from `{}'".format(
                                buildscript_filename
                                )
                            )
                        ret = 5

                    else:
                        logging.info(
                            "Retrieved building information from `{}'".format(
                                buildscript_filename
                                )
                            )

    return ret
