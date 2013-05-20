#!/usr/bin/python3

import sys
import logging

import org.wayround.utils.program

import org.wayround.aipsetup.commands
import org.wayround.aipsetup.config


config = org.wayround.aipsetup.config.load_config('/etc/aipsetup.ini')

commands = org.wayround.aipsetup.commands.commands()

ret = org.wayround.utils.program.program(
    'aipsetup3', config, commands, loglevel='INFO'
    )

exit(ret)
