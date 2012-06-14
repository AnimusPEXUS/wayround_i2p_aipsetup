#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import os.path
import sys
import shutil

import aipsetup.utils.config
import aipsetup.utils.getopt2


config = aipsetup.utils.config.load_config()
if config == None:
    print("-e- configuration file error exiting")
    exit(1)

ret = 0


optilist, args = aipsetup.utils.getopt2.getopt(sys.argv[1:])
args_l = len(args)

if '--help' in [ i[0] for i in optilist ]:
    print("""\
   Usage: %(basename)s [command] [command_parameters]

   Commands:

      info          Pkg info files Actions
      buildinfo     Build info files Actions
      builders      builder files Actions

      constitution  View or Edit Constitution
      buildingsite  Building Site Manuvers
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
    print(aipsetup.AIPSETUP_VERSION)

elif args_l == 0:
    print("-e- No commands or parameters passed. Try aipsetup --help")
    ret = 1

else:

    if args[0] in ['info', 'buildinfo', 'builders',
                   'build', 'server', 'client',
                   'pkgindex', 'name', 'docbook',
                   'buildingsite', 'constitution',
                   'pack', 'package']:

        exec("import aipsetup.%(name)s" % {
                'name': args[0]
                })

        exec("ret = aipsetup.%(name)s.router(optilist, args[1:], config)" % {
                'name': args[0]
                })

    else:
        print("-e- Wrong command. Try aipsetup --help")
        ret = 1

print("-i- done")
exit(ret)
