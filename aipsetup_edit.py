#!/usr/bin/python



import sys
import os
import getopt
import subprocess
import aipsetup_utils



# protect module from being run as script
aipsetup_utils.module_run_protection(__name__)



module_name = __name__
module_group = 'build'
module_modes = ['esc','escript']
module_help = """\
This is template editing mode. By default \
it starts editor with opened selected template. if template is \
not exist, then it's created from `usr' template. if saved file \
is empty or it's hash equals to user's - new template will be deleted"""


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

def run(aipsetup_config,
        arguments = []):

    optilist, args = getopt.getopt(arguments,
                                   'dt:e:',
                                   ['help'])

    for i in optilist:
        if i[0] == '--help':
            editing_help()
            exit (0)

    d_sett = False
    t_sett = False
    t_sett_mean = ''
    e_sett = False
    e_sett_mean = 'less'


    if len(args) != 1:
        print '-e- must be exacly one argument'
        exit (-1)

    for i in optilist:
        if i[0] == '-d':
            d_sett = True

        if i[0] == '-t':
            t_sett = True
            t_sett_mean = i[1]

        if i[0] == '-e':
            e_sett = True
            e_sett_mean = i[1]

    if d_sett and t_sett:
        print '-e- -t and -d options can not be combined'
        return -1

    if d_sett:
        print '-i- deleting template '+aipsetup_config['templates']+'/'+args[0]
        try:
            os.unlink(aipsetup_config['templates']+'/'+args[0])
        except OSError as err:
            print '-e- can not remove file: '+err.strerror
            return -1

    if t_sett:
        print '-i- using '+t_sett_mean+' as template'
    else:
        t_sett_mean='usr'

    if t_sett:
        if aipsetup_utils.filecopy(aipsetup_config['templates']+'/'+t_sett_mean,
                                   aipsetup_config['templates']+'/'+args[0],
                                   True) != 0:
            print '-e- can\'t use template '+t_sett_mean
            return -1

    editor = aipsetup_config['editor']
    if e_sett:
        editor = e_sett_mean
            
    print '-i- opening '+aipsetup_config['templates']+'/'+args[0]+' with '+editor
    subproc = subprocess.Popen([editor,
                                aipsetup_config['templates']+'/'+args[0]])
            
            
    subproc.wait()
    print '-i- process exited'
    
    return 0
