
import org.wayround.aipsetup.info


def router(opts, args):

    ret = org.wayround.aipsetup.router.router(
        opts, args, commands={
            'help': print_help,
            'list': list_files,
            'edit': edit_file
            }
        )

    return ret

def print_help(opts, args):
    print("""\
aipsetup build_info command

    list [MASK]

    edit NAME

""")

def list_files(opts, args):
    return org.wayround.aipsetup.info.list_files(opts, args, 'buildinfo')

def edit_file(opts, args):
    return org.wayround.aipsetup.info.edit_file(opts, args, 'buildinfo')
