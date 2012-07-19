#!/usr/bin/python3.2

import sys
import logging

import org.wayround.utils.getopt2

import org.wayround.aipsetup
import org.wayround.aipsetup.config
import org.wayround.aipsetup.help


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
opts, args = org.wayround.utils.getopt2.getopt_keyed(sys.argv[1:])
args_l = len(args)

# Setup logging level and format
log_level = 'INFO'

if '--log' in opts:
    log_level_u = i[1].upper()

    if not log_level_u in list(logging._levelNames):
        print("-e- Wrong --log parameter")
    else:
        log_level = log_level_u

    del(opts['--log'])
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



if '--help' in opts:
    org.wayround.aipsetup.help.aipsetup_help(opts, args)
elif '--version' in opts:
    print(org.wayround.aipsetup.AIPSETUP_VERSION)

elif args_l == 0:
    logging.error("No commands or parameters passed. Try aipsetup --help")
    ret = 1

else:

    if not args[0] in org.wayround.aipsetup.AIPSETUP_MODULES_LIST:
        logging.error("Have no module named `{}'".format(args[0]))
        ret = 1
    else:

        if org.wayround.aipsetup.config.config == {} \
            and args[0] in org.wayround.aipsetup.AIPSETUP_MODULES_LIST_FUSED:
            logging.error("Configuration error. Only allowed modules are {}".format(
                    repr(list(org.wayround.aipsetup.AIPSETUP_MODULES_LIST - org.wayround.aipsetup.AIPSETUP_MODULES_LIST_FUSED))
                    )
                )
        else:

            try:
                exec("import org.wayround.aipsetup.{}".format(args[0]))
            except:
                logging.exception("Error importing submodule `{}'".format(args[0]))
            else:
                commands = {}
                try:
                    exec("commands = org.wayround.aipsetup.{}.exported_commands()".format(args[0]))
                except:
                    logging.exception("Can't get `{}' module exported commands".format(args[0]))

                else:
                    if args_l == 1:
                        logging.error("module command is required. see aipsetup {} --help".format(args[0]))
                    else:
                        if not args[1] in commands:
                            logging.error("Function `{}' not exported by module `{}'".format(args[1], args[0]))
                        else:

                            ret = commands[args[1]](opts, args[2:])

exit(ret)
