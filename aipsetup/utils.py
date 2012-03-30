#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import os.path
import re
import ConfigParser
import shutil
import traceback


# *******************
# Protective function. Protects modules from being run as scripts
# requires __name__ tobe passed as parameter
def module_run_protection(name):
    if name == "__main__":
        print '-e- !! This module must be started by aipsetup, not as script !!'
        # this exit is ok, but try not to use exit() function anywhere else
        exit (-1)

module_run_protection(__name__)

# *******************

def show_version_message():
    print """\
Copyright (C) 2008-2012 Alexey V. Gorshkov (a.k.a. AnimusPEXUS)
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

def get_configuration(defaults, file='/etc/aipsetup.conf'):

    ret = defaults

    cp = ConfigParser.RawConfigParser()

    f = None

    try:
        f = open(file, 'r')
    except:
        print "-e- Can't open %(file)s" % {'file': file}
        ret = None

    try:
        cp.readfp(f)
    except:
        print "-e- Can't read %(file)s" % {'file': file}
        ret = None

    f.close()

    if isinstance(ret, dict):

        if cp.has_section('main'):

            for i in defaults:

                if cp.has_option('main', i):

                    ret[i] = cp.get('main', i)

    del(cp)
    return ret

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
                print 'reading ' + str(size)
            buff = in_file.read(255)
            if verbose:
                print 'readed  ' + str(len(buff))
                print 'write ' + str(len(buff))
            out_file.write(buff)
            out_file.flush()
    except:
        return 'ERROR'
    return 'EOF'

def pathRemoveDblSlash(dir_str):
    t = dir_str
    while t.find('//') != -1:
        t = t.replace('//', '/')
    return t

# def option_check(names=['--help', '-h'], optionlist=[]):
#     '''search option list for required option and returnd tupil in
#        which first element is False or True depending on search
#        success, second is option exect name, third is value'''

#     for i in optionlist:
#         for j in names:

#             if i[0] == j:
#                 return (True, i[0], i[1])

#     return (False, None, None)

# def traceback_return(info):
#     ret = u''
#     print repr(info[0])
#     for i in traceback.extract_tb(info[2]):
#         ret += u'   -T-  ['+unicode(i[1])+'] ('+unicode(repr())+')'+unicode()+' ('+unicode(repr(tb_object.tb_frame))+')'
#         tb_object = tb_object.tb_next
#     return ret

def pkg_name_parse(name='aaa-1.1.1.1.tar.gz'):
    result = re.match('([0-9A-Za-z_\ -]*)-?(.*)(tar\.gz|tar\.bz2|tar\.xz|tgz|tbz2|zip|7z|tar)$', name)
    print repr(result.groups())
