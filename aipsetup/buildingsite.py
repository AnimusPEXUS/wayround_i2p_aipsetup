# -*- coding: utf-8 -*-

import os
import shutil
import sys
import inspect
import copy
import pprint

import aipsetup.info
import aipsetup.constitution
import aipsetup.name
import aipsetup.build
import aipsetup.pack
import aipsetup.utils.log


DIR_TARBALL    = '00.TARBALL'
DIR_SOURCE     = '01.SOURCE'
DIR_PATCHES    = '02.PATCHES'
DIR_BUILDING   = '03.BUILDING'
DIR_DESTDIR    = '04.DESTDIR'
DIR_BUILD_LOGS = '05.BUILD_LOGS'
DIR_LISTS      = '06.LISTS'

i = None
for i in ['TARBALL',
          'SOURCE',
          'PATCHES',
          'BUILDING',
          'DESTDIR',
          'BUILD_LOGS',
          'LISTS']:
    exec("""\
def getDir_%(name)s(directory):
    '''
    Returns absolute path to DIR_%(name)s

    note: this method is generated dinamicly
    '''
    return os.path.abspath(
        os.path.join(
            directory,
            DIR_%(name)s)
        )
""" % {
            'name': i
            })

del(i)

DIR_ALL = [
    DIR_TARBALL,
    DIR_SOURCE,
    DIR_PATCHES,
    DIR_BUILDING,
    DIR_DESTDIR,
    DIR_BUILD_LOGS,
    DIR_LISTS
    ]
'All package directories list in proper order'

DIR_LIST = DIR_ALL
'DIR_ALL copy'


