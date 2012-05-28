# -*- coding: utf-8 -*-

import copy
import os
import re

import aipsetup.utils.file

def columned_list_print(lst, width=None, columns=None,
                        margin_right=u' │ ', margin_left=u' │ ', spacing=u' │ ',
                        fd=1):
    print return_columned_list_print(lst, width=None, columns=None,
                                      margin_right=u' │ ', margin_left=u' │ ',
                                      spacing=u' │ ', fd=1)

def return_columned_list_print(lst, width=None, columns=None,
                      margin_right=u' │ ', margin_left=u' │ ', spacing=u' │ ',
                      fd=1):

    if width == None:
        if (isinstance(fd, int) and os.isatty(fd)) \
                or (isinstance(fd, file) and fd.isatty()):

            size = aipsetup.utils.file.get_terminal_size(fd)
            if size == None:
                width = 80
            else:
                width = size['ws_col']
        else:
            width = 80

    longest = 0
    lst_l = len(lst)
    for i in lst:
        l = len(i)
        if l > longest:
            longest = l


    mrr_l = len(margin_right)
    mrl_l = len(margin_left)
    spc_l = len(spacing)

    int_l = width-mrr_l-mrl_l

    if columns == None:
        columns = (int_l / (longest+spc_l))

    if columns < 1:
        columns = 1


    rows = int(lst_l / columns)

    # print "int_l   == " + str(int_l)
    # print "longest == " + str(longest)
    # print "width   == " + str(width)
    # print "lst_l   == " + str(lst_l)
    # print "columns == " + str(columns)

    ret = ''
    for i in range(0, lst_l, columns):
        # print "i == " + str(i)
        l2 = lst[i:i+columns]

        l3 = []
        for j in l2:
            l3.append(j.ljust(longest))

        while len(l3) != columns:
            l3.append(u''.ljust(longest))

        ret += deunicodify("%(mrl)s%(row)s%(mrr)s" % {
                'mrl': margin_left,
                'mrr': margin_right,
                'row': spacing.join(l3)
                })

    return ret

def codify(list_or_basestring, on_wrong_type='exception',
           ftype='str', ttype='unicode', operation='decode',
           coding='utf-8'):

    ret = None
    if isinstance(list_or_basestring, eval(ftype)):
        ret = eval("list_or_basestring.%(opname)s('%(coding)s', 'strict')" % {
                'opname': operation,
                'coding': coding
                })

    elif isinstance(list_or_basestring, eval(ttype)):
        ret = copy.copy(list_or_basestring)

    elif isinstance(list_or_basestring, list):
        l2 = []
        for i in list_or_basestring:
            l2.append(unicodify(i))
        ret = l2
    else:
        if on_wrong_type == 'exception':
            raise TypeError
        elif on_wrong_type == 'copy':
            ret = copy.copy(list_or_basestring)
        else:
            raise Exception

    return ret

def unicodify(list_or_basestring, on_wrong_type='exception'):

    """
    Convert str or list of strs to unicode or list of unicode

    WARNING: (Python >3 `bin' and Python <3 `str') strings all assumed
    to be in UTF-8. decoding will be based only on UTF-8!!!

    dict convertion is not supported

    if on_wrong_type == 'exception' - exception is raised if wrong
    type given, else if on_wrong_type == 'copy' - wrong data just
    copyed

    """

    return codify(list_or_basestring, on_wrong_type='exception',
                  ftype='str', ttype='unicode', operation='decode')

def deunicodify(list_or_basestring, on_wrong_type='exception'):

    """
    Convert unicode or list of unicodes to str or list of strs

    WARNING: (Python >3 `bin' and Python <3 `str') strings all assumed
    to be in UTF-8. encoding will be based only on UTF-8!!!

    dict convertion is not supported

    if on_wrong_type == 'exception' - exception is raised if wrong
    type given, else if on_wrong_type == 'copy' - wrong data just
    copyed

    """

    return codify(list_or_basestring, on_wrong_type='exception',
                   ftype='unicode', ttype='str', operation='encode')


def parse_checksums_text(text):

    ret = 0

    lines = text.splitlines()

    sums = {}

    for i in lines:
        ist = i.strip(' \n\t\0')
        re_res = re.match('(.*?) \*(.*?)', i)

        if re_res == None:
            ret = 1
            break
        else:
            sums[re_res.groups(2)] = re_res.groups(1)

    if ret == 0:
        ret = sums

    return ret
