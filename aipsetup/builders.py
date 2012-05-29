# -*- coding: utf-8 -*-

import aipsetup.utils.file

def print_help():
    print """\
aipsetup builders command

   list [MASK]

   copy NAME1 NAME2

   edit NAME

"""

def router(opts, args, config):

    ret = 0

    args_l = len(args)

    if args_l == 0:
        print "-e- command not given"
        ret = 1

    else:

        if args[0] == 'help':
            print_help()

        elif args[0] == 'list':
            mask = '*'

            if args_l > 2:
                print '-e- Too many parameters'
            else:

                if args_l > 1:
                    mask = args[1]

                aipsetup.utils.file.list_files(
                    config, mask, 'builders'
                )

        elif args[0] == 'edit':
            if args_l != 2:
                print "-e- builder to edit not specified"
            else:
                aipsetup.utils.edit.edit_file(config, args[1], 'builders')

        elif args[0] == 'copy':
            if args_l != 3:
                print "-e- wrong parameters count"
            else:

                aipsetup.utils.file.copy_file(config, args[1], args[2], 'builders')

        else:
            print "-e- wrong command. try aipsetup builders help"

    return ret

