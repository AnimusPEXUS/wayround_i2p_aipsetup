
import logging

import org.wayround.aipsetup.name
import org.wayround.aipsetup.config

def source_version_comparator(name1, name2):

    ret = 0

    d1 = org.wayround.aipsetup.name.source_name_parse(
        name1, modify_info_file=False
        )

    d2 = org.wayround.aipsetup.name.source_name_parse(
        name2, modify_info_file=False
        )

    if d1 == None or d2 == None:
        raise Exception("Can't parse filename")

    if d1['groups']['name'] != d2['groups']['name']:
        raise Exception("Different names")

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

def package_version_comparator(name1, name2):

    ret = 0

    d1 = org.wayround.aipsetup.name.package_name_parse(
        name1, modify_info_file=False
        )

    d2 = org.wayround.aipsetup.name.package_name_parse(
        name2, modify_info_file=False
        )

    if d1 == None or d2 == None:
        raise Exception("Can't parse filename")

    if d1['groups']['name'] != d2['groups']['name']:
        raise Exception("Different names")

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
