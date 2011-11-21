#!/usr/bin/python

import sys
import ConfigParser
import os
import shutil

def module_run_protection(name):
    if name == "__main__":
        print '-e- This module must be started by aipsetup. Not as script by hand.'
        # this exit is ok.
        exit (-1)

module_run_protection(__name__)

def show_version_message():
    print """\
Copyright (C) 2008-2010 Alexey V. Gorshkov (a.k.a. AnimusPEXUS)
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
        return None

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
    if verbose:
        print '-i- Copying "' + src + '"'
        print '       to "' + dst + '"'
    try:
        shutil.copy(src, dst)
    except:
        return 1
    return 0

def iocat(in_file, out_file, size=255, verbose=False):
    buff = 'tmp'
    try:
        while (buff != r''):
            if verbose:
                print 'reading '+str(size)
            buff = in_file.read(255)
            if verbose:
                print 'readed  '+str(len(buff))
                print 'write '+str(len(buff))
            out_file.write(buff)
            out_file.flush()
    except:
        return 'ERROR'
    return 'EOF'
