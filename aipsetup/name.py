
import os.path
import re
import sys


NAME_REGEXPS = {
    'standard': \
        r'%(standard_name)s-%(standard_version)s%(standard_extensions)s',

    'standard_with_date': \
        r'%(standard_name)s-%(standard_version)s-%(date)s%(standard_extensions)s',

    'standard_underscores': \
        r'%(standard_name)s_%(underscored_version)s%(standard_extensions)s',

    'standard_underscores_with_date': \
        r'%(standard_name)s_%(underscored_version)s_%(date)%(standard_extensions)s',

    'standard_with_letter_after_version': \
        r'%(standard_name)s-%(standard_version)s(?P<version_letter>[a-zA-Z])(?P<version_letter_number>\d*)%(standard_extensions)s',

    'standard_with_status': \
        r'%(standard_name)s-%(standard_version)s%(standard_statuses)s%(standard_extensions)s',

    'standard_underscores_with_status': \
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
        'standard_name'       : r'(?P<name>.*?)',
        'standard_version'    : r'(?P<version>(\d+\.??)+)',
        'standard_statuses'   : r'(?P<status>([-\.][a-zA-Z]+\d*[a-zA-Z]?\d*)+)',
        'underscored_version' : r'(?P<version>(\d+_??)+)',
        'underscored_statuses': r'(?P<status>([_\.][a-zA-Z]+\d*[a-zA-Z]?\d*)+)',
        'date'                : r'(?P<date>\d{8,16})'
        }

def print_help():
    print """\
"""

def router(opts, args, config):
    ret = 0

    if len(args) == 0:
        print "-e- not enough parameters"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
            ret = 0

        elif args[0] == 'test_expressions_on_sources':
            test_expressions_on_sources(config)


    return ret

def test_expressions_on_sources(config):

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

        bn = os.path.basename(i)

        match_found = False

        for j in ['standard_with_date',
                  'standard',
                  'standard_underscores_with_date',
                  'standard_underscores',
                  'standard_with_letter_after_version',
                  'standard_with_status',
                  'standard_underscores_with_status',
                  'version_right_after_name',
                  'version_right_after_name_with_status'
                  ]:

            print "-i- Matching `%(re)s'" % {
                're': j
                }
            re_r = re.match(NAME_REGEXPS[j], bn)

            if re_r  != None:


                groups = ''

                for k in re_r.re.groupindex:

                    groups += "       %(group)s:`%(value)s'\n" % {
                        'group': k,
                        'value': re_r.group(re_r.re.groupindex[k])
                        }

                print "-i- Match `%(i)s' `%(re)s'\n%(groups)s" % {
                    'i': bn,
                    're': j,
                    'groups': groups
                    }
                match_found = True

            del(re_r)

            if match_found:
                break

        if not match_found:
            print "-e- No match `%(i)s'" % {
                'i': bn
                }

        print ""
        sys.stdout.flush()

    return

def source_name_parse(name, nametype):

    d = {
        'name': '',
        'version': '',
        'version_letter': '',
        'extension': '',
        'status': '',
        'status_ver': '',
        'patch': ''
        }

    r = re.match(NAME_REGEXPS[nametype], name)

    if r != None:
        for i in d:
            try:
                d[i] = r.group(i)
            except:
                d[i] = ''

    if d['status'] in ['a', 'alpha']:
       d['status'] = 'alpha'

    elif d['status'] in ['b', 'beta']:
        d['status'] = 'beta'

    elif d['status'] in ['rc']:
        d['status'] = 'rc'

    elif d['status'] in ['pre', 'p']:
        d['status'] = 'pre'


    return d


def asp_name_parse():
    pass
