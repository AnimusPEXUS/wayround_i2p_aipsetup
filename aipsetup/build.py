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

"""

def router(opts, args, config):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print "-e- Command not given. See `aipsetup build help'"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()

        elif args[0] in ['extract', 'configure',
                         'build', 'install',
                         'complite']:

            d = '.'

            if args_l > 1:
                d = args[1]

            ret = eval(
                "%(name)s(config, d)" % {
                    'name': args[0]
                    }
                )

        else:
            print "-e- Wrong build command"


    return ret

def _same_function(config, dirname, actor_name, function, whatdoes, process):

    ret = 0

    log = aipsetup.utils.Log(config, dirname, process)
    # log.write("-i- Closing this log now, cause it can't be done farther")

    log.write("-i- =========[%(whatdoes)s]=========" % {
        'whatdoes': whatdoes.capitalize()
        })

    pi = aipsetup.buildingsite.read_package_info(
        config, dirname, ret_on_error=None)

    if pi == None:
        log.write("-e- Error getting information about %(process)s" % {
                'process': process
                })
        ret = 1
    else:
        try:
            actor = pi['pkg_buildinfo'][actor_name]
        except:
            log.write("-e- Error getting %(actor_name)s name" % {
                    'actor_name': actor_name
                    })
            log.write(aipsetup.utils.return_excetption_info(sys.exc_info()))
            ret = 2

        else:
            if not actor in ['autotools']:
                log.write("-e- Package desires %(actor_name)s which is not supported by" % {
                    'actor_name': actor_name
                    })
                log.write("    current aipsetup system")
                ret = 3
            else:
                if eval("aipsetup.tools.%(toolname)s.%(function)s(config, log, dirname)" % {
                        'toolname': actor,
                        'function': function
                        }) != 0:
                    log.write("-e- Tool %(toolname)s could not perform %(process)s" % {
                            'toolname': actor,
                            'process': process
                            })
                    ret = 4
                else:

                    log.write("-i- %(process)s complited" % {
                            'process': process.capitalize()
                            })

    log.stop()

    return ret

def extract(config, dirname):
    return _same_function(
        config,
        dirname,
        'extractor',
        'extract',
        'extracting',
        'extraction'
        )

def configure(config, dirname):
    return _same_function(
        config,
        dirname,
        'configurer',
        'configure',
        'configuring',
        'configuration'
        )

def build(config, dirname):
    return _same_function(
        config,
        dirname,
        'builder',
        'build',
        'building',
        'building'
        )

def install(config, dirname):
    return _same_function(
        config,
        dirname,
        'installer',
        'install',
        'installing',
        'installation'
        )


def complite(config, dirname):
    ret = 0
    for i in ['extract', 'configure',
              'build', 'install']:

        if eval("%(name)s(config, dirname)" % {
                'name': i
                }) != 0:
            print "-e- Building error on stage %(name)s" % {
                'name': i
                }
            ret = 1
            break

    return ret
