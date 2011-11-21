#!/usr/bin/python2.6
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import subprocess


def help():
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

def delete(name='temp.py', templatedir=os.path.expanduser('~/aipsetup/templates')):

    full_path = templatedir + '/' + name

    print '-i- deleting template ' + full_path
    try:
        os.unlink(full_path)
    except OSError as err:
        print '-e- can not remove file: ' + err.strerror
        return -1
    else:
        print '-i-  deleted'
        return 0

def edit(name='temp.py', editor='emacs', templatedir=''):

    full_path = templatedir + '/' + name

    print '-i- opening ' + full_path + ' with ' + editor
    try:
        subproc = subprocess.Popen(
            [
                editor,
                full_path
                ]
            )
    except:
        print '-e- can\'t start editor'
        return -1

    try:
        code = subproc.wait()
    except KeyboardInterrupt:
        print '\b\b-?- Interrupted by user. Editor will now be killed.'
        subproc.kill()
    else:
        print '-i- process exited with code: ' + str(code)
    return

def create(prototype='usr.py'):
    pass

def list(mask='*'):
    pass
