#!/usr/bin/python

import sys
import aipsetup_utils

# protect module from being run as script
aipsetup_utils.module_run_protection(__name__)

module_name=__name__
module_group='build'
module_modes=['esc','escript']
module_help='This is template editing mode. By default \
it starts editor with opened selected template. if template is \
not exist, then it\'s created from `usr\' template. if saved file is empty or it\'s hash equals to usr\'s - new template will be deleted'

aipsetup_utils.update_modules_data(module_name, module_group, module_modes, module_help)

def editing_help():
    print """\
  this mode accepts only one argument - themplate name.
  without argument, error will be displayed.

    options are following:

     -d              delete template
     -t template     use `template' as prototype, not `usr'.
                     WARNING: this also deletes template you've
                              selected to edit"""

def run(help_mode=False,arguments=[]):
    if help_mode:
        editing_help()
    else:
        d_sett=False
        t_sett=False
        t_sett_mean=''
        if len(args) != 1:
            print '-e- not selected template to edit'
            exit (-1)
        for i in optilist:
            if i[0]=='-d':
                d_sett=True
                
            if i[0]=='-t':
                t_sett=True
                t_sett_mean=i[1]

            if d_sett and t_sett:
                print '-e- -t and -d options can not be combined'
                exit (-1)
            
            if d_sett:
                print '-i- deleting template '+args[0]
            
            if t_sett:
                print '-i- using '+t_sett_mean+' as template'
            else:
                t_sett_mean='usr'
