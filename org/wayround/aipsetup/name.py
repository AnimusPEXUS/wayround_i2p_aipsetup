
"""
Module with package names parsing facilities
"""

import os.path
import re
import fnmatch
import logging
import copy

import org.wayround.utils.tag
import org.wayround.utils.text
import org.wayround.utils.list

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config

#Difficult name examples:
DIFFICULT_NAMES = [
    'bind-9.9.1-P2.tar.gz',
    'boost_1_25_1.tar.bz2',
    'dahdi-linux-complete-2.1.0.3+2.1.0.2.tar.gz',
    'dhcp-4.1.2rc1.tar.gz',
    'dvd+rw-tools-5.5.4.3.4.tar.gz',
    'GeSHi-1.0.2-beta-1.tar.bz2',
    'lynx2.8.7rel.1.tar.bz2',
    'name.tar.gz',
    'openssl-0.9.7a.tar.gz',
    'org.apache.felix.ipojo.manipulator-1.8.4-project.tar.gz',
    'Perl-Dist-Strawberry-BuildPerl-5101-2.11_10.tar.gz'
    'pkcs11-helper-1.05.tar.bz2',
    'qca-pkcs11-0.1-20070425.tar.bz2',
    'tcl8.4.19-src.tar.gz',
    'wmirq-0.1-source.tar.gz',
    'xc-1.tar.gz',
    'xf86-input-acecad-1.5.0.tar.bz2',
    'xf86-input-elo2300-1.1.2.tar.bz2'
    ]

ACCEPTABLE_SOURCE_NAME_EXTENSIONS = [
    '.tar.gz',
    '.tar.bz2',
    '.tar.xz',
    '.tar.lzma',
    '.zip',
    '.7z',
    '.tgz',
    '.tbz2',
    '.tbz'
    ]

ASP_NAME_REGEXPS = {
    'aipsetup2': r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)-(?P<timestamp>\d{14})-(?P<host>.*)$',
    'aipsetup3':
        r'^\((?P<name>.+?)\)-\((?P<version>(\d+\.??)+)\)-\((?P<status>.*?)\)-\((?P<timestamp>\d{8}\.\d{6}\.\d{7})\)-\((?P<host>.*)\)$'
    }

ASP_NAME_REGEXPS_COMPILED = {}

for i in ASP_NAME_REGEXPS:
    logging.debug("Compiling `{}'".format(i))
    ASP_NAME_REGEXPS_COMPILED[i] = re.compile(ASP_NAME_REGEXPS[i])

del(i)

def cli_name():
    """
    Internally used by aipsetup
    """
    return 'n'


def exported_commands():
    """
    Internally used by aipsetup
    """
    return {
        'parse': name_parse_name,
        'pparse': name_parse_package,
        'parse_test': name_parse_test
        }

def commands_order():
    """
    Internally used by aipsetup
    """
    return [
        'test_expressions_on_sources',
        'parse',
        'parse_test',
        'pparse'
        ]

def name_parse_name(opts, args):
    """
    Parse name

    [-w] NAME

    if -w is set - change <name>.json info file nametype value to
    result
    """

    ret = 0

    if len(args) != 1:
        logging.error("File name required")
        ret = 1
    else:

        filename = args[0]

        write = '-w' in opts

        if source_name_parse(
            filename,
            modify_info_file=write
            ) == None:

            ret = 2

    return ret

def name_parse_package(opts, args):
    """
    Parse package name

    NAME
    """

    ret = 0

    if len(args) != 1:
        logging.error("File name required")
        ret = 1
    else:

        filename = args[0]

        p_re = package_name_parse(filename, mute=False)

        if p_re == None:
            ret = 2

    return ret


def name_parse_test(args, opts):
    """
    Test Name Parsing Facilities
    """
    parse_test()
    return 0

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

