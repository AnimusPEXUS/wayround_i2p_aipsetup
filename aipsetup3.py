#!/usr/bin/python3.2

import os.path
import sys
import logging

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

logging.basicConfig(format="%(levelname)s %(message)s")

import org.wayround.utils.getopt2

import org.wayround.aipsetup
import org.wayround.aipsetup.config

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


optilist, args = org.wayround.utils.getopt2.getopt(sys.argv[1:])
args_l = len(args)

if '--help' in [ i[0] for i in optilist ]:
    print("""\
   Usage: %(basename)s [command] [command_parameters]

   Commands:

      info          Pkg info files Actions
      buildinfo     Build info files Actions
      builders      builder files Actions

      constitution  View or Edit Constitution
      buildingsite  Building Site Maneuvers
      build         Building Actions
      pack          Packaging Actions
      server        UHT Server Related Actions
      client        Download Actions
      pkgindex      Package Index Actions

      name          Tools for Parsing File Names
      docbook       Docbook Tools


      --help        See this Help
      --version     Version Info
""" % {
        'basename': os.path.basename(__file__)
        })

elif '--version' in [ i[0] for i in optilist ]:
    print(org.wayround.aipsetup.AIPSETUP_VERSION)

elif args_l == 0:
    print("-e- No commands or parameters passed. Try aipsetup --help")
    ret = 1

else:

    if args[0] in ['info', 'buildinfo',
                   'build', 'server', 'client',
                   'pkgindex', 'name', 'docbook',
                   'buildingsite', 'constitution',
                   'pack', 'package', 'config']:

        exec("import org.wayround.aipsetup.{name!s}".format(
                name=args[0]
                )
             )

        exec("ret = org.wayround.aipsetup.{name!s}.router(optilist, args[1:])".format(
                name=args[0]
                )
             )

    else:
        print("-e- Wrong command. Try aipsetup --help")
        ret = 1

print("-i- done")
exit(ret)
