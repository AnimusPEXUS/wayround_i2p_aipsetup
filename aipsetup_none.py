#!/usr/bin/python


import sys
import textwrap
import __main__
import getopt
import aipsetup_utils


# protect module from being run as script
aipsetup_utils.module_run_protection(__name__)


module_name = __name__
module_group = 'basic'
module_modes = ['none']
module_help = \
    """This is default (dummy) behavior mode. It's actually does
    nothing, only shows this help text and list of subcommands shared
    by submodules"""

aipsetup_utils.update_modules_data(module_name,
                                   module_group,
                                   module_modes,
                                   module_help)
# show aipsetup help
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
    show_group_modules('templates')
    show_group_modules('packages')
    show_group_modules('misc')


def get_module_modes(module='aipsetup_none'):
    b = []
    for i in __main__.modules_data:
        if i[0] == module:
            b = i[2]
            b.sort
            return b

def show_group_modules(group='basic'):

    modules = get_group_modules(group)

    outlist = modules
    print '    == ' + group + ' modes ==\n'

    for i in outlist:
        print '     ' + ' | '.join(i[2]) + ':'

        tmps = i[3]
        tmps = tmps.replace('\n', ' ')
        while (tmps.find('  ') != -1):
            tmps = tmps.replace('  ', ' ')

        print textwrap.fill(
            tmps,
            subsequent_indent = '        ',
            initial_indent = '          ')
        print
        break

def get_group_modules(group = 'basic'):
    outlist = []
    for i in __main__.modules_data:
        if i[1] == group:
            outlist.append(i)
    return outlist

def run(aipsetup_config,
        arguments = []):

    optilist = None
    args = None

    try:
        optilist, args = getopt.getopt(arguments, '', ['help', 'version'])
    except getopt.GetoptError, e:
        print '-e- Error while parsing parameters: ' + e.msg
        return -1

    h_sett = False
    help_sett = False
    version_sett = False

    for i in optilist:
        if i[0] == '--version':
            version_sett = True

        if (i[0] == '--help'):
            help_sett = True

    if not (len(arguments) == 0) and (len(optilist) == 0):
        print 'this mode only shows help. here it is:'
        module_help()
        return 0


    if version_sett:
        aipsetup_utils.show_version_message()
        return 0

    module_help()
    return 0