def print_help():
    print("""\
aipsetup buildingsite command

   init DIRNAME

      Make sure all required dirs under DIRNAME exists.

   apply_info [-d=DIRNAME] [TARBALL]

      Apply package info to DIRNAME directory. Use TARBALL as name for
      parsing and farver package buildingsite configuration.

         -d=DIRNAME set building dir. Defaults to current working dir.
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

        elif args[0] == 'init':

            init_dir = '.'

            if args_l > 1:
                init_dir = args[1]

            ret = init(
                config,
                directory = init_dir
                )


        elif args[0] == 'apply_info':
            if args_l != 2:
                print("-e- tarball name to analize not specified")
            else:

                name = args[1]

                dirname = '.'

                for i in opts:
                    if i[0] == '-d':
                        dirname = i[1]

                apply_info(config, dirname, source_filename=name)

        else:
            print("-e- Wrong command")


    return ret


def isWdDirRestricted(directory):
    """This function is a rutine to check supplied dir is it suitable
    to be a working dir"""

    ret = False

    dirs_begining_with = [
        '/bin',     '/boot' ,    '/daemons',
        '/dev',     '/etc',      '/lib',     '/proc',
        '/sbin',    '/sys',
        '/usr'
    ]

    exec_dirs = ['/opt', '/var', '/']

    dir_str_abs = os.path.abspath(directory)

    for i in dirs_begining_with:
        if dir_str_abs.startswith(i):
            ret = True
            break

    if not ret:
        for i in exec_dirs:
            if i == dir_str_abs:
                ret = True
                break
    return ret

def init(config, directory='build'):


    ret = 0

    directory = os.path.abspath(directory)

    print((
        "-i- Initiating building site %(dir)s" % {
            'dir': directory
            }
        ))

    print("-i- Checking dir name safety")

    if isWdDirRestricted(directory):
        print(("-e- %(dir_str)s is restricted working dir" % {
            'dir_str': directory
            }))
        print("    won't init")
        ret = -1


    # if exists and not derictory - not continue
    if ret == 0:

        if ((os.path.exists(directory))
            and not os.path.isdir(directory)):
            print("-e- File already exists and it is not a directory")
            ret = -2

    if ret == 0:

        if not os.path.exists(directory):
            print("-i- Building site not exists - creating")
            os.mkdir(directory)

        print("-i- Create all subdirs")
        for i in DIR_ALL:
            a = os.path.abspath(os.path.join(directory, i))

            if not os.path.exists(a):
                resh = 'creating'
            elif not os.path.isdir(a):
                resh = 'not a dir!'
            elif os.path.islink(a):
                resh = 'is a link!'
            else:
                resh = 'exists'

            print(("       %(dirname)s - %(resh)s" % {
                'dirname': i,
                'resh': resh
                }))

            if os.path.exists(a):
                pass
            else:
                os.makedirs(a)

    if ret == 0:
        print("-i- Init complite")
    else:
        print("-e- Init error")

    return ret


def read_package_info(config, directory, ret_on_error=None):
    ret = ret_on_error

    pi_filename = os.path.join(directory, 'package_info.py')

    if not os.path.isfile(pi_filename):
        print("-e- `%(name)s' not found" % {
            'name': pi_filename
            })
    else:
        txt = ''
        f = None
        try:
            f = open(pi_filename, 'r')
        except:
            print("-e- Can't open `%(name)s'" % {
                'name': pi_filename
                })
            aipsetup.utils.error.print_exception_info(
                sys.exc_info()
                )
        else:
            txt = f.read()
            f.close()

            g = {}
            l = {}

            try:
                ret = eval(txt, g, l)
            except:
                print("-e- error in `%(name)s'" % {
                    'name': pi_filename
                })
                aipsetup.utils.error.print_exception_info(
                    sys.exc_info()
                    )
                ret = ret_on_error

    return ret

def write_package_info(config, directory, info):

    pi_filename = os.path.join(directory, 'package_info.py')

    f = None

    try:
        f = open(pi_filename, 'w')
    except:
        print("-e- can't open `%(file)s' for writing" % {
            'file': pi_filename
            })
        aipsetup.utils.error.print_exception_info(
            sys.exc_info()
            )
    else:
        txt = ''
        try:
            txt = pprint.pformat(info)
        except:
            print("-e- can't represent data for package info")
            aipsetup.utils.error.print_exception_info(
                sys.exc_info()
                )
        else:

            f.write("#!/usr/bin/python\n")
            f.write("# -*- coding: utf-8 -*-\n")

            f.write("\n")
            f.write("\n")

            f.write(txt)

        f.close()

    return


def apply_pkg_nameinfo_on_buildingsite(config, dirname, filename):

    ret = 0

    d = read_package_info(config, dirname, ret_on_error={})

    d['pkg_nameinfo'] = None

    base = os.path.basename(filename)

    parse_result = aipsetup.name.source_name_parse(
        config, base,
        mute=False, modify_info_file=False
        )

    if parse_result == None:
        print("-e- Can't correctly parse file name")
        ret = 1
    else:
        d['pkg_nameinfo'] = parse_result

        write_package_info(config, dirname, d)

        ret = 0

    return ret



def apply_constitution_on_buildingsite(config, dirname):

    ret = 0

    d = read_package_info(config, dirname, ret_on_error={})

    const = aipsetup.constitution.read_constitution(config)

    if const == None:

        ret = 1

    else:

        d['constitution'] = const

        write_package_info(config, dirname, d)

        ret = 0

    return ret


def apply_pkg_info_on_buildingsite(config, dirname):

    ret = 0

    d = read_package_info(config, dirname, ret_on_error={})

    if not isinstance(d, dict) \
            or not 'pkg_nameinfo' in d \
            or not isinstance(d['pkg_nameinfo'], dict) \
            or not 'groups' in d['pkg_nameinfo'] \
            or not isinstance(d['pkg_nameinfo']['groups'], dict) \
            or not 'name' in d['pkg_nameinfo']['groups'] \
            or not isinstance(d['pkg_nameinfo']['groups']['name'],
                              str):


        print("-e- info undetermined")
        d['pkg_info'] = {}
        ret = 1

    else:
        infoname = d['pkg_nameinfo']['groups']['name']

        info_filename = os.path.join(config['info'], '%(name)s.xml' % {
                'name': infoname
                })

        print("-i- Reading info file `%(name)s'" % {
            'name': info_filename
            })
        info = aipsetup.info.read_from_file(info_filename)
        if not isinstance(info, dict):
            print("-e- Can't read info from %(filename)s" % {
                'filename': info_filename
                })
            d['pkg_info'] = {}
            ret = 2
        else:

            d['pkg_info'] = info
            # print repr(info)

            write_package_info(config, dirname, d)

            ret = 0

    return ret


def apply_pkg_buildinfo_on_buildingsite(config, dirname):

    ret = 0

    pi = read_package_info(config, dirname, ret_on_error={})

    if not isinstance(pi, dict) \
            or not 'pkg_info' in pi \
            or not isinstance(pi['pkg_info'], dict) \
            or not 'buildinfo' in pi['pkg_info'] \
            or not isinstance(pi['pkg_info']['buildinfo'], str):
        print("-e- buildinfo undetermined")
        pi['pkg_buildinfo'] = {}
        ret = 1

    else:

        buildinfo_filename = os.path.join(
            config['buildinfo'], '%(name)s.py' % {
                'name': pi['pkg_info']['buildinfo']
                }
            )

        if not os.path.exists(buildinfo_filename) \
                or not os.path.isfile(buildinfo_filename):
            print("-e- Can't find buildinfo Python script `%(name)s'" % {
                'name': buildinfo_filename
                })
            ret = 2

        else:

            g = {}
            l = {}

            try:
                exec(compile(open(buildinfo_filename).read(), buildinfo_filename, 'exec'), g, l)
            except:
                print("-e- Can't load buildinfo Python script `%(name)s'" % {
                    'name': buildinfo_filename
                    })
                aipsetup.utils.error.print_exception_info(
                    sys.exc_info()
                    )
                ret = 3

            else:

                if not 'build_info' in l \
                        or not inspect.isfunction(l['build_info']):

                    print("-e- Named module doesn't have 'build_info' function")
                    ret = 4

                else:

                    try:
                        l['build_info'](copy.copy(config), pi)
                    except:
                        print(("-e- Error while calling for "
                            +"build_info() from `%(name)s'") % {
                            'name': buildinfo_filename
                            })
                        aipsetup.utils.error.print_exception_info(
                            sys.exc_info()
                            )
                        pi['pkg_buildinfo'] = {}
                        ret = 5

                    else:

                        write_package_info(config, dirname, pi)

                        ret = 0

    return ret


def apply_info(config, dirname='.', source_filename=None):

    ret = 0

    if apply_pkg_nameinfo_on_buildingsite(
            config, dirname, source_filename
            ) != 0:
        ret = 1
    elif apply_constitution_on_buildingsite(config, dirname) != 0:
        ret = 2
    elif apply_pkg_info_on_buildingsite(config, dirname) != 0:
        ret = 3
    elif apply_pkg_buildinfo_on_buildingsite(config, dirname) != 0:
        ret = 4

    return ret


