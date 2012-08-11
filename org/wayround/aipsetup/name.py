
"""
Module with package names parsing facilities
"""

import os.path
import re
import fnmatch
import logging

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config


NAME_REGEXPS_ORDER = [
    'universal'
    ]

NAME_REGEXPS = {
    'universal': (
        r'^{universal_name}(?:[\-\._]?){universal_version}{universal_extensions}$'
        ),
    }

NAME_REGEXPS_COMPILED = {}

for i in list(NAME_REGEXPS.keys()):
    logging.debug("Expending `{}'".format(i))
    NAME_REGEXPS[i] = NAME_REGEXPS[i].format_map({
        'universal_extensions' : (
            r'(?P<extension>(\.tar\.gz|\.tar\.bz2|\.tar\.xz|\.tar\.lzma|\.tar|\.zip|\.7z|\.tgz|\.tbz2|\.tbz))'
            ),

        'universal_name'       : r'(?P<name>[0-9a-zA-Z_\-\+]+?)',
        'universal_version'    : r'(?P<version>\d+[\-_\.]?(?:(?:\d|[a-zA-Z])+[\-_\.\~]?)*)'
        })
    logging.debug(NAME_REGEXPS[i])

for i in list(NAME_REGEXPS.keys()):
    logging.debug("Compiling `{}'".format(i))
    NAME_REGEXPS_COMPILED[i] = re.compile(NAME_REGEXPS[i])

del(i)

class RegexpsError(Exception): pass

# Ensure exception in case something missed
for each in NAME_REGEXPS_ORDER:
    if not each in NAME_REGEXPS:
        raise RegexpsError("{} absent in NAME_REGEXPS".format(each))

for each in NAME_REGEXPS:
    if not each in NAME_REGEXPS_ORDER:
        raise RegexpsError("{} absent in NAME_REGEXPS_ORDER".format(each))

del(each)

ASP_NAME_REGEXPS = {
    'aipsetup2': r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)-(?P<timestamp>\d{14})-(?P<host>.*)$',
    'aipsetup3': r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)-(?P<timestamp>\d{8}\.\d{6}\.\d{7})-(?P<host>.*)$'
    }

ASP_NAME_REGEXPS_COMPILED = {}

for i in ASP_NAME_REGEXPS:
    logging.debug("Compiling {}".format(i))
    ASP_NAME_REGEXPS_COMPILED[i] = re.compile(ASP_NAME_REGEXPS[i])

del(i)


def exported_commands():
    return {
        'test_expressions_on_sources': name_test_expressions_on_sources,
        'parse_name': name_parse_name
        }

def commands_order():
    return ['test_expressions_on_sources', 'parse_name']

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



def source_name_parse(
    filename,
    modify_info_file=False,
    acceptable_version_number=None,
    mute=False
    ):

    """
    Parse source file name. On success do some more actions.

    If this function succided but not passed version check -
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

    logging.debug("Parsing source file name {}".format(filename))

    ret = None

    filename = os.path.basename(filename)

    re_r = None

    # Find matching regular expression
    for j in NAME_REGEXPS_ORDER:

        s = "Matching `{}'".format(j)
        if mute:
            logging.debug(s)
        else:
            logging.info(s)


        re_r = NAME_REGEXPS_COMPILED[j].match(filename)

        if re_r != None:
            break

    # Perform file name elements separation
    if re_r != None:
        ret = {
            'name': None,
            're'  : None,
            'groups': {
                'name'                 : None,
                'version'              : None,
                'version_list'         : None,
                'extension'            : None
                }
            }

        for i in ret['groups']:
            try:
                ret['groups'][i] = re_r.group(i)
            except:
                ret['groups'][i] = ''


        for k in re_r.re.groupindex:
            ret['groups'][k] = re_r.group(re_r.re.groupindex[k])


        fnmatched = False
        if isinstance(acceptable_version_number, str):
            if fnmatch.fnmatch(ret['groups']['version'], acceptable_version_number):
                fnmatched = True


        if acceptable_version_number == None or \
                (isinstance(acceptable_version_number, str) and fnmatched):


            ret['groups']['version'] = (
                ret['groups']['version'].replace('_', '.')
                )

            ret['groups']['version'] = (
                ret['groups']['version'].replace('-', '.')
                )

            ret['groups']['version'] = (
                ret['groups']['version'].strip('.')
                )

            ret['groups']['version_list'] = (
                ret['groups']['version'].split('.')
                )

            if '' in ret['groups']['version_list']:
                ret['groups']['version_list'].remove('')


            ret['name'] = filename
            ret['re'] = j

        else:
            ret = None

    del(re_r)


    if ret == None:
        logging.debug("No match `{}'".format(filename))

    else:

        groups = ''
        for i in ret['groups']:
            groups += "       %(group)s: %(value)s\n" % {
                'group': i,
                'value': repr(ret['groups'][i])
                }

        s = "Match `{filename}' `{re}'\n{groups}".format_map({
            'filename': filename,
            're': j,
            'groups': groups
            })

        if mute:
            logging.debug(s)
        else:
            logging.info(s)


    if ret != None and modify_info_file:
        fn = os.path.join(
            org.wayround.aipsetup.config.config['info'],
            '%(name)s.xml' % {
                'name': ret['groups']['name']
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

        data['pkg_name_type'] = ret['re']

        org.wayround.aipsetup.info.write_to_file(fn, data)

    return ret
