
import os
import shutil
import sys
import inspect
import copy
# import json
import pprint

import aipsetup.info
import aipsetup.constitution
import aipsetup.utils

DIR_TARBALL    = '00.TARBALL'
DIR_SOURCE     = '01.SOURCE'
DIR_PATCHES    = '02.PATCHES'
DIR_BUILDING   = '03.BUILDING'
DIR_DESTDIR    = '04.DESTDIR'
DIR_BUILD_LOGS = '05.BUILD_LOGS'
DIR_LISTS      = '06.LISTS'
# DIR_OUTPUT     = '07.OUTPUT'

DIR_ALL = [
    DIR_TARBALL,
    DIR_SOURCE,
    DIR_PATCHES,
    DIR_BUILDING,
    DIR_DESTDIR,
    DIR_BUILD_LOGS,
    DIR_LISTS
    # DIR_OUTPUT
    ]
'All package directories list in proper order'

DIR_LIST = DIR_ALL
'DIR_ALL copy'


def print_help():
    print """\
aipsetup build command

   init [-d=DIRNAME] [-v] [TARBALL]

      -d=DIRNAME set building directory name. DIRNAME defaults to `tmp'

      -v - be verbose

      TARBALL, if sett - Copy TARBALL file right into package TARBALL
               dir

   apply_info [-d=DIRNAME] NAME

      Apply package info. NAME can be any file in pkg_info dir

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
                print "-e- buildinfo to apply not specified"
            else:

                name = args[1]

                dirname = '.'

                for i in opts:
                    if i[0] == '-d':
                        dirname = i[1]

                apply_info(config, name, dirname)


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

def apply_info(config, infoname, dirname='.'):

    info_filename = os.path.join(config['info'], '%(name)s.xml' % {
            'name': infoname
            })

    info = aipsetup.info.read_from_file(info_filename)
    if not isinstance(info, dict):
        print "-e- Can't read info from %(filename)s" % {
            'filename': info_filename
            }

    else:

        name = info['buildinfo']

        const = aipsetup.constitution.read_constitution(config)
        if not isinstance(const, dict):
            print "-e- Error getting constitution for farver configuration"
        else:

            buildinfodir = config['buildinfo']

            buildinfo_filename = os.path.join(buildinfodir, '%(name)s.py' % {
                    'name':name
                    })

            wfile = os.path.join(dirname, 'package_info.txt')

            if os.path.exists(wfile) and not os.path.isfile(wfile):
                print "-e- can't use %(file)s - remove it first" % {
                    'file': wfile
                    }

            else:

                if not os.path.exists(buildinfo_filename) \
                        or not os.path.isfile(buildinfo_filename):
                    print "-e- Can't find buildinfo module `%(name)s'" % {
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
                                d = l['build_info'](
                                    copy.copy(config), info, const)
                            except:
                                print "-e- Error while calling for build_info() in %(name)s " % {
                                    'name': buildinfo_filename
                                    }
                                aipsetup.utils.print_exception_info(sys.exc_info())

                            else:

                                f = None

                                try:
                                    f = open(wfile, 'w')
                                except:
                                    print "-e- can't open %(file)s for writing" % {
                                        'file': wfile
                                        }
                                    aipsetup.utils.print_exception_info(sys.exc_info())
                                else:
                                    txt = ''
                                    try:
                                        # txt = json.dumps(d)
                                        txt=pprint.pformat(d)
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
