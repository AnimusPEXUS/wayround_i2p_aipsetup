#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import os.path

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.tools.autotools

import org.wayround.utils.log

def print_help():
    print("""\
aipsetup build command

   extract [DIRNAME]

      Extract source in buildingsite DIRNAME. If DIRNAME not given
      assume current working dir.

   configure [SITEDIR]
      configures SITEDIR accordingly to info

   build [SITEDIR]
      builds SITEDIR accordingly to info

   install [SITEDIR]
      creates destdir in SITEDIR accordingly to info

   postinstall [SITEDIR]
      postinstallation processings for SITEDIR accordingly to info

   complite [SITEDIR]
      configures, builds and installs SITEDIR accordingly to info

 See also aipsetup pack help
""")

def router(opts, args, config):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print("-e- Command not given. See `aipsetup build help'")
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
            print("-e- Wrong build command")

    return ret

def _same_function(config, dirname, actor_name,
                   function, whatdoes, process):

    ret = 0

    log = org.wayround.utils.log.Log(config, dirname, process)
    # log.write("-i- Closing this log now, cause it can't be done farther")

    log.write("-i- =========[%(whatdoes)s]=========" % {
        'whatdoes': whatdoes.capitalize()
        })

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        config, dirname, ret_on_error=None
        )

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
            log.write(
                org.wayround.utils.error.return_exception_info(
                    sys.exc_info()
                    )
                )
            ret = 2

        else:
            if not actor in ['autotools']:
                log.write(
                    ("-e- Package desires %(actor_name)s "\
                    + "which is not supported by") % {
                        'actor_name': actor_name
                        }
                    )
                log.write("    current aipsetup system")
                ret = 3
            else:
                if eval(
                    ("aipsetup.tools.%(toolname)s."\
                    + "%(function)s(config, log, dirname)") % {
                        'toolname': actor,
                        'function': function
                        }
                    ) != 0:
                    log.write(
                        ("-e- Tool %(toolname)s could "
                        + "not perform %(process)s") % {
                            'toolname': actor,
                            'process': process
                            }
                        )
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

def postinstall(config, dirname):
    return _same_function(
        config,
        dirname,
        'postinstaller',
        'postinstall',
        'postinstalling',
        'postinstallation'
        )


def complite(config, dirname):
    ret = 0

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        config, dirname, ret_on_error=None
        )

    if pi == None:
        # FIXME: inform user about error using logging
        ret = 1
    else:

        act_seq = []
        try:
            act_seq = pi['pkg_buildinfo']['build_sequance']
        except:
            print("-e- Can't get actor sequence")
            ret = 2
        else:

            for i in act_seq:

                if not i in ['extract', 'configure',
                             'build', 'install',
                             'postinstall']:
                    print("-e- Requested actor not supported")
                    ret = 3
                else:

                    if eval("%(name)s(config, dirname)" % {
                            'name': i
                            }) != 0:
                        print("-e- Building error on stage %(name)s" % {
                            'name': i
                            })
                        ret = 5
                        break

    return ret
