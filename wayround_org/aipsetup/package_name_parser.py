
"""
Module with package names parsing facilities
"""

import copy
import datetime
import logging
import os.path
import re

import wayround_org.utils.list
import wayround_org.utils.text


ASP_NAME_REGEXPS = {
    'aipsetup3':
        r'^\((?P<name>.+?)\)-\((?P<version>(\d+\.??)+)\)-\((?P<status>.*?)\)'
        r'-\((?P<timestamp>\d{8}\.\d{6}\.\d{7})\)-\((?P<host>.*)\)'
        r'-\((?P<arch>.*)\)$',
    'aipsetup2':
        r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)'
        r'-(?P<timestamp>\d{14})-(?P<host>.*)$'
    }
"""
Regexps for parsing package names
"""

ASP_NAME_REGEXPS_COMPILED = {}
"""
same as :data:`ASP_NAME_REGEXPS` but compiled
"""

for i in ASP_NAME_REGEXPS:
    logging.debug("Compiling `{}'".format(i))
    ASP_NAME_REGEXPS_COMPILED[i] = re.compile(ASP_NAME_REGEXPS[i])

del(i)
ALL_DELIMITERS = ['.', '_', '-', '+', '~']

TIMESTAMPS = {
    'aipsetup3':
        r'^(?P<year>\d+)(?P<month>\d{2})(?P<day>\d{2})\.'
        r'(?P<hour>\d{2})(?P<minute>\d{2})'
        r'(?P<second>\d{2})\.(?P<micro>\d{7})$',
    'aipsetup2':
        r'^(?P<year>\d+)(?P<month>\d{2})(?P<day>\d{2})'
        r'(?P<hour>\d{2})(?P<minute>\d{2})(?P<second>\d{2})$'
    }

TIMESTAMPS_COMPILED = {}

for i in TIMESTAMPS:
    logging.debug("Compiling `{}'".format(i))
    TIMESTAMPS_COMPILED[i] = re.compile(TIMESTAMPS[i])

del(i)


def rm_ext_from_pkg_name(name):
    """
    Remove extension from package name
    """

    ret = ''

    if name.endswith('.tar.xz'):
        ret = name[:-7]

    elif name.endswith('.asp'):
        ret = name[:-4]

    elif name.endswith('.xz'):
        ret = name[:-3]

    else:
        ret = name

    return ret


def package_name_parse(filename):
    """
    Parse package name.

    Can parse with endings .tar.xz, .asp and .xz
    """

    filename = os.path.basename(filename)

    logging.debug("Parsing package file name {}".format(filename))

    ret = None

    filename = rm_ext_from_pkg_name(filename)

    for i in ASP_NAME_REGEXPS:

        re_res = ASP_NAME_REGEXPS_COMPILED[i].match(filename)

        if re_res is not None:
            ret = {
                're': i,
                'name': filename,
                'groups': {
                    'name': re_res.group('name'),
                    'version': re_res.group('version'),
                    'timestamp': re_res.group('timestamp'),
                    'host': re_res.group('host'),
                    'arch': re_res.group('arch')
                    }
                }

            if ret['re'] == 'aipsetup3':
                ret['groups']['status'] = re_res.group('status')

            if (
                    not 'status' in ret['groups']
                    or ret['groups']['status'] == None
                    or ret['groups']['status'] == 'None'
                    ):
                ret['groups']['status'] = ''

            ret['groups']['version_list_dirty'] = (
                wayround_org.utils.text.slice_string_to_sections(
                    ret['groups']['version']
                    )
                )

            ret['groups']['version_list_dirty'] = (
                wayround_org.utils.list.list_strip(
                    ret['groups']['version_list_dirty'],
                    ALL_DELIMITERS
                    )
                )

            ret['groups']['version_list'] = (
                copy.copy(ret['groups']['version_list_dirty'])
                )

            wayround_org.utils.list.remove_all_values(
                ret['groups']['version_list'],
                ALL_DELIMITERS
                )

            ret['groups']['status_list_dirty'] = (
                wayround_org.utils.text.slice_string_to_sections(
                    ret['groups']['status']
                    )
                )

            ret['groups']['status_list_dirty'] = (
                wayround_org.utils.list.list_strip(
                    ret['groups']['status_list_dirty'],
                    ALL_DELIMITERS
                    )
                )

            ret['groups']['status_list'] = (
                copy.copy(ret['groups']['status_list_dirty'])
                )

            wayround_org.utils.list.remove_all_values(
                ret['groups']['status_list'],
                ALL_DELIMITERS
                )

            break

    return ret


def parse_timestamp(timestamp):

    ret = None

    for i in TIMESTAMPS_COMPILED.keys():

        res = TIMESTAMPS_COMPILED[i].match(timestamp)

        if res:

            micro = 0

            if i == 'aipsetup3':
                micro = res.group('micro')

            ret = datetime.datetime(
                int(res.group('year')),
                int(res.group('month')),
                int(res.group('day')),
                int(res.group('hour')),
                int(res.group('minute')),
                int(res.group('second')),
                int(micro)
                )

            break

    return ret
