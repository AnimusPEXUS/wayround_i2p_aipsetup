#!/usr/bin/python3.2

import os.path
import sys
import logging

import org.wayround.utils.getopt2

import org.wayround.aipsetup
import org.wayround.aipsetup.config

AIPSETUP_SUBMODULES = frozenset(
    ['info', 'buildinfo',
     'build', 'server', 'client',
     'pkgindex', 'name', 'docbook',
     'buildingsite', 'constitution',
     'pack', 'package', 'config']
    )

# Logging settings
for i in [
    (logging.CRITICAL, '-c-'),
    (logging.ERROR   , '-e-'),
    (logging.WARN    , '-w-'),
    (logging.WARNING , '-w-'),
    (logging.INFO    , '-i-'),
    (logging.DEBUG   , '-d-')
    ]:
    logging.addLevelName(i[0], i[1])
del i

# Parse parameters
optilist, args = org.wayround.utils.getopt2.getopt_keyed(sys.argv[1:])
args_l = len(args)

# Setup logging level and format
log_level = 'INFO'

if '--log' in optilist:
    log_level_u = i[1].upper()

    if not log_level_u in list(logging._levelNames):
        print("-e- Wrong --log parameter")
    else:
        log_level = log_level_u

    del(optilist['--log'])
    del(log_level_u)

logging.basicConfig(format="%(levelname)s %(message)s", level=log_level)


# Try load config
try:
    org.wayround.aipsetup.config.config = \
        org.wayround.aipsetup.config.load_config('/etc/aipsetup.conf')
except:
    logging.warning("""\
Some errors was spotted while reading config file.
    aipsetup will work as far as it can without config.
    (use `aipsetup config' to create new config or diagnose existing!)
""")
    org.wayround.aipsetup.config.config = {}

ret = 0



if '--help' in optilist:
    if args_l == 0:

        print("""\
    Usage: {basename} [command] [command_parameters]

    Commands:

        info            Pkg info files Actions
        buildinfo       Build info files Actions
        builders        Builder files Actions

        constitution    View or Edit Constitution
        buildingsite    Building Site Maneuvers
        build           Building Actions
        pack            Packaging Actions
        server          LUST Server Related Actions
        client          Download Actions
        pkgindex        Package Index Actions

        name            Tools for Parsing File Names
        docbook         Docbook Tools


        --help          See this Help
        --version       Version Info
""".format(basename=os.path.basename(__file__)))

    else:
        if not args[0] in AIPSETUP_SUBMODULES:
            logging.error("Have no module named `{}'".format(args[0]))
        else:
            try:
                exec("import org.wayround.aipsetup.{}".format(args[0]))
            except:
                logging.critical("Error importing submodule `{}'".format(args[0]))
            else:
                try:
                    help_text = eval("org.wayround.aipsetup.{}.help_text()".format(args[0]))
                except:
                    logging.error("help text for submodule `{}' not available".format(args[0]))

                else:
                    print(help_text.format_map({
                        'aipsetup': os.path.basename(__file__),
                        'command': args[0]
                        }))

elif '--version' in optilist:
    print(org.wayround.aipsetup.AIPSETUP_VERSION)

elif args_l == 0:
    logging.error("No commands or parameters passed. Try aipsetup --help")
    ret = 1

else:

    if not args[0] in AIPSETUP_SUBMODULES:
        logging.error("Have no module named `{}'".format(args[0]))
        ret = 1
    else:
        try:
            exec("import org.wayround.aipsetup.{}".format(args[0]))
        except:
            logging.critical("Error importing submodule `{}'".format(args[0]))
        else:
            commands = {}
            try:
                exec("commands = org.wayround.aipsetup.{}.exported_commands()".format(args[0]))
            except:
                logging.critical("Can't get `{}' module exported commands".format(args[0]))

            else:
                if not args[1] in commands:
                    logging.error("Function `{}' not exported by module `{}'".format(args[1], args[0]))
                else:

                    ret = commands[args[1]](optilist, args[2:])
exit(ret)
