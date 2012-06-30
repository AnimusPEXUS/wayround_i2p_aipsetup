# -*- coding: utf-8 -*-

"""
Client-module for searching and getting files on and from
aipsetup package server
"""

import os
import os.path
import sys
import urllib.request, urllib.parse, urllib.error
import subprocess

import aipsetup.version
import aipsetup.name
import aipsetup.info


def print_help():
    """
    help printer
    """
    print("""\
aipsetup client command

   search [-i] [--how=b|r|e|i|c] [--where=r|l] [--what=s|r|i] [-v=VER]
          NAME

      Search files on remote or local UHT server

      -i - NAME is case insensitive

      --how values:

      b - package name begins with NAME
      r - NAME is regular expression
      e - NAME is exact name
      i - assume NAME tobe package info name and get RE for it
      c - NAME is package name substring

      --where values: 'r' or 'l' - is for remote or local access

      --what  values: 's', 'r' or 'i' - is for source, repository or
                      info access

      VER can be 'MAX', 'MIN' or mask '3.2.*', '3.*' etc. default is
          'ANY'

      VER works only with --how=i

   get [-o=DIRNAME] [-i] [--how=b|r|e|i|c] [--where=r|l]
       [--what=s|r|i] [-v=VER] NAME

      Get files from remote or local UHT server

      All options and parameters same as in search, plus -o option

      -o - Place requested files in pointed (by default current)
           directory

""")

def router(opts, args, config):
    """
    aipsetup control router
    """
    ret = 0

    if len(args) == 0:
        print("-e- not enough parameters")
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
            ret = 0

        elif args[0] == 'search':

            wsp = workout_search_params(opts, args, config)

            if not wsp['p_errors'] and not wsp['n_errors']:

                ret = search(config,
                             wsp
                             )

        elif args[0] == 'get':

            wsp = workout_search_params(opts, args, config)

            output = None

            for i in opts:
                if i[0] == '-o':
                    output = i[1]

            if not wsp['p_errors'] and not wsp['n_errors']:

                ret = get(config,
                          output,
                          wsp
                          )

        else:
            print("-e- wrong command")
            ret = 1

    return ret


def workout_search_params(opts, args, config):
    """
    Parse options and parameters for `search' and/or `get'
    """

    args_l = len(args)

    # NOTE: Maybe those variable need tobe refactored, but not now

    what = ''
    how = ''
    where = ''
    sensitive = ''
    value = ''
    n_errors = False
    p_errors = False

    if args_l != 2:
        print("-e- can be one parameter")
        p_errors = True
    else:

        how = 'i'

        for i in opts:
            if i[0] == '--how':
                how = i[1]

        where = 'r'

        for i in opts:
            if i[0] == '--where':
                where = i[1]

        what = 'r'

        for i in opts:
            if i[0] == '--what':
                what = i[1]

        ver = 'ANY'

        for i in opts:
            if i[0] == '-v':
                ver = i[1]

        sensitive = True

        for i in opts:
            if i[0] == '-i':
                sensitive = False


        if not how in 'breic':
            print("-e- `how' error")
            p_errors = True

        if not where in 'rl':
            print("-e- `where' error")
            p_errors = True

        if not what in 'sri':
            print("-e- `what' error")
            p_errors = True

        if how != 'i' and ver != 'ANY':
            print("-e- VERSION can only be used with --how=i")
            p_errors = True


        value = args[1]

        if not p_errors:

            n_errors = False

            if how == 'i':
                idic = aipsetup.info.read_from_file(
                    os.path.join(
                        config['info'], '%(name)s.xml' % {
                            'name': value
                            }
                        )
                    )

                if not isinstance(idic, dict):
                    print("-e- Can't find info for %(name)s" % {
                        'name': value
                        })
                    n_errors = True

                else:

                    if what == 's':
                        regexp = \
                            aipsetup.name.NAME_REGEXPS[idic['pkg_name_type']].replace('(?P<name>.+?)', value)
                        print("-i- Using regexp `%(re)s' from `%(name)s' pkg info" % {
                            're': regexp,
                            'name': value
                            })

                        value = regexp
                        how = 'r'
                        sensitive = True

                    elif what == 'r':
                        regexp = r"%(name)s-(?P<version>.*?)-(?P<date>[\d]*).asp" % {
                            'name': value
                            }
                        print("-i- Using regexp `%(re)s' for pkg name `%(name)s'" % {
                            'name': value,
                            're': regexp
                            })

                        value = regexp
                        how = 'r'
                        sensitive = True

                    elif what == 'i':
                        print("-e- Invalid parameters combination")
                        p_errors = True

                    else:
                        raise ValueError

            if not n_errors and not p_errors:

                hows = {'b': 'begins', 'r': 'regexp',
                        'e': 'exac',   'c': 'contains'}

                whats = {'s': 'source',
                         'r': 'repository',
                         'i': 'info'}

                wheres = {'r': 'remote',
                          'l': 'local'}

                how = hows[how]
                what = whats[what]
                where = wheres[where]

    return dict(
        what = what,
        how = how,
        where = where,
        sensitive = sensitive,
        ver = ver,
        value=value,
        p_errors=p_errors,
        n_errors=n_errors
        )


