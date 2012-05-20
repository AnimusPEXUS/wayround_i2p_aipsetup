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


"""
This class is for all building methods.

It is initiated with some dir, which may be not a working, but this class
must be able to check that dir, init it if required, Copy source there And
use pointed themplate for source building.

!! Packaging and downloading routines must be on other classes !!
"""


def print_help():
    print """\
aipsetup build command

   extract [DIRNAME]

      Extract source in buildingsite DIRNAME. If DIRNAME not given
      assume current working dir.

   patch

   configure

   build

   install

   prepack

   compress

   decompress

   pack

   unpack

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

        elif args[0] == 'configure':

            d = '.'

            if args_l > 1:
                d = args[1]

            configure(config, d)

        elif args[0] == 'build':

            d = '.'

            if args_l > 1:
                d = args[1]

            build(config, d)

        elif args[0] == 'install':

            d = '.'

            if args_l > 1:
                d = args[1]

            install(config, d)

        elif args[0] == 'prepack':

            d = '.'

            if args_l > 1:
                d = args[1]

            prepack(config, d)


        elif args[0] == 'pack':

            d = '.'

            if args_l > 1:
                d = args[1]

            pack(config, d)

        else:
            print "-e- Wrong build command"


    return ret

def extract(config, dirname):

    print "-i- =========[extracting]========="

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

                print "-i- extraction complited"

    return

def configure(config, dirname):

    print "-i- =========[configuring]========="

    pi = aipsetup.buildingsite.read_package_info(
        config, dirname, ret_on_error=None)

    if pi == None:
        print "-e- Error getting information about configuring"
    else:
        try:
            configurer = pi['pkg_buildinfo']['configurer']
        except:
            print "-e- Error getting configurer name"
            aipsetup.utils.print_excetption_info(sys.exc_info())

        else:
            if not configurer in ['autotools']:
                print "-e- Package desires configurer not supported by"
                print "    current aipsetup system"
            else:
                eval("aipsetup.tools.%(toolname)s.configure(config, dirname)" % {
                        'toolname': configurer
                        })

    return

def build(config, dirname):

    print "-i- =========[building]========="

    pi = aipsetup.buildingsite.read_package_info(
        config, dirname, ret_on_error=None)

    if pi == None:
        print "-e- Error getting information about making"
    else:
        try:
            builder = pi['pkg_buildinfo']['builder']
        except:
            print "-e- Error getting builder name"
            aipsetup.utils.print_excetption_info(sys.exc_info())

        else:
            if not builder in ['autotools']:
                print "-e- Package desires builder not supported by"
                print "    current aipsetup system"
            else:
                eval("aipsetup.tools.%(toolname)s.build(config, dirname)" % {
                        'toolname': builder
                        })

    return


def install(config, dirname):

    print "-i- =========[installing]========="

    pi = aipsetup.buildingsite.read_package_info(
        config, dirname, ret_on_error=None)

    if pi == None:
        print "-e- Error getting information about installing"
    else:
        try:
            installer = pi['pkg_buildinfo']['installer']
        except:
            print "-e- Error getting installer name"
            aipsetup.utils.print_excetption_info(sys.exc_info())

        else:
            if not installer in ['autotools']:
                print "-e- Package desires installer not supported by"
                print "    current aipsetup system"
            else:
                eval("aipsetup.tools.%(toolname)s.install(config, dirname)" % {
                        'toolname': installer
                        })

    return

def postinstall(config, dirname):
    return

def pack(config, dirname):
    return
