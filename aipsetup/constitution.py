
import inspect
import sys

import aipsetup.utils


def print_help():
    print("""\
aipsetup build command

   edit   edit constitution file

   view   view constitution file

""")

def router(opts, args, config):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print("-e- not enough parameters")
        ret = 1
    else:

        if args[0] == 'help':
            print_help()

        elif args[0] == 'edit':
            aipsetup.utils.edit.edit_file_direct(
                config, config['constitution']
                )

        elif args[0] == 'view':

            f = open(config['constitution'], 'r')
            txt = f.read()
            f.close()

            print(txt)

        else:
            print("user --help")

    return ret


def read_constitution(config):

    ret = None

    l = {}
    g = {}

    try:
        exec(compile(open(config['constitution']).read(), config['constitution'], 'exec'), g, l)
    except:
        print("-e- Error loading constitution script")
        aipsetup.utils.error.print_exception_info(
            sys.exc_info()
            )
    else:
        if not 'constitution' in l \
                or not inspect.isfunction(l['constitution']):
            print("-e- `%(name)s' has no `constitution' function" % {
                'name': config['constitution']
                })

        else:
            try:
                ret = l['constitution'](config)
            except:
                ret = None
                print("-e- Error calling for constitution dict")
                aipsetup.utils.error.print_exception_info(
                    sys.exc_info()
                    )

    return ret
