
import org.wayround.aipsetup.info


def help_text():
    return """\
{aipsetup} {command} command

    list [MASK]

    edit NAME
"""

def exported_commands():
    return {
        'list': buildinfo_list_files,
        'edit': buildinfo_edit_file
        }

def buildinfo_list_files(opts, args):
    return org.wayround.aipsetup.info.list_files(opts, args, 'buildinfo')

def buildinfo_edit_file(opts, args):
    return org.wayround.aipsetup.info.edit_file(opts, args, 'buildinfo')