def get(config, output='.', wsp={}):
    """
    Get files from server

    @param config: aipsetup config from aipsetup.utils.config
    @type config: dict
    @param output: output dircetory
    @type output: basestr
    """

    # We already using `client' here. Same as in `search'.
    # So it's meaningless to use `search' work results!

    ret = 0

    if not os.path.exists(output):
        print("-i- creating %(dir)s" % {
            'dir': output
            })
        try:
            os.makedirs(output)
        except:
            print("-e- Can't create output dir")
            ret = 2
    else:
        if os.path.exists(output) and not os.path.isdir(output):
            print("-e- Destination file exists and is not dir")
            ret = 1

        elif os.path.exists(output) and os.path.isdir(output):
            print("-i- using %(dir)s for output" % {
                'dir': output
                })
        else:
            print("-e- Unknown location :-P")
            raise Exception

    if ret != 0:
        # We have an error here, so nothing to be done more
        pass
    else:
        lst = client(config, wsp)

        if not isinstance(lst, list):
            print("-e- Error getting response list")
            ret = lst
        else:

            lst = fn_version_filter(config, lst, wsp)

            lst.sort(aipsetup.version.version_comparator)

            lst = fn_version_min_max_filter(lst, wsp)

            proto = None
            host = None
            port = None
            prefix = None

            for i in ['proto', 'host', 'port', 'prefix']:
                exec("%(i)s = config['client_%(where)s_%(i)s']" % {
                        'where': wsp['where'],
                        'i': i
                        } )

            semi = ''
            if port != None and port != '':
                semi = ':'

            path = 'files_%(what)s' % {'what': wsp['what']}

            for i in lst:

                name = ''
                if wsp['what'] == 'info':
                    name = '/%(v)s.xml' % {
                        'v': wsp['value']
                        }
                else:
                    name = i

                name = urllib.parse.quote(name)

                request = ("%(proto)s://%(host)s%(semi)s%(port)s%(prefix)s%(path)s%(name)s") % {
                    'proto'     : proto,
                    'host'      : host,
                    'semi'      : semi,
                    'port'      : port,
                    'prefix'    : prefix,
                    'path'      : path,
                    'name'      : name
                    }

                print("-i- Requesting: %(req)s" % {
                    'req': request
                    })

                bname = os.path.basename(i)

                process = subprocess.Popen(['wget',  '-O',  bname, request])
                process.wait()

    return ret


def search(config, wsp):
    """
    Search packages on server using `client' function
    """

    ret = 0

    lst = client(config, wsp)

    if isinstance(lst, list):

        lst = fn_version_filter(config, lst, wsp)

        lst.sort(aipsetup.version.version_comparator)

        lst = fn_version_min_max_filter(lst, wsp)

        for i in lst:
            print(i)

        print("count: %(n)s" % {
            'n': len(lst)
            })

    else:
        print("-e- Error getting response list")
        ret = lst

    return ret

def client(config, wsp={}):
    """
    Central client function before `get' and `search' functions.
    """

    what = None
    how = None
    sensitive = None
    value = None
    where = None

    for i in wsp:
        exec(
            "%(i)s = wsp['%(i)s']" % {
                'i': i
                }
            )

    ret = 0

    if not what in ['info', 'source', 'repository'] \
            or not how in ['regexp', 'begins', 'exac', 'contains'] \
            or not isinstance(sensitive, bool) \
            or not isinstance(value, str):
        print("-e- Wrong parameters")
        ret = 1

    else:

        proto = None
        host = None
        port = None
        prefix = None

        for i in ['proto', 'host', 'port', 'prefix']:
            exec("%(i)s = config['client_%(where)s_%(i)s']" % {
                    'where': where,
                    'i': i
                    } )

        semi = ''
        if port != None and port != '':
            semi = ':'

        sens = ''
        if sensitive:
            sens = '&sensitive=on'

        request = ("%(proto)s://%(host)s%(semi)s%(port)s%(prefix)ssearch?"\
                       + "what=%(what)s&how=%(how)s&"\
                       + "view=list%(sensitive)s&"\
                       + "value=%(value)s") % {
            'proto'     : proto,
            'host'      : host,
            'semi'      : semi,
            'port'      : port,
            'prefix'    : prefix,
            'what'      : what,
            'how'       : how,
            'sensitive' : sens,
            'value'     : urllib.parse.quote(str(value))
            }

        print("-i- Requesting: %(req)s" % {
            'req': request
            })

        try:
            req_res = urllib.request.urlopen(request)
        except:
            exception = sys.exc_info()
            if isinstance(exception[1],  IOError):
                print("-e- Connection refused")
            aipsetup.utils.error.print_exception_info(
                exception
                )
            ret = 1
        else:
            code = int(req_res.getcode())
            if code != 200:
                print("-e- Response code: %(n)d" % {
                    'n': code
                    })
                ret = 2
            else:
                lst = req_res.readlines()
                lst2 = []
                for i in lst:
                    stripped = i.strip()
                    if stripped != '':
                        lst2.append(stripped)
                ret = lst2

    return ret


def fn_version_filter(config, lst, wsp):
    """
    Filter list by version.
    """

    # NOTE: The problem of this function, is what:
    #       to filter filenames by version - we need
    #       to parse them again :-( .
    #
    #       Additionaly we need to keep in mind passability
    #       of a large list before filter in client!
    #       So we needet to separate version filter in to
    #       different function -- to save memory, maybe
    #       in a price on performance

    ret = []
    if not wsp['ver'] in ['MAX', 'MIN', 'ANY']:

        for i in lst:
            if aipsetup.name.source_name_parse(
                config,
                i,
                mute=True,
                modify_info_file=False,
                acceptable_vn=wsp['ver']
                ) != None:

                ret.append(i)

    else:
        ret = lst

    return ret

def fn_version_min_max_filter(lst, wsp):
    """
    Return only maximal or minimal source file name from list

    List must be sorted using aipsetup.version.version_comparator
    before being passed to this function.
    """

    lst2 = []

    if wsp['ver'] == 'MAX':
        lst2 = [lst[-1]]
    elif wsp['ver'] == 'MIN':
        lst2 = [lst[0]]
    else:
        lst2 = lst

    return lst2
