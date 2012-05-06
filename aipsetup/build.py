#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os.path
import os
import shutil
import glob

import aipsetup.utils
import aipsetup.buildingsite
import aipsetup.tools.autotools


"""This class is for all building methods.

It is initiated with some dir, which may be not a working, but this class
must be able to check that dir, init it if required, Copy source there And
use pointed themplate for source building.

!! Packaging and downloading routines must be on other classes !!"""


def print_help():
    print """\
aipsetup build command

   extract [DIRNAME]

      Extract source in buildingsite DIRNAME. If DIRNAME not given
      assume current working dir.

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

        elif args[0] == 'extract':

            d = '.'

            if args_l > 1:
                d = args[1]

            extract(config, d)

        else:
            print "-e- Wrong command"


    return ret

def extract(config, dirname):

    pi = aipsetup.buildingsite.read_package_info(
        config, dirname, ret_on_error=None)

    if pi == None:
        print "-e- Error getting information about extraction"
    else:
        try:
            extractor = pi['pkg_buildinfo']['extractor']
        except:
            print "-e- Error getting extractor name"
            aipsetup.utils.print_excetption_info(sys.exc_info())

        else:
            if not extractor in ['autotools']:
                print "-e- Package desires extractor not supported by"
                print "    current aipsetup system"
            else:
                eval("aipsetup.tools.%(toolname)s.extract(config, dirname)" % {
                        'toolname': extractor
                        })

    return
