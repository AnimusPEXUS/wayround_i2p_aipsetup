#!/usr/bin/python3

import sys

if sys.path[0] == '':
    del sys.path[0]

import logging

import wayround_org.utils.program

wayround_org.utils.program.logging_setup(loglevel='INFO')

import wayround_org.aipsetup.commands
import wayround_org.aipsetup.config
import wayround_org.aipsetup.build
import wayround_org.aipsetup.dbconnections

config = wayround_org.aipsetup.config.load_config('/etc/aipsetup.conf')

package_info = None

bs = wayround_org.aipsetup.build.BuildingSiteCtl('.')
if bs.is_building_site():
    package_info = bs.read_package_info()

del(bs)

commands = wayround_org.aipsetup.commands.commands()

ret = wayround_org.utils.program.program(
    'aipsetup3',
    commands,
    additional_data={
        'config': config,
        'package_info': package_info
        }
    )

try:
    import wayround_org.aipsetup.gtk
    wayround_org.aipsetup.gtk.stop_session()
except:
    logging.error("Exception while stopping Gtk+ session")

try:
    wayround_org.aipsetup.dbconnections.close_all()
except:
    logging.exception("Exception while closing database connections")

exit(ret)
