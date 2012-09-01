
import logging

import org.wayround.aipsetup.name
import org.wayround.aipsetup.config

def source_version_comparator(name1, name2):

    ret = 0

    d1 = org.wayround.aipsetup.name.source_name_parse(
        name1,
        mute=True
        )

    d2 = org.wayround.aipsetup.name.source_name_parse(
        name2,
        mute=True
        )


    if d1 == None or d2 == None:
        raise Exception("Can't parse filename")

    if d1['groups']['name'] != d2['groups']['name']:
        raise ValueError("Files has different names")

    else:
        com_res = standard_comparison(
            d1['groups']['version_list'], d1['groups']['status_list'],
            d2['groups']['version_list'], d2['groups']['status_list']
            )

        if com_res != 0:
            ret = com_res
        else:
            ret = 0

    if ret == -1:
        logging.debug(name1 + ' < ' + name2)
    elif ret == 1:
        logging.debug(name1 + ' > ' + name2)
    else:
        logging.debug(name1 + ' = ' + name2)

    return ret

def package_version_comparator(name1, name2):

    ret = 0

    d1 = org.wayround.aipsetup.name.package_name_parse(
        name1, mute=True
        )

    d2 = org.wayround.aipsetup.name.package_name_parse(
        name2, mute=True
        )

    if d1 == None:
        raise Exception("Can't parse filename: `{}'".format(name1))

    if d2 == None:
        raise Exception("Can't parse filename: `{}'".format(name2))

    if d1['groups']['name'] != d2['groups']['name']:
        raise Exception("Different names")

    else:
        com_res = standard_comparison(
            d1['groups']['timestamp'].split('.'), None,
            d2['groups']['timestamp'].split('.'), None,
            )

        if com_res != 0:
            ret = com_res
        else:
            ret = 0

    return ret


def standard_comparison(
    version_list1, status_list1,
    version_list2, status_list2
    ):

    vers_comp_res = None
    stat_comp_res = None

    vers1 = version_list1
    vers2 = version_list2

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
            logging.debug(vers1[i] + ' > ' + vers2[i])
            vers_comp_res = +1
            break
        elif int(vers1[i]) < int(vers2[i]):
            logging.debug(vers1[i] + ' < ' + vers2[i])
            vers_comp_res = -1
            break
        else:
            continue


    # second comparison part
    if vers_comp_res == None:
        if longer != None:
            if longer == 'vers1':
                logging.debug(str(vers1) + ' > ' + str(vers2))
                vers_comp_res = +1
            else:
                logging.debug(str(vers1) + ' > ' + str(vers2))
                vers_comp_res = -1

    if vers_comp_res == None:
        vers_comp_res = 0

    if vers_comp_res == 0:
        # TODO: better algorithm required 
        if status_list1 != None and status_list2 != None:
            s1 = '.'.join(status_list1)
            s2 = '.'.join(status_list2)
            if s1 > s2:
                stat_comp_res = +1
            elif s1 < s2:
                stat_comp_res = -1
            else:
                stat_comp_res = 0

            vers_comp_res = stat_comp_res

    ret = vers_comp_res

    return ret

