
"""
Perform actions on buildinfo scripts
"""

import os.path
import logging
import inspect

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config


def exported_commands():
    return {
        'list': buildinfo_list_files,
        'edit': buildinfo_edit_file
        }

def commands_order():
    return ['list', 'edit']

def buildinfo_list_files(opts, args):
    """
    List buildinfo files

    [FILEMASK]

    Default FILEMASK is *.py
    """
    return org.wayround.aipsetup.info.info_list_files(
        opts, args, 'buildinfo', mask='*.py'
        )

def buildinfo_edit_file(opts, args):
    """
    Edit buildinfo script

    FILENAME
    """
    return org.wayround.aipsetup.info.info_edit_file(opts, args, 'buildinfo')

def load_buildinfo(name):

    # FIXME: cleanup buildingsite module from analogical functionality

    ret = None

    buildinfo_filename = os.path.abspath(
        os.path.join(
            org.wayround.aipsetup.config.config['buildinfo'],
            '{}.py'.format(name)
            )
        )

    if not os.path.isfile(buildinfo_filename):
        logging.error(
            "Can't find buildinfo Python script `{}'".format(buildinfo_filename)
            )
        ret = 1

    else:

        txt = ''
        try:
            f = open(buildinfo_filename, 'r')
        except:
            logging.exception("Can't read file `{}'".foamrt(buildinfo_filename))
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
                        buildinfo_filename,
                        'exec'
                        ),
                    globals_dict,
                    locals_dict
                    )

            except:
                logging.exception("Can't load buildinfo Python script `%(name)s'" % {
                    'name': buildinfo_filename
                    })
                ret = 3

            else:

                if (
                    not 'build_info' in locals_dict
                    or
                    not inspect.isfunction(locals_dict['build_info'])
                    ):

                    logging.error(
                        "Module `{}' doesn't have function `build_info'".format(
                            buildinfo_filename
                            )
                        )
                    ret = 4

                else:

                    try:
#                        ret = module.build_info()
                        ret = locals_dict['build_info']()
                    except:
                        logging.exception(
                            "Error while calling for build_info() from `{}'".format(
                                buildinfo_filename
                                )
                            )
                        ret = 5

                    else:
                        logging.info(
                            "Retrieved building information from `{}'".format(
                                buildinfo_filename
                                )
                            )

    return ret
