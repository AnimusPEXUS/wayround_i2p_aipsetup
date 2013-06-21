#!/usr/bin/python3

import logging

import org.wayround.utils.program

org.wayround.utils.program.logging_setup(loglevel='INFO')

import org.wayround.aipsetup.commands
import org.wayround.aipsetup.config
import org.wayround.aipsetup.gtk
import org.wayround.aipsetup.dbconnections

config = org.wayround.aipsetup.config.load_config('/etc/aipsetup.ini')

commands = org.wayround.aipsetup.commands.commands()

ret = org.wayround.utils.program.program(
    'aipsetup3', config, commands
    )

try:
    org.wayround.aipsetup.gtk.stop_session()
except:
    logging.error("Exception while stopping Gtk+ session")

try:
    org.wayround.aipsetup.dbconnections.close_all()
except:
    logging.exception("Exception while closing database connections")

exit(ret)
