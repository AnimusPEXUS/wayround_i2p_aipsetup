
import os
import shutil
import sys
import inspect
import copy
import pprint

import aipsetup.info
import aipsetup.constitution
import aipsetup.utils
import aipsetup.name

DIR_TARBALL    = '00.TARBALL'
DIR_SOURCE     = '01.SOURCE'
DIR_PATCHES    = '02.PATCHES'
DIR_BUILDING   = '03.BUILDING'
DIR_DESTDIR    = '04.DESTDIR'
DIR_BUILD_LOGS = '05.BUILD_LOGS'
DIR_LISTS      = '06.LISTS'


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
    print """\
aipsetup build command

   init [-d=DIRNAME] [-v] [TARBALL1] [TARBALL2] .. [TARBALLn]

      Initiates new buildingsite under DIRNAME. If TARBALLs are given,
      they will be placed under TARBALL directory in new buildingsite.

         -d=DIRNAME set building directory name. DIRNAME defaults to
                    `tmp'

         -v - be verbose

   apply_info [-d=DIRNAME] TARBALL

      Apply package info to DIRNAME directory. Use TARBALL as name for
      parsing and farver package buildingsite configuration.

         -d=DIRNAME set building dir. Defaults to current working dir.


"""

def router(opts, args, config):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print "-e- not enough parameters"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()

        elif args[0] == 'init':

            init_dir = 'tmp'

            src_file = None

            for i in opts:
                if i[0] == '-d':

                    init_dir = i[1]

            verbose_option = False

            for i in opts:
                if i[0] == '-v':
                    verbose_option = True

            if args_l == 2:
                src_file = args[1]


            if isinstance(init_dir, basestring):

                ret = init(
                    directory=init_dir,
                    source_file=src_file,
                    verbose=verbose_option
                    )

                if ret != 0:
                    print "-e- Error initiating directory"

            else:
                print "-e- Wrong -d parameter"

        elif args[0] == 'apply_info':
            if args_l != 2:
                print "-e- tarball name to analize not specified"
            else:

                name = args[1]

                dirname = '.'

                for i in opts:
                    if i[0] == '-d':
                        dirname = i[1]

                apply_info(config, dirname, source_filename=name)

        else:
            print "-e- Wrong command"


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

def init(directory='build', source_file=None, verbose=False):

    """Initiates pointed dir for farver usage. All contents is removed"""

    ret = 0

    if verbose:
        print "-i- Initiating dir %(dir)s" % {
            'dir': directory
            }

    if verbose:
        print "-v- checking dir name safety"

    if isWdDirRestricted(directory):
        print "-e- %(dir_str)s is restricted working dir" % {
            'dir_str': directory
            }
        print "    won't init"
        ret = -1


    # if exists and not derictory - not continue
    if ret == 0:

        if ((os.path.exists(directory))
            and not os.path.isdir(directory)):
            print "-e- file already exists ant it is not a directory"
            ret = -2

    if ret == 0:

        # remove all files and directories in initiating dir
        if (os.path.exists(directory)) and os.path.isdir(directory):
            if verbose:
                print "-i- directory already exists. cleaning..."
            shutil.rmtree(directory)

        os.mkdir(directory)

        # create all subdirs
        for i in DIR_ALL:
            a = os.path.abspath(os.path.join(directory, i))
            if verbose:
                print "-v- creating directory " + a
            os.makedirs(a)

    if verbose:
        print "-v- copying source"

    if ret == 0:
        if source_file != None:
            if os.path.isdir(source_file):
                for i in glob.glob(os.path.join(source_file,'*')):
                    if os.path.isdir(i):
                        shutil.copytree(
                            i, os.path.join(
                                directory, DIR_SOURCE, os.path.basename(i)))
                    else:
                        shutil.copy2(
                            i, os.path.join(directory, DIR_SOURCE))
            elif os.path.isfile(source_file):
                shutil.copy(
                    source_file, os.path.join(directory, DIR_TARBALL))
            else:
                print "-e- file %(file)s - not dir and not file." % {
                    'file': source_file
                    }
                print "    skipping copy"

    return ret


def read_package_info(config, directory, ret_on_error=None):
    ret = ret_on_error

    pi_filename = os.path.join(directory, 'package_info.py')

    if not os.path.isfile(pi_filename):
        print "-e- `%(name)s' not found" % {
            'name': pi_filename
            }
    else:
        txt = ''
        f = None
        try:
            f = open(pi_filename, 'r')
        except:
            print "-e- Can't open `%(name)s'" % {
                'name': pi_filename
                }
            aipsetup.utils.print_exception_info(sys.exc_info())
        else:
            txt = f.read()
            f.close()

            g = {}
            l = {}

            try:
                ret = eval(txt, g, l)
            except:
                print "-e- error in `%(name)s'" % {
                    'name': pi_filename
                }
                aipsetup.utils.print_exception_info(sys.exc_info())
                ret = ret_on_error

    return ret

