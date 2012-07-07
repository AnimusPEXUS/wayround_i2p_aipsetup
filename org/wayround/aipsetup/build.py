
import sys
import os.path
import logging

import org.wayround.aipsetup.buildingsite

import org.wayround.utils.log


FUNCTIONS = frozenset([
    'extract',
    'configure',
    'build',
    'distribute',
    'prepack'
    ])

FUNCTIONS_TEXTS_SET = {
    'extract': ('extractor', 'extract', 'extracting', 'extraction'),
    'configure': ('configurer', 'configure', 'configuring', 'configuration'),
    'build': ('builder', 'build', 'building', 'building'),
    'distribute': ('distributer', 'distribute', 'distributing', 'distribution'),
    'prepack': ('prepackager', 'prepack', 'prepackaging', 'prepackaging')
    }


def print_help(opts, args):
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




def router(opts, args):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print("-e- Command not given.")
        ret = 1
    else:

        if args[0] == 'help':
            print_help()

        elif args[0] in list(FUNCTIONS):

            d = '.'

            if args_l > 1:
                d = args[1]

            ret = general_tool_function(
                args[0], d, FUNCTIONS_TEXTS_SET[args[0]]
                )

        elif args[0] == 'complete':

            d = '.'

            if args_l > 1:
                d = args[1]

            ret = complete(d)

        else:
            print("-e- Wrong build command")

    return ret

def general_tool_function(tool_name, dirname, texts):

    process = texts[3]
    whatdoes = texts[2]
    function = texts[1]

    ret = 0

    log = org.wayround.utils.log.Log(dirname, process)
    # log.write("-i- Closing this log now, cause it can't be done farther")

    log.write("-i- =========[{}]=========".format(whatdoes.capitalize()))

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, ret_on_error=None
        )

    if pi == None:
        log.write("-e- Error getting information about %(process)s" % {
                'process': process
                })
        ret = 1
    else:
        try:
            actor = pi['pkg_buildinfo'][tool_name]
        except:
            log.write("-e- Error getting %(tool_name)s name" % {
                    'tool_name': tool_name
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
                    ("-e- Package desires %(tool_name)s "\
                    + "which is not supported by") % {
                        'tool_name': tool_name
                        }
                    )
                log.write("    current aipsetup system")
                ret = 3
            else:
                if eval(
                    ("aipsetup.tools.%(toolname)s."\
                    + "%(function)s(log, dirname)") % {
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


def complete(dirname):
    ret = 0

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, ret_on_error=None
        )

    if pi == None:
        logging.error("Error reading package info in dir {}".format(dirname))
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