def package_name_parse(filename, mute=True):
    """
    Parse package name
    """

    filename = os.path.basename(filename)

    logging.debug("Parsing package file name {}".format(filename))

    ret = None

    filename = rm_ext_from_pkg_name(filename)

    for i in ASP_NAME_REGEXPS:
        re_res = ASP_NAME_REGEXPS_COMPILED[i].match(filename)
        if re_res != None:
            ret = {
                're': i,
                'name': filename,
                'groups': {
                    'name': re_res.group('name'),
                    'version': re_res.group('version'),
                    'timestamp': re_res.group('timestamp'),
                    'host': re_res.group('host')
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
                org.wayround.utils.text.slice_string_to_sections(
                    ret['groups']['version']
                    )
                )

            ret['groups']['version_list_dirty'] = (
                org.wayround.utils.list.list_strip(
                    ret['groups']['version_list_dirty'],
                    ['.', '_', '-', '+']
                    )
                )

            ret['groups']['version_list'] = (
                copy.copy(ret['groups']['version_list_dirty'])
                )

            org.wayround.utils.list.remove_all_values(
                ret['groups']['version_list'],
                ['.', '_']
                )

            ret['groups']['status_list_dirty'] = (
                org.wayround.utils.text.slice_string_to_sections(
                    ret['groups']['status']
                    )
                )

            ret['groups']['status_list_dirty'] = (
                org.wayround.utils.list.list_strip(
                    ret['groups']['status_list_dirty'],
                    ['.', '_', '-', '+']
                    )
                )

            ret['groups']['status_list'] = (
                copy.copy(ret['groups']['status_list_dirty'])
                )

            org.wayround.utils.list.remove_all_values(
                ret['groups']['status_list'],
                ['.', '_']
                )

            break

    if ret != None:
        groups = ''
        for i in ret['groups']:
            groups += "       {group}: {value}\n".format_map(
                {
                    'group': i,
                    'value': repr(ret['groups'][i])
                    }
                )

        s = "Match `{filename}'\n{groups}".format_map({
            'filename': filename,
            'groups': groups
            })

        if mute:
            logging.debug(s)
        else:
            logging.info(s)

    logging.debug("Parsing package file name {} result\n{}".format(filename, repr(ret)))

    return ret

def find_possible_chared_versions(name_sliced, separator='.'):

    versions = []

    version_started = None
    version_ended = None

    index = -1

    for i in name_sliced:
        index += 1

        if i.isdecimal():

            if version_started == None:
                version_started = index

            version_ended = index

        else:

            if version_started != None:
                if i != separator:
                    versions.append((version_started, version_ended + 1,))
                    version_started = None


    if version_started != None:
        versions.append((version_started, version_ended + 1,))
        version_started = None

    return versions

def find_possible_versions(name_sliced):
    ret = {}
    for i in ['.', '_']:
        ret[i] = find_possible_chared_versions(name_sliced, i)
    return ret

def find_most_possible_version(name_sliced, mute=False):

    ret = None

    possible_versions = find_possible_versions(name_sliced)
    logging.debug("possible_versions: {}".format(repr(possible_versions)))

    maximum_length = 0

    for i in ['.', '_']:
        for j in possible_versions[i]:
            l = j[1] - j[0]
            if l > maximum_length:
                maximum_length = l

    if maximum_length == 0:
        s = "Version not found"
        if not mute:
            logging.error(s)
        else:
            logging.debug(s)
        ret = 1
    else:

        lists_to_compare = []

        logging.debug("lists_to_compare: {}".format(repr(lists_to_compare)))

        for i in ['.', '_']:
            for j in possible_versions[i]:
                l = j[1] - j[0]
                if l == maximum_length:
                    lists_to_compare.append(j)

        l = len(lists_to_compare)
        if l == 0:
            ret = None
        else:
            most_possible_version = lists_to_compare[0]

            for i in lists_to_compare:
                if i[0] < most_possible_version[0]:
                    most_possible_version = i

            logging.debug("most_possible_version: {}".format(repr(most_possible_version)))
            ret = most_possible_version

    return ret


def source_name_parse_delicate(filename, mute=False):

    """
    Main source name parsing function

    Do not use this directly, use source_name_parse() instead.
    """

    filename = os.path.basename(filename)

    logging.debug("Parsing source file name {}".format(filename))

    ret = None

    extension = None
    for i in ACCEPTABLE_SOURCE_NAME_EXTENSIONS:
        if filename.endswith(i):
            extension = i

    if extension == None:
        s = "Wrong extension"
        if not mute:
            logging.error(s)
        else:
            logging.debug(s)
        ret = 1
    else:
        without_extension = filename[:-len(extension)]

        name_sliced = org.wayround.utils.text.slice_string_to_sections(without_extension)

        most_possible_version = find_most_possible_version(name_sliced, mute)

        if not isinstance(most_possible_version, tuple):
            ret = None
        else:
            ret = {
                'name': None,
                'groups': {
                    'name'              : None,
                    'extension'         : None,

                    'version'           : None,
                    'version_list_dirty': None,
                    'version_list'      : None,
                    'version_dirty'     : None,

                    'status'            : None,
                    'status_list_dirty' : None,
                    'status_dirty'      : None,
                    'status_list'       : None,
                    }
                }

            ret['name'] = filename

            ret['groups']['name'] = ''.join(
                name_sliced[:most_possible_version[0]]
                ).strip('.-_')

            ret['groups']['version_list_dirty'] = (
                name_sliced[most_possible_version[0]:most_possible_version[1]]
                )

            ret['groups']['version_list'] = (
                copy.copy(ret['groups']['version_list_dirty'])
                )

            org.wayround.utils.list.remove_all_values(
                ret['groups']['version_list'],
                ['.', '_']
                )

            ret['groups']['version'] = (
                '.'.join(ret['groups']['version_list'])
                )

            ret['groups']['version_dirty'] = (
                ''.join(ret['groups']['version_list_dirty'])
                )

            ret['groups']['extension'] = extension


            ret['groups']['status_list'] = (
                name_sliced[most_possible_version[1]:]
                )

            ret['groups']['status_list'] = (
                org.wayround.utils.list.list_strip(
                    ret['groups']['status_list'],
                    ['.', '_', '-', '+']
                    )
                )

            if len(ret['groups']['status_list']) > 0:

                ret['groups']['status_dirty'] = (
                    ''.join(ret['groups']['status_list'])
                    )

                ret['groups']['status_list_dirty'] = (
                    copy.copy(ret['groups']['status_list'])
                    )

                org.wayround.utils.list.remove_all_values(
                    ret['groups']['status_list'],
                    ['.', '_', '-', '~']
                    )


    return ret

def source_name_parse(
    filename,
    modify_info_file=False,
    acceptable_version_number=None,
    mute=False
    ):
    """
    Parse source file name and do some more actions on success

    If this function succeeded but not passed version check -
    return None.

    If this function succided, passeed version check and
    `modify_info_file' is True -
    update infofile in info directory.

    If this function succided, return dict:

        ret = {
            'name': None,
            'groups': {
                'name'              : None,
                'extension'         : None,

                'version'           : None,
                'version_list_dirty': None,
                'version_list'      : None,
                'version_dirty'     : None,

                'status'            : None,
                'status_list_dirty' : None,
                'status_dirty'      : None,
                'status_list'       : None,
                }
            }

    """

    ret = source_name_parse_delicate(filename, mute)

    fnmatched = False
    if isinstance(acceptable_version_number, str):
        if fnmatch.fnmatch(ret['groups']['version'], acceptable_version_number):
            fnmatched = True


    if acceptable_version_number == None or \
            (isinstance(acceptable_version_number, str) and fnmatched):

        if not isinstance(ret, dict):
            logging.debug("No match `{}'".format(filename))

        else:

            groups = ''
            for i in ret['groups']:
                groups += "       {group}: {value}\n".format_map(
                    {
                        'group': i,
                        'value': repr(ret['groups'][i])
                        }
                    )

            s = "Match `{filename}'\n{groups}".format_map({
                'filename': filename,
                'groups': groups
                })

            if mute:
                logging.debug(s)
            else:
                logging.info(s)

        if ret != None and modify_info_file:
            _modify_info_file(ret, mute)

    else:
        ret = None

    return ret

def _modify_info_file(src_filename_parsed, mute=True):
    fn = os.path.join(
        org.wayround.aipsetup.config.config['info'],
        '{}.json'.format(src_filename_parsed['groups']['name'])
        )

    s = "Updating info file {}".format(fn)

    if mute:
        logging.debug(s)
    else:
        logging.info(s)

    data = org.wayround.aipsetup.info.read_from_file(fn)

    if data == None:
        logging.warning("Error reading file. Creating new. {}".format(fn))
        data = org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE

    org.wayround.aipsetup.info.write_to_file(fn, data)

    return

def parse_test():

    for i in DIFFICULT_NAMES:
        logging.info("====== Testing RegExps on `{}' ======".format(i))
        if not isinstance(source_name_parse(i), dict):
            logging.error("Error parsing file name `{}' - RegExp not matched".format(i))
