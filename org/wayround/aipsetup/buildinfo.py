
"""
Perform actions on buildinfo scripts
"""

import org.wayround.aipsetup.info


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
