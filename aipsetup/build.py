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


def print_help():
    print """\
aipsetup build command

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

        else:
            print "-e- Wrong command"


    return ret





