# -*- coding: utf-8 -*-

import aipsetup
import aipsetup.name
import aipsetup.utils.config

def version_comparator(name1, name2):

    ret = 0

    d1 = aipsetup.name.source_name_parse(
        aipsetup.utils.config.actual_config,
        name1, mute=True, modify_info_file=False
        )

    d2 = aipsetup.name.source_name_parse(
        aipsetup.utils.config.actual_config,
        name2, mute=True, modify_info_file=False
        )

    if d1 == None or d2 == None:
        print "-e- Can't parse filename"
        raise Exception

    if d1['groups']['name'] != d2['groups']['name']:
        print "-e- Different names"
        raise Exception

    else:
        com_res = standard_comparison(
            d1['groups']['version'],
            d2['groups']['version']
            )

        if com_res != 0:
            ret = com_res
        else:
            ret = 0

    return ret


def standard_comparison(e1, e2):

    vers1 = e1.split('.')
    vers2 = e2.split('.')

    longer = None

    v1l = len(vers1)
    v2l = len(vers2)

    #  length used in first comparison part
    el_1 = v1l

    if v1l == v2l:
        longer = None
        el_1 = v1l

    elif v1l > v2l:
        longer = 'vers1'
        el_1 = v2l

    else:
        longer = 'vers2'
        el_1 = v1l

    # first comparison part

    for i in range(el_1):

        if int(vers1[i]) > int(vers2[i]):
            return +1
        elif int(vers1[i]) < int(vers2[i]):
            return -1
        else:
            continue

    # second comparison part

    if longer != None:
        if longer == 'vers1':
            return +1
        else:
            return -1

    return 0
