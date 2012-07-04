# -*- coding: utf-8 -*-

"""
Rutines to edit buildinfo files
"""

import org.wayround.utils.file
import org.wayround.utils.edit

def print_help():
    """
    print help
    """
    print("""\
aipsetup build_info command

   list [MASK]

   copy NAME1 NAME2

   edit NAME

""")

def router(opts, args, config):
    """
    aipsetup control router
    """

    ret = 0

    args_l = len(args)

    if args_l == 0:
        print("-e- command not given")
        ret = 1

    else:

        if args[0] == 'help':
            print_help()

        elif args[0] == 'list':

            mask = '*'

            if args_l > 2:
                print('-e- Too many parameters')
            else:

                if args_l > 1:
                    mask = args[1]

                org.wayround.utils.file.list_files(
                    config, mask, 'buildinfo'
                    )


        elif args[0] == 'edit':

            if args_l != 2:
                print("-e- buildeinfo to edit not specified")
            else:
                org.wayround.utils.edit.edit_file(
                    config, args[1], 'buildinfo'
                    )

        elif args[0] == 'copy':

            if args_l != 3:
                print("-e- wrong parameters count")
            else:

                org.wayround.utils.file.copy_file(
                    config, args[1], args[2], 'buildinfo'
                    )

        else:
            print("-e- wrong command. try aipsetup buildinfo help")

    return ret
