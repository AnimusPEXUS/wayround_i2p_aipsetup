
import os
import os.path
import subprocess
import imp
import inspect
import copy
import pprint
import sys

import utils

def print_help():
    print """\
aipsetup build_info command

   list [MASK]

   copy NAME1 NAME2

   edit NAME

   apply [-d=.] NAME

      apply buildinfo NAME to dir pointed by -d

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

                utils.list_files(config, mask, 'buildinfo')


        elif args[0] == 'edit':

            if args_l != 2:
                print "-e- buildeinfo to edit not specified"
            else:
                utils.edit_file(config, args[1], 'buildinfo')

        elif args[0] == 'copy':

            if args_l != 3:
                print "-e- wrong parameters count"
            else:

                utils.copy_file(config, args[1], args[2], 'buildinfo')

        elif args[0] == 'apply':

            if args_l != 2:
                print "-e- buildinfo to apply not specified"
            else:

                name = args[1]

                dirname = '.'

                for i in opts:
                    if i[0] == '-d':
                        dirname = i[1]

                apply_buildinfo(config, name, dirname)

        else:
            print "-e- wrong command. try aipsetup buildinfo help"

    return ret

def apply_buildinfo(config, name, dirname='.'):

    buildinfodir = config['buildinfo']

    buildinfo_filename = os.path.join(buildinfodir, name)

    wfile = os.path.join(dirname, 'package_info.txt')

    if os.path.exists(wfile) and not os.path.isfile(wfile):
        print "-e- can't use %(file)s - remove it first" % {
            'file': wfile
            }

    else:

        if not os.path.exists(buildinfo_filename) \
                or not os.path.isfile(buildinfo_filename):
            print "-e- Can't find module `%(name)s'" % {
                'name': buildinfo_filename
                }
        else:

            module = None
            g = {}
            l = {}

            try:
                module = execfile(buildinfo_filename, g, l)
            except:
                print "-e- Can't load Python script `%(name)s'" % {
                    'name': buildinfo_filename
                    }
                utils.print_exception_info(sys.exc_info())
            else:

                # print repr(g)
                # print repr(l)

                if not 'build_info' in l \
                        or not inspect.isfunction(l['build_info']):

                    print "-e- Named module doesn't have 'build_info' function"

                else:
                    d = None
                    try:
                        d = l['build_info'](copy.copy(config))
                    except:
                        print "-e- Error while calling for build_info() in %(name)s " % {
                            'name': buildinfo_filename
                            }
                        utils.print_exception_info(sys.exc_info())

                    else:

                        f = None

                        try:
                            f = open(wfile, 'w')
                        except:
                            print "-e- can't open %(file)s for writing" % {
                                'file': wfile
                                }
                            utils.print_exception_info(sys.exc_info())
                        else:
                            txt = ''
                            try:
                                txt=pprint.pformat(d)
                            except:
                                print "-e- can't represent data for package info"
                                utils.print_exception_info(sys.exc_info())
                            else:

                                f.write(txt)

                            f.close()
            finally:
                pass
                # if not moduleinfo[0] == None:
                #     moduleinfo[0].close()
    return
