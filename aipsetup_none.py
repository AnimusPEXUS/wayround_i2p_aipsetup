#!/usr/bin/python

import sys
import aipsetup_utils
import __main__

# protect module from being run as script
aipsetup_utils.module_run_protection(__name__)

module_name=__name__
module_modes=['none']
module_group='basic'
module_help='This is default behavior mode. Does nothing. \
Only shows this help page'

aipsetup_utils.update_modules_data(module_name, module_group, module_modes, module_help)

def module_help():
    print """\

  usage: """+sys.argv[0:1][0]+""" -m mode [--help] [--version] \


    --version       show version info
    --help          show this help message or mode's one

    -m mode         mode (see below)


    [modes]
    -------
"""
    show_group_modules('basic')

def get_module_modes(module='aipsetup_none'):
    b=[]
    for i in __main__.modules_data:
        if i[0]==module:
            b=i[2]
            b.sort
            return b

def show_group_modules(group='basic'):

    modules=get_group_modules(group)

    outlist=modules
    print '    == ' + group + ' modes ==\n'
    
    for i in outlist:
        print '     "'+'" | "'.join(i[2])+'":\n       '+i[3]
        print
        break

def get_group_modules(group='basic'):
    outlist=[]
    for i in __main__.modules_data:
        if i[1]==group:
            outlist.append(i)
    return outlist

def run(help_mode=False,optilist=[],args=[]):
    if not (help_mode or (len(args) == 0)):
        print 'this mode only shows help. here it is:'

    module_help()
