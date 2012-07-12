
import os.path
import re
import fnmatch
import logging

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config


NAME_REGEXPS_ORDER = [
    'standard_with_date',
    'standard',
    'underscored_with_date',
    'underscored',
    'standard_with_letter_after_version',
    'standard_with_status',
    'underscored_with_status',
    'version_right_after_name',
    'version_right_after_name_with_status'
    ]

NAME_REGEXPS = {
    'standard': \
        r'^{standard_name}-{standard_version}{standard_extensions}$',

    'standard_with_date': \
        r'^{standard_name}-{standard_version}-{date}{standard_extensions}$',

    'underscored': \
        r'^{standard_name}_{underscored_version}{standard_extensions}$',

    'underscored_with_date': \
        r'^{standard_name}_{underscored_version}_{date}{standard_extensions}$',

    'standard_with_letter_after_version': \
        r'^{standard_name}-{standard_version}(?P<version_letter>[a-zA-Z])(?P<version_letter_number>\d*){standard_extensions}$',

    'standard_with_status': \
        r'^{standard_name}-{standard_version}{standard_statuses}{standard_extensions}$',

    'underscored_with_status': \
        r'^{standard_name}_{underscored_version}{underscored_statuses}{standard_extensions}$',

    'version_right_after_name': \
        r'^{standard_name}{standard_version}{standard_extensions}$',

    'version_right_after_name_with_status': \
        r'^{standard_name}{standard_version}[-\.]?{standard_statuses}{standard_extensions}$'

    }

for i in NAME_REGEXPS:
    logging.debug("Expending {}".format(i))
    NAME_REGEXPS[i] = NAME_REGEXPS[i].format_map({
        'statuses'            : r'pre|alpha|beta|rc|test|source|src|dist|full',
        'standard_extensions' : r'(?P<extension>\.tar\.gz|\.tar\.bz2|\.tar\.xz|\.tar\.lzma|\.tar|\.zip|\.7z|\.tgz|\.tbz2|\.tbz)',
        'standard_name'       : r'(?P<name>.+?)',
        'standard_version'    : r'(?P<version>(\d+\.??)+)',
        'standard_statuses'   : r'(?P<statuses>([-\.][a-zA-Z]+\d*[a-zA-Z]?\d*)+)',
        'underscored_version' : r'(?P<version>(\d+_??)+)',
        'underscored_statuses': r'(?P<statuses>([_\.][a-zA-Z]+\d*[a-zA-Z]?\d*)+)',
        'date'                : r'(?P<date>\d{8,16})'
        })

del(i)

class RegexpsError(Exception): pass

# Ensure exception in case something missed
for each in NAME_REGEXPS_ORDER:
    if not each in NAME_REGEXPS:
        raise RegexpsError

for each in NAME_REGEXPS:
    if not each in NAME_REGEXPS_ORDER:
        raise RegexpsError

del(each)

ASP_NAME_REGEXPS = {
    'aipsetup2': r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)-(?P<timestamp>\d{14})-(?P<host>.*)$',
    'aipsetup3': r'^(?P<name>.+?)-(?P<version>(\d+\.??)+)-(?P<timestamp>\d{8}\.\d{6}\.\d{7})-(?P<host>.*)$'
    }

def help_text():
    return """\

{aipsetup} {command} command

    test_expressions_on_sources


    parse_name [-w] NAME

        if -w is set - change <name>.xml info file nametype value to
        result
"""

def exported_commands():
    return {
        'test_expressions_on_sources': name_test_expressions_on_sources,
        'parse_name': name_parse_name
        }

def name_parse_name(opts, args):

    ret = 0

    if len(args) != 2:
        print("-e- file name required")
        ret = 1
    else:

        filename = args[1]

        write = False
        if '-w' in opts:
            write = True

        source_name_parse(filename, modify_info_file=write)

    return ret


def name_test_expressions_on_sources(opts, args):

    ret = 0

    # TODO: Add some more usability
    # TODO: Add immediate package info files update _option_

    logging.info("Testing expressions on sources")
    logging.debug("Looking for source index file")
    try:
        f = open(org.wayround.aipsetup.config.config['source_index'], 'r')
    except:
        logging.error(
            "Can't open file {}".format(
                org.wayround.aipsetup.config.config['source_index']
                )
            )
        ret = 1

    else:
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


    return ret


def package_name_parse(filename):

    logging.debug("Parsing package file name {}".format(filename))

    ret = None

    if filename.endswith('.tar.xz'):
        filename = filename[:-7]
    elif filename.endswith('.asp'):
        filename = filename[:-4]
    elif filename.endswith('.xz'):
        filename = filename[:-3]

    for i in ASP_NAME_REGEXPS:
        re_res = re.match(ASP_NAME_REGEXPS[i], filename)
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



def source_name_parse(filename, modify_info_file=False, acceptable_vn=None):
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

    bn = os.path.basename(filename)

    re_r = None

    # Find matching regular expression
    for j in NAME_REGEXPS_ORDER:

        logging.info("Matching `{}'".format(j))

        re_r = re.match(NAME_REGEXPS[j], bn)

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
                'version_letter'       : None,
                'version_letter_number': None,
                'statuses'             : None,
                'patch'                : None,
                'date'                 : None,
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
        if isinstance(acceptable_vn, str):
            if fnmatch.fnmatch(ret['groups']['version'], acceptable_vn):
                fnmatched = True


        if acceptable_vn == None or \
                (isinstance(acceptable_vn, str) and fnmatched):

            ret['groups']['version'] = \
                ret['groups']['version'].replace('_', '.')

            ret['groups']['version'] = \
                ret['groups']['version'].strip('.')

            ret['groups']['statuses'] = \
                ret['groups']['statuses'].replace('_', '-')

            ret['groups']['statuses'] = \
                ret['groups']['statuses'].replace('.', '-')

            ret['groups']['statuses'] = \
                ret['groups']['statuses'].strip('-')

            ret['groups']['statuses_list'] = \
                ret['groups']['statuses'].split('-')

            if '' in ret['groups']['statuses_list']:
                ret['groups']['statuses_list'].remove('')


            ret['name'] = bn
            ret['re'] = j

        else:
            ret = None

    del(re_r)


    if ret == None:
        logging.debug("No match `{}'".format(bn))

    else:

        groups = ''
        for i in ret['groups']:
            groups += "       %(group)s: %(value)s\n" % {
                'group': i,
                'value': repr(ret['groups'][i])
                }

        logging.info("Match `{bn}' `{re}'\n{groups}".format_map({
            'bn': bn,
            're': j,
            'groups': groups
            })
            )


    if ret != None and modify_info_file:
        fn = os.path.join(
            org.wayround.aipsetup.config.config['info'],
            '%(name)s.xml' % {
                'name': ret['groups']['name']
                }
            )

        logging.info("Updating info file {}".format(fn))

        data = org.wayround.aipsetup.info.read_from_file(fn)

        if data == None:
            logging.warning("Error reading file. Creating new. {}".format(fn))
            data = org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE

        data['pkg_name_type'] = ret['re']

        org.wayround.aipsetup.info.write_to_file(fn, data)

    return ret
