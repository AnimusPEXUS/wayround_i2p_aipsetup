
"""
Module with package names parsing facilities
"""

import os.path
import re
import fnmatch
import logging
import copy

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
    '.tar',
    '.zip',
    '.7z',
    '.tgz',
    '.tbz2',
    '.tbz'
    ]

ASP_NAME_REGEXPS = {
    'aipsetup2': r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)-(?P<timestamp>\d{14})-(?P<host>.*)$',
    'aipsetup3': r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)-(?P<timestamp>\d{8}\.\d{6}\.\d{7})-(?P<host>.*)$'
    }

ASP_NAME_REGEXPS_COMPILED = {}

for i in ASP_NAME_REGEXPS:
    logging.debug("Compiling `{}'".format(i))
    ASP_NAME_REGEXPS_COMPILED[i] = re.compile(ASP_NAME_REGEXPS[i])

del(i)


def exported_commands():
    return {
        'test_expressions_on_sources': name_test_expressions_on_sources,
        'parse': name_parse_name,
        'parse_test': name_parse_test
        }

def commands_order():
    return [
        'test_expressions_on_sources',
        'parse',
        'parse_test'
        ]

def name_parse_name(opts, args):
    """
    Parse name

    [-w] NAME

    if -w is set - change <name>.xml info file nametype value to
    result
    """

    # TODO: help clarification required

    ret = 0

    if len(args) != 1:
        logging.error("File name required")
        ret = 1
    else:

        filename = args[0]

        write = '-w' in opts

        if source_name_parse(filename, modify_info_file=write) != 0:
            ret = 2

    return ret


def name_test_expressions_on_sources(opts, args):
    """
    Run parsing tests on available source package file names
    """

    ret = 0

    # TODO: Add some more usability
    # TODO: Add immediate package info files update _option_

    logging.info("Testing expressions on sources")
    logging.debug("Looking for source index file")
    try:
        f = open(org.wayround.aipsetup.config.config['source_index'], 'r')
    except:
        logging.exception(
            "Can't open file `{}'".format(
                org.wayround.aipsetup.config.config['source_index']
                )
            )
        ret = 1

    else:
        try:
            lst = f.readlines()

            f.close()

            logging.debug("Stripping lines")
            lst2 = []

            for i in lst:
                lst2.append(i.strip())

            lst = lst2
            del(lst2)

            logging.debug("Sorting lines")
            lst.sort()

            logging.debug("Parsing found filenames")
            for i in lst:

                logging.debug("Parsing file name {}".format(i))

                # TODO: do I need return value?
                source_name_parse(i, False)
        finally:
            f.close()


    return ret


def package_name_parse(filename):

    filename = os.path.basename(filename)

    logging.debug("Parsing package file name {}".format(filename))

    ret = None

    if filename.endswith('.tar.xz'):
        filename = filename[:-7]
    elif filename.endswith('.asp'):
        filename = filename[:-4]
    elif filename.endswith('.xz'):
        filename = filename[:-3]

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
            break

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

        name_sliced = re.findall(r'[a-zA-Z]+|\d+|[\.\-\_\~\+]', without_extension)

        most_possible_version = find_most_possible_version(name_sliced, mute)

        if not isinstance(most_possible_version, tuple):
            ret = None
        else:
            ret = {
                'name': None,
                'groups': {}
                }

            ret['name'] = filename

            ret['groups']['name'] = ''.join(name_sliced[:most_possible_version[0]]).strip('.-_')
            ret['groups']['version_list_dirty'] = name_sliced[most_possible_version[0]:most_possible_version[1]]

            ret['groups']['version_list'] = copy.copy(ret['groups']['version_list_dirty'])

            for i in ['.', '_']:
                while i in ret['groups']['version_list']:
                    ret['groups']['version_list'].remove(i)

            ret['groups']['version'] = '.'.join(ret['groups']['version_list'])
            ret['groups']['version_dirty'] = ''.join(ret['groups']['version_list_dirty'])

            ret['groups']['extension'] = extension


            ret['groups']['status_list'] = name_sliced[most_possible_version[1]:]

            while (len(ret['groups']['status_list']) > 0
                   and  ret['groups']['status_list'][0] in ['.', '_', '-', '+']):
                del ret['groups']['status_list'][0]

            while (len(ret['groups']['status_list']) > 0
                   and ret['groups']['status_list'][-1] in ['.', '_', '-', '+']):
                del ret['groups']['status_list'][-1]

            if len(ret['groups']['status_list']) > 0:

                ret['groups']['status'] = ''.join(ret['groups']['status_list'])

                for i in ['.', '_', '-', '~']:
                    while i in ret['groups']['status_list']:
                        ret['groups']['status_list'].remove(i)


    return ret

def source_name_parse(
    filename,
    modify_info_file=False,
    acceptable_version_number=None,
    mute=False
    ):
    """
    Parse source file name. On success do some more actions.

    If this function succeeded but not passed version check -
    return None.

    If this function succided, passeed version check and
    `modify_info_file' is True -
    update infofile in info directory.

    If this function succided, return dict:

        {
            # original (not parsed) package name
            'name': None,
            # matched soure regular expression name
            # (NAME_REGEXPS in this module)
            're'  : None,
            # matched regular expression's groups
            'groups': {
                'name'                 : None,
                'version'              : None,
                'version_letter'       : None,
                'version_letter_number': None,
                'statuses'             : None,
                'patch'                : None,
                'date'                 : None,
                'extension'            : None
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

        if ret == None:
            logging.debug("No match `{}'".format(filename))

        else:

            groups = ''
            for i in ret['groups']:
                groups += "       %(group)s: %(value)s\n" % {
                    'group': i,
                    'value': repr(ret['groups'][i])
                    }

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
        '%(name)s.xml' % {
            'name': src_filename_parsed['groups']['name']
            }
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

def name_parse_test(args, opts):
    parse_test()
    return 0

def parse_test():

    # FIXME: fix parsers!

    for i in DIFFICULT_NAMES:
        logging.info("====== Testing RegExps on `{}' ======".format(i))
        if not isinstance(source_name_parse(i), dict):
            logging.error("Error parsing file name `{}' - RegExp not matched".format(i))
