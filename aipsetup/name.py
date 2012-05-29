
import os.path
import re
import sys
import fnmatch

import aipsetup.info

class RegexpsError(Exception):
    pass


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
        r'%(standard_name)s-%(standard_version)s%(standard_extensions)s',

    'standard_with_date': \
        r'%(standard_name)s-%(standard_version)s-%(date)s%(standard_extensions)s',

    'underscored': \
        r'%(standard_name)s_%(underscored_version)s%(standard_extensions)s',

    'underscored_with_date': \
        r'%(standard_name)s_%(underscored_version)s_%(date)%(standard_extensions)s',

    'standard_with_letter_after_version': \
        r'%(standard_name)s-%(standard_version)s(?P<version_letter>[a-zA-Z])(?P<version_letter_number>\d*)%(standard_extensions)s',

    'standard_with_status': \
        r'%(standard_name)s-%(standard_version)s%(standard_statuses)s%(standard_extensions)s',

    'underscored_with_status': \
        r'%(standard_name)s_%(underscored_version)s%(underscored_statuses)s%(standard_extensions)s',

    'version_right_after_name': \
        r'%(standard_name)s%(standard_version)s%(standard_extensions)s',

    'version_right_after_name_with_status': \
        r'%(standard_name)s%(standard_version)s[-\.]?%(standard_statuses)s%(standard_extensions)s'

    }


for i in NAME_REGEXPS:
    NAME_REGEXPS[i] = NAME_REGEXPS[i] % {
        'statuses'            : r'pre|alpha|beta|rc|test|source|src|dist|full',
        'standard_extensions' : r'(?P<extension>\.tar\.gz|\.tar\.bz2|\.tar\.xz|\.tar\.lzma|\.tar|\.zip|\.7z|\.tgz|\.tbz2)',
        'standard_name'       : r'(?P<name>.+?)',
        'standard_version'    : r'(?P<version>(\d+\.??)+)',
        'standard_statuses'   : r'(?P<statuses>([-\.][a-zA-Z]+\d*[a-zA-Z]?\d*)+)',
        'underscored_version' : r'(?P<version>(\d+_??)+)',
        'underscored_statuses': r'(?P<statuses>([_\.][a-zA-Z]+\d*[a-zA-Z]?\d*)+)',
        'date'                : r'(?P<date>\d{8,16})'
        }

del(i)

# Ensure exception in case something missed
for each in NAME_REGEXPS_ORDER:
    if not each in NAME_REGEXPS:
        raise RegexpsError

for each in NAME_REGEXPS:
    if not each in NAME_REGEXPS_ORDER:
        raise RegexpsError

del(each)


def print_help():
    print """\

   test_expressions_on_sources


   parse_name [-w] NAME

     if -w is set - change <name>.xml info file nametype value to
     result

"""

def router(opts, args, config):
    ret = 0

    args_l = len(args)

    if args_l == 0:
        print "-e- not enough parameters"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
            ret = 0

        elif args[0] == 'test_expressions_on_sources':
            test_expressions_on_sources(config)

        elif args[0] == 'parse_name':

            if args_l != 2:
                print "-e- file name required"
            else:

                filename = args[1]

                write = False
                for i in opts:
                    if i[0] == '-w':
                        write = True

                source_name_parse(config, filename, mute=False,
                                  modify_info_file=write)

        else:
            print "-e- Wrong command"

    return ret

def test_expressions_on_sources(config):

    # TODO: Add some more usability
    # TODO: Add immediate package info files update _option_

    f = open(config['source_index'], 'r')

    lst = f.readlines()

    f.close()

    lst2 = []

    for i in lst:
        lst2.append(i.strip())

    lst = lst2
    del(lst2)

    lst.sort()

    for i in lst:

        source_name_parse(config, i, False, False)

        print ""
        sys.stdout.flush()

    return


def asp_name_parse():
    pass


def source_name_parse(config, filename, mute=False,
                      modify_info_file=False, acceptable_vn=None):
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
            # matched regular expression
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

    ret = None

    bn = os.path.basename(filename)

    re_r = None

    # Find matching regular expression
    for j in NAME_REGEXPS_ORDER:

        if not mute:
            print "-i- Matching `%(re)s'" % {
                're': j
                }
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
        if isinstance(acceptable_vn, basestring):
            if fnmatch.fnmatch(ret['groups']['version'], acceptable_vn):
                fnmatched = True


        if acceptable_vn == None or \
                (isinstance(acceptable_vn, basestring) and fnmatched):

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


    if not mute:
        if ret == None:
            print "-e- No match `%(i)s'" % {
                'i': bn
                }

        else:

            groups = ''
            for i in ret['groups']:
                groups += "       %(group)s: %(value)s\n" % {
                    'group': i,
                    'value': repr(ret['groups'][i])
                    }

            print "-i- Match `%(bn)s' `%(re)s'\n%(groups)s" % {
                'bn': bn,
                're': j,
                'groups': groups
                }


    if ret != None and modify_info_file:
        fn = os.path.join(
            config['info'],
            '%(name)s.xml' % {
                'name': ret['groups']['name']
                }
            )

        if not mute:
            print "-i- Updating info file %(name)s" % {
                'name': fn
                }


        data = aipsetup.info.read_from_file(
            fn
            )

        if data == None:
            if not mute:
                print "-i- Error reading file. Creating new."
            data = aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE

        data['pkg_name_type'] = ret['re']

        aipsetup.info.write_to_file(fn, data)

    return ret
