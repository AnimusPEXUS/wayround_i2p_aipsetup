
"""
Version comparison utilities
"""

import logging

import wayround_org.utils.version

import wayround_org.aipsetup.package_name_parser


def package_version_comparator(name1, name2):
    """
    Compares package names by timestamps
    """

    ret = 0

    d1 = wayround_org.aipsetup.package_name_parser.package_name_parse(
        name1
        )

    d2 = wayround_org.aipsetup.package_name_parser.package_name_parse(
        name2
        )

    if d1 == None:
        raise Exception("Can't parse filename: `{}'".format(name1))

    if d2 == None:
        raise Exception("Can't parse filename: `{}'".format(name2))

    if d1['groups']['name'] != d2['groups']['name']:
        raise Exception("Different names")

    else:
        d1_ts = d1['groups']['timestamp'].split('.')
        d2_ts = d2['groups']['timestamp'].split('.')

        if d1['re'] == 'aipsetup2':
            d1_ts = [d1_ts[0][0:8], d1_ts[0][8:], '0']

        if d2['re'] == 'aipsetup2':
            d2_ts = [d2_ts[0][0:8], d2_ts[0][8:], '0']

        com_res = wayround_org.utils.version.standard_comparison(
            d1_ts, None,
            d2_ts, None,
            )

        if com_res != 0:
            ret = com_res
        else:
            ret = 0

    return ret


def lb_comparator(version_str, pattern_str='== 0.0.0'):

    logging.debug("lb_comparator: `{}', `{}'".format(version_str, pattern_str))
    pattern_str = str(pattern_str).strip()
    version_str = str(version_str).strip()

    comparator = '=='

    if ' ' in pattern_str:
        spc_ind = pattern_str.index(' ')
        comparator = pattern_str[0:spc_ind]
        pattern_str = pattern_str[spc_ind + 1:].strip()

    if comparator == '=':
        comparator = '=='

    if not comparator in ['==', '<', '<=', '>', '>=']:
        raise ValueError("Wrong comparator: `{}'".format(comparator))

    pattern_str = pattern_str.split('.')
    version_str = version_str.split('.')

    cmp_res = \
        wayround_org.utils.version.standard_comparator(
            version_str,
            pattern_str
            )

    ret = eval("cmp_res {} 0".format(comparator))
    logging.debug("evaluating: {} {} 0 => {}".format(cmp_res, comparator, ret))
    return ret
