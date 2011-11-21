#!/usr/bin/python

import sys
import ConfigParser
import os

def show_version_message():
    print """\
Copyright (C) 2008-2010 Alexey V. Gorshkov (AGUtilities)
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE."""
    return

def update_modules_data(module_name, module_group, module_modes, module_help):
    import __main__
    try:
        __main__.modules_data
    except:
        print '-e- __main__.modules_data error'
    else:
        __main__.modules_data.append([module_name, module_group, module_modes, module_help])
    return

def module_run_protection(name):
    if name == "__main__":
        print '-e- this module must be started by aipsetup, not by hand'
        exit (-1)

def get_configuration(defaults):
    home = defaults['homedir']
    temps = defaults['templates']
    editor = defaults['editor']
    settings = defaults['settings']

    cp = ConfigParser.RawConfigParser()

    cp.add_section('main')

    cp.set('main', 'home', home)
    cp.set('main', 'templates', temps)
    cp.set('main', 'editor', editor)

    try:
        cp.read(settings)
    except:
        print '-e- file with settings not found '+settings
        exit (-1)

    home = cp.get('main', 'home')
    temps = cp.get('main', 'templates')
    editor = cp.get('main', 'editor')


    return {
        'homedir'   : home,
        'templates' : temps,
        'editor'    : editor,
        'settings'  : settings
        }

def filecopy(src, dst, verbose=False):
    print '-i- copying '+src+' to '+dst
    try:
        s = os.open(src, 'rb')
    except:
        if verbose:
            print '-e- error opening file for read '+src
        return 1

    try:
        d =  os.open(dst, 'rb')
    except:
        if verbose:
            print '-e- error opening file for write '+dst
        return 2

    try:
        d.write(s.read())
    except:
        if verbose:
            print '-e- error reading from file ' + src +\
                ' or writing to file ' + dst
        return 3
    
    s.close()
    d.close()

    return 0

module_run_protection(__name__)
