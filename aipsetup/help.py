#!/usr/bin/python

import os.path
import sys

def main_help():
    print """
  usage: """+os.path.basename(sys.argv[0:1][0])+""" mode [--help] [--version]


    --version       show version info
    --help          show this help message

    mode         mode (see below)
"""
    return

def build_help():
    print ur'''
 This mode purpuse is source preparing, building and
 bla,bla,bla...

    aipsetup build -c command [-d dir] [-f file] [-t template]

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

'''
    return

def template_help():
    print ur"""
 This mode accepts only one argument - themplate name.
 Without argument, error will be displayed.

    options are following:

     -d              delete template
     -t template     use `template' as prototype, not `usr'.
                     WARNING: this also deletes template you've
                              selected to edit
     -e editor       open template with named editor

     -l | --list     list templates

     default         template editing


 -d, -t, -m and -l are not compatible. -e usefull only with -m option.
 -m, -d and -m takes only one argument - template to work with
 -l doesn't allow any arguments with this aipsetup mode
"""
    return
