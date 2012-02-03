#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import os
import re
import aipsetup.utils
import shutil



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

def isWdDirRestricted(self):
    """This function is a rutine to check supplied dir is it suitable
    to be a working dir"""

    ret = False

    dirs_begining_with = [
        '/bin', '/boot' , '/daemons',
        '/dev', '/etc', '/lib', '/proc' ,
        '/sbin', '/sys',
        '/usr/bin', '/usr/sbin', '/usr/lib',
        '/usr/man', '/usr/share'
    ]

    exec_dirs = ['/opt', '/usr', '/var', '/']

    dir_str_abs = os.path.abspath(self.directory)

    for i in dirs_begining_with:
        if (re.match('^'+i, dir_str_abs) != None):
            ret = True
            break

    if not ret:
        for i in exec_dirs:
            if i == dir_str_abs:
                ret = True
                break
    return ret

def init(directory='build'):

    """Initiates pointed dir for farver usage. All contents is removed"""

    print '-i- initiating dir ' + directory

    if isWdDirRestricted(directory):
        print '-e- ' + dir_str + ' is restricted working dir'
        print '    won\'t init'
        return -1

    # if exists and not derictory - not continue
    print '-v- checking dir name safety'
    if ((os.path.exists(directory))
        and not os.path.isdir(directory)):
        print '-e- file already exists ant it is not a directory'
        return -2

    # remove all files and directories in initiating dir
    if (os.path.exists(directory)) and os.path.isdir(directory):
        print '-i- directory already exists. cleaning...'
        shutil.rmtree(directory)

    os.mkdir(directory)

    # create all subdirs
    # NOTE: probebly '/' in paths is not a problem, couse we
    #       working with GNU/Linux (maybe other UNIXes) only
    for i in DIR_ALL:
        a = aipsetup.utils.pathRemoveDblSlash(
            directory+'/' + i)
        if verbose:
            print '-v- creating directory ' + a
        os.makedirs(a)


    return 0

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