def write_package_info(config, directory, info):

    pi_filename = os.path.join(directory, 'package_info.py')

    f = None

    try:
        f = open(pi_filename, 'w')
    except:
        print "-e- can't open `%(file)s' for writing" % {
            'file': pi_filename
            }
        aipsetup.utils.print_exception_info(sys.exc_info())
    else:
        txt = ''
        try:
            txt=pprint.pformat(info)
        except:
            print "-e- can't represent data for package info"
            aipsetup.utils.print_exception_info(sys.exc_info())
        else:

            f.write("#!/usr/bin/python\n")
            f.write("# -*- coding: utf-8 -*-\n")

            f.write("\n")
            f.write("\n")

            f.write(txt)

        f.close()

    return


def apply_pkg_nameinfo_on_buildingsite(config, dirname, filename):

    d = read_package_info(config, dirname, ret_on_error={})

    d['pkg_nameinfo'] = None

    base = os.path.basename(filename)

    parse_result = aipsetup.name.source_name_parse(
        config, base,
        mute=False, modify_info_file=False
        )

    if parse_result == None:
        print "-e- Can't correctly parse file name"

    else:
        d['pkg_nameinfo'] = parse_result

    write_package_info(config, dirname, d)

    return



def apply_constitution_on_buildingsite(config, dirname):

    d = read_package_info(config, dirname, ret_on_error={})

    d['constitution'] = aipsetup.constitution.read_constitution(config)

    write_package_info(config, dirname, d)

    return


def apply_pkg_info_on_buildingsite(config, dirname):

    d = read_package_info(config, dirname, ret_on_error={})

    if not isinstance(d, dict) \
            or not 'pkg_nameinfo' in d \
            or not isinstance(d['pkg_nameinfo'], dict) \
            or not 'groups' in d['pkg_nameinfo'] \
            or not isinstance(d['pkg_nameinfo']['groups'], dict) \
            or not 'name' in d['pkg_nameinfo']['groups'] \
            or not isinstance(d['pkg_nameinfo']['groups']['name'],
                              basestring):


        print "-e- info undetermined"
        d['pkg_info'] = {}

    else:
        infoname = d['pkg_nameinfo']['groups']['name']

        info_filename = os.path.join(config['info'], '%(name)s.xml' % {
                'name': infoname
                })

        info = aipsetup.info.read_from_file(info_filename)
        if not isinstance(info, dict):
            print "-e- Can't read info from %(filename)s" % {
                'filename': info_filename
                }
            d['pkg_info'] = {}
        else:

            d['pkg_info'] = info
            # print repr(info)

    write_package_info(config, dirname, d)

    return


def apply_pkg_buildinfo_on_buildingsite(config, dirname):

    pi = read_package_info(config, dirname, ret_on_error={})

    if not isinstance(pi, dict) \
            or not 'pkg_info' in pi \
            or not isinstance(pi['pkg_info'], dict) \
            or not 'buildinfo' in pi['pkg_info'] \
            or not isinstance(pi['pkg_info']['buildinfo'], basestring):
        print "-e- buildinfo undetermined"
        pi['pkg_buildinfo'] = {}

    else:

        buildinfo_filename = os.path.join(
            config['buildinfo'], '%(name)s.py' % {
                'name': pi['pkg_info']['buildinfo']
                }
            )

        if not os.path.exists(buildinfo_filename) \
                or not os.path.isfile(buildinfo_filename):
            print "-e- Can't find buildinfo Python script `%(name)s'" % {
                'name': buildinfo_filename
                }
        else:

            g = {}
            l = {}

            try:
                execfile(buildinfo_filename, g, l)
            except:
                print "-e- Can't load buildinfo Python script `%(name)s'" % {
                    'name': buildinfo_filename
                    }
                utils.print_exception_info(sys.exc_info())
            else:

                if not 'build_info' in l \
                        or not inspect.isfunction(l['build_info']):

                    print "-e- Named module doesn't have 'build_info' function"

                else:

                    try:
                        l['build_info'](copy.copy(config), pi)
                    except:
                        print "-e- Error while calling for build_info() from `%(name)s'" % {
                            'name': buildinfo_filename
                            }
                        aipsetup.utils.print_exception_info(sys.exc_info())
                        pi['pkg_buildinfo'] = {}

    write_package_info(config, dirname, pi)

    # print repr(pi)

    return


def apply_info(config, dirname='.', source_filename=None):

    apply_pkg_nameinfo_on_buildingsite(config, dirname, source_filename)
    apply_constitution_on_buildingsite(config, dirname)
    apply_pkg_info_on_buildingsite(config, dirname)
    apply_pkg_buildinfo_on_buildingsite(config, dirname)

    return
