#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import os
import aipsetup.utils
import shutil
import glob



"""This class is for all building methods.

It is initiated with some dir, which may be not a working, but this class
must be able to check that dir, init it if required, Copy source there And
use pointed themplate for source building.

!! Packaging and downloading routines must be on other classes !!"""

DIR_TARBALL    = '00.TARBALL'
DIR_SOURCE     = '01.SOURCE'
DIR_PATCHES    = '02.PATCHES'
DIR_BUILDING   = '03.BUILDING'
DIR_DESTDIR    = '04.DESTDIR'
DIR_BUILD_LOGS = '05.BUILD_LOGS'
DIR_LISTS      = '06.LISTS'
DIR_OUTPUT     = '07.OUTPUT'

DIR_ALL = [
    DIR_TARBALL,
    DIR_SOURCE,
    DIR_PATCHES,
    DIR_BUILDING,
    DIR_DESTDIR,
    DIR_BUILD_LOGS,
    DIR_LISTS,
    DIR_OUTPUT
    ]


directory = ''

def print_help():
    print """\
aipsetup build command

   init

   apply_info

   extract

   patch

   configure

   make

   install

   pack

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

            for i in optilist:
                if i[0] == '-d':

                    init_dir = i[1]

            if args_l == 2:
                src_file = args[1]


            if isinstance(init_dir, basestring):

                ret = init(
                    directory=init_dir,
                    source_file=src_file,
                    verbose=verbose_option
                    )

                if ret != 0:
                    print '-e- Error initiating directory'

            else:
                print "-e- Wrong -d parameter"

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
        '/usr/bin', '/usr/sbin', '/usr/lib',
        '/usr/man', '/usr/share'
    ]

    exec_dirs = ['/opt', '/usr', '/var', '/']

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

def init(directory='build', source_file=False, verbose=False):

    """Initiates pointed dir for farver usage. All contents is removed"""

    ret = 0

    if verbose:
        print '-i- initiating dir ' + directory

    if isWdDirRestricted(directory):
        print '-e- %(dir_str)s is restricted working dir' % {
            'dir_str': dir_str
            }
        print "    won't init"
        ret = -1


    # if exists and not derictory - not continue
    if ret == 0:

        if verbose:
            print '-v- checking dir name safety'

        if ((os.path.exists(directory))
            and not os.path.isdir(directory)):
            print '-e- file already exists ant it is not a directory'
            ret = -2

    if ret == 0:

        # remove all files and directories in initiating dir
        if (os.path.exists(directory)) and os.path.isdir(directory):
            if verbose:
                print '-i- directory already exists. cleaning...'
            shutil.rmtree(directory)

        os.mkdir(directory)

        # create all subdirs
        # NOTE: probebly '/' in paths is not a problem, couse we
        #       working with POSIX only
        for i in DIR_ALL:
            a = aipsetup.utils.pathRemoveDblSlash(
                directory+'/' + i)
            if verbose:
                print '-v- creating directory ' + a
            os.makedirs(a)

    if verbose:
        print "-v- copying source"

    if ret == 0:
        if source_file != None:
            if os.path.isdir(source_file):
                for i in glob.glob(os.path.join(source_file,'*')):
                    if os.path.isdir(i):
                        shutil.copytree(
                            i, os.path.join(directory, DIR_SOURCE, os.path.basename(i)))
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

def set_instructions(settings, name, where='.'):

    '''copy building instructions to pointed dir'''

    ret = True

    if not os.path.isfile(os.path.join(settings['templates'], name)):
        print '-e- Such instructions not found in ' + settings['templates']

        ret = False

    else:

        try:
            shutil.copy(os.path.join(settings['templates'], name),
                        where)
        except:
            print '-e- Instructions copying error'
            ret = False

    if ret:
        print '-i- Copyed ' + name + ' to ' + where

    return ret
