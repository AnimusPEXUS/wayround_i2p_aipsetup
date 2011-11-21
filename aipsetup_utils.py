#!/usr/bin/python

import sys

def show_version_message():
    print """\
Copyright (C) 2008-2010 Alexey V. Gorshkov (AGUtilities)
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."""

def update_modules_data(module_name, module_group, module_modes, module_help):
    import __main__
    try:
        __main__.modules_data
    except:
        print '-e- __main__.modules_data error'
    else:
        __main__.modules_data.append([module_name, module_group, module_modes, module_help])

def module_run_protection(name):
    if name == "__main__":
        print '-e- this module must be started by aipsetup, not by hand'
        exit (-1)

module_run_protection(__name__)
