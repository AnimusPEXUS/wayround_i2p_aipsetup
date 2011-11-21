#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import re
import sys
import shutil
import getopt
import uuid
import aipsetup_utils
import aipsetup_builder


# protect module from being run as script
aipsetup_utils.module_run_protection(__name__)

module_name = __name__
module_group = 'build'
module_modes = ['build']
module_help = \
    ur"""This mode is for preparing source, building source and
    preparing files for building deployment package"""

aipsetup_utils.update_modules_data(
    module_name, module_group, module_modes, module_help)

def help():
    print ur"""
 This module purpuse is source preparing, building and
 bla,bla,bla...

    aipsetup -m build -c command [-d dir] [-f file] [-t template]

    options are following:

     -c command         One of the commands below.

     -d dir             Working dir.
                        If dir is 'auto' (which is default) - automatically
                        choose name for it.
                        If -d is not used, then current dir will
                        be attempted to use (except for wd command).
                        ('auto' works only with wd command).

     -f file            Input file (see commands descriptions)

     -t template        Force this template usage for doing things.
                        (read more about templates below)


     commands used with -c option
     --------

     info         Info on working dir
                       -d must be used

     init         Prepare complite working dir.
                  (WARNING: if -d is not 'auto' and does exists,
                            then all it's contents will be deleted!)
                       -d must be used

     cp           Place tarball to working dir.
                       -d must be used
                       -f must be used

     person       Personalize working dir for source.
                  If -t used, then farther processes to this dir
                  will be done using template pointed by -t.
                  If -t is not used, then attempt to gues will be done
                  based on internal aipsetup's Package Info System.
                       -d must be used
                       -t can be used

     e_src        Clean source dir in working dir and
                  extract source there. ('e' means extract)
                       -d must be used

     p_src        Patch source with patch files places in
                  patches dir.
                       -d must be used
                       -t can be used

     b_src        Build source.
                       -d must be used
                       -t can be used



     About how things done
     ---------------------

First of all, you need a temporary dir. init mode can be used for it's
createon.

Next you need to copy tarball to working dir. cp mode can be used
here.


"""
    return

def run(aipsetup_config,
        arguments = []):

    try:
        optilist, args = getopt.getopt(arguments,
                                   'd:c:f:',
                                   ['help'])
    except getopt.GetoptError, e:
        print '-e- Error while parsing parameters: ' + e.msg
        return -1

    for i in optilist:
        if i[0] == '--help':
            help()
            exit (0)

    d_sett = False
    d_sett_mean = '.'
    c_sett = False
    c_sett_mean = 'none'
    f_sett = False
    f_sett_mean = ''

    for i in optilist:
        if i[0] == '-d':
            d_sett = True
            d_sett_mean = i[1]

        if i[0] == '-c':
            c_sett = True
            c_sett_mean = i[1]

        if i[0] == '-f':
            f_sett = True
            f_sett_mean = i[1]

    if d_sett:
        if isWdDirRestricted(d_sett_mean):
            print '-e- Selected dir (' + os.path.abspath(d_sett_mean) \
                + ') is Restricted to be used as working dir'
            return -1

    if c_sett:
        if c_sett_mean == 'none':
            help()
            return 0

        if c_sett_mean == 'init':
            wd = ''
            if not d_sett:
                if isWdDirValid('.'):
                    wd = '.'
                else:
                    wd = 'auto'
            elif d_sett_mean == 'auto':
                wd = 'auto'
            else:
                wd = d_sett_mean

            if wd == 'auto':
                wd = 'aipsetup-wd-' + uuid.uuid4().hex

                while os.path.exists(wd):
                    wd = 'aipsetup-wd-' + uuid.uuid4().hex


            if not isWdDirRestricted(wd):
                print wd
                initWdDir(wd)

            return 0

        if c_sett_mean == 'cp':
            if not d_sett:
                print '-e- -d must be sett'
                return -1

            if not f_sett:
                print '-e- -f must be sett'
                return -2

            if not os.path.isdir(d_sett_mean):
                print '-e- ' + d_sett_mean + ' is not a dir'
                return -3

            if not isWdDirValid(d_sett_mean):
                print '-e- ' + d_sett_mean + ' is not a valid dir'
                return -4

            if not os.path.isfile(f_sett_mean):
                print '-e- -f must be a file'
                return -5
            try:
                shutil.copy(f_sett_mean, d_sett_mean + '/00.TARBALL')
            except:
                print '-e- can\'t copy file: '
                print sys.exc_info()
                return -6

            print '-i- copyed source file'
            return 0

        print '-e- wrong -c command given'
        return -1
    else:
        print '-e- -c must be specified'
        return -1

    return 0



def isWdDirValid(dir_str):
    if isWdDirRestricted(dir_str):
        print '-e- ' + dir_str + ' is restricted working dir'
        print '    won\'t init'
        return False

    if (not os.path.isdir(dir_str)):
        return False

    if not os.path.isdir(pathRemoveDblSlash(dir_str+'/00.TARBALL')) or \
            not os.path.isdir(pathRemoveDblSlash(dir_str+'/01.SOURCE')) or \
            not os.path.isdir(pathRemoveDblSlash(dir_str+'/02.PATCH')) or \
            not os.path.isdir(pathRemoveDblSlash(dir_str+'/03.BUILD')) or \
            not os.path.isdir(pathRemoveDblSlash(dir_str+'/04.FS_ROOT')) or \
            not os.path.isdir(pathRemoveDblSlash(dir_str+'/05.LOGS')) or \
            not os.path.isdir(pathRemoveDblSlash(dir_str+'/06.LISTS')) or \
            not os.path.isdir(pathRemoveDblSlash(dir_str+'/07.PACKAGE')):
        return False

    return True
