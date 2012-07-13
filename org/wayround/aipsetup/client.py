
"""
Client for searching and getting files on and from aipsetup package server
"""

import os.path
import sys
import urllib.request, urllib.parse
import subprocess
import logging

import org.wayround.utils

import org.wayround.aipsetup.version
import org.wayround.aipsetup.name
import org.wayround.aipsetup.info
import org.wayround.aipsetup.config

def help_text():
    return """\
{aipsetup} {command} command

    search

    get
"""

def exported_commands():
    return {
        'search': client_search,
        'get': client_get
        }

def commands_order():
    return ['search', 'get']


def client_search(opts, args):
    """
    [-i] [--how=b|r|e|i|c] [--what=s|r|i] [-v=VER]
           NAME

    Search files on LUST server

    -i - NAME is case insensitive

    --how values:

    b - package name begins with NAME
    r - NAME is regular expression
    e - NAME is exact name
    i - assume NAME to be package info name and get RE for it
    c - NAME is package name substring

    --what  values: 's', 'r' or 'i' - is for source, repository or
                    info access

    VER can be 'MAX', 'MIN' or mask '3.2.*', '3.*' etc. default is
        'ANY'

    VER works only with --how=i
    """

    ret = 0
    wsp = workout_search_params(opts, args)

    if not wsp['p_errors'] and not wsp['n_errors']:

        ret = search(wsp)

    return ret

def client_get(opts, args):
    """
    [-o=DIRNAME] [-i] [--how=b|r|e|i|c]
    [--what=s|r|i] [-v=VER] NAME

    Get files from LUST server

    All options and parameters same as in search, plus -o option

    -o - Place requested files in pointed (by default current)
         directory
    """

    ret = 0

    wsp = workout_search_params(opts, args)

    output = None

    if '-o' in opts:
        output = opts['-o']

    if not wsp['p_errors'] and not wsp['n_errors']:

        ret = get(output, wsp)

    return ret



def workout_search_params(opts, args):
    """
    Parse options and parameters for `search' and/or `get'
    """

    args_l = len(args)

    # NOTE: Maybe those variable need to be refactored, but not now

    what = ''
    how = ''
    sensitive = ''
    value = ''
    n_errors = False
    p_errors = False

    if args_l != 1:
        logging.error("can be only one argument")
        p_errors = True
    else:

        how = 'i'
        what = 'r'
        ver = 'ANY'
        sensitive = True

        if '--how' in opts:
            how = opts['--how']

        if '--what' in opts:
            what = opts['--what']

        if '-v' in opts:
            ver = opts['-v']

        if '-i' in opts:
            sensitive = False


        if not how in 'breic':
            logging.error("`how' wrong value")
            p_errors = True

        if not what in 'sri':
            logging.error("`what' wrong value")
            p_errors = True

        if how != 'i' and ver != 'ANY':
            logging.error("`VERSION' can only be used with --how=i")
            p_errors = True


        value = args[1]

        if not p_errors:

            n_errors = False

            if how == 'i':
                idic = org.wayround.aipsetup.info.read_from_file(
                    os.path.join(
                        org.wayround.aipsetup.config.config['info'],
                        '%(name)s.xml' % {
                            'name': value
                            }
                        )
                    )

                if not isinstance(idic, dict):
                    logging.error("Can't find info for %(name)s" % {
                        'name': value
                        })
                    n_errors = True

                else:

                    if what == 's':
                        regexp = \
                            org.wayround.aipsetup.name.NAME_REGEXPS[idic['pkg_name_type']].replace('(?P<name>.+?)', value)
                        logging.info("Using regexp `%(re)s' from `%(name)s' pkg info" % {
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
                        logging.info("Using regexp `%(re)s' for pkg name `%(name)s'" % {
                            'name': value,
                            're': regexp
                            })

                        value = regexp
                        how = 'r'
                        sensitive = True

                    elif what == 'i':
                        logging.error("Invalid parameters combination")
                        p_errors = True

                    else:
                        raise ValueError

            if not n_errors and not p_errors:

                hows = {'b': 'begins', 'r': 'regexp',
                        'e': 'exac', 'c': 'contains'}

                whats = {'s': 'source',
                         'r': 'repository',
                         'i': 'info'}


                how = hows[how]
                what = whats[what]

    return dict(
        what=what,
        how=how,
        sensitive=sensitive,
        ver=ver,
        value=value,
        p_errors=p_errors,
        n_errors=n_errors
        )


def get(output='.', wsp={}):
    """
    Get files from server

    @param config: aipsetup config from utils.config
    @type config: dict
    @param output: output dircetory
    @type output: basestr
    """

    # We already using `client' here. Same as in `search'.
    # So it's meaningless to use `search' work results!

    ret = 0

    if not os.path.exists(output):
        logging.info("creating %(dir)s" % {
            'dir': output
            })
        try:
            os.makedirs(output)
        except:
            logging.error("Can't create output dir")
            ret = 2
    else:
        if os.path.exists(output) and not os.path.isdir(output):
            logging.error("Destination file exists and is not dir")
            ret = 1

        elif os.path.exists(output) and os.path.isdir(output):
            logging.info("using %(dir)s for output" % {
                'dir': output
                })
        else:
            logging.error("Unknown location :-P")
            raise Exception

    if ret != 0:
        # We have an error here, so nothing to be done more
        pass
    else:
        lst = client(wsp)

        if not isinstance(lst, list):
            logging.error("Error getting response list")
            ret = lst
        else:

            lst = fn_version_filter(lst, wsp)

            lst.sort(org.wayround.aipsetup.version.version_comparator)

            lst = fn_version_min_max_filter(lst, wsp)

            proto = None
            host = None
            port = None
            prefix = None

            for i in ['proto', 'host', 'port', 'prefix']:
                exec("%(i)s = config['client_%(i)s']" % {
                        'i': i
                        })

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

                logging.info("Requesting: %(req)s" % {
                    'req': request
                    })

                bname = os.path.basename(i)

                process = subprocess.Popen(['wget', '-O', bname, request])
                process.wait()

    return ret


def search(wsp):
    """
    Search packages on server using `client' function
    """

    ret = 0

    lst = client(wsp)

    if isinstance(lst, list):

        lst = fn_version_filter(lst, wsp)

        lst.sort(org.wayround.aipsetup.version.version_comparator)

        lst = fn_version_min_max_filter(lst, wsp)

        for i in lst:
            print(i)

        print("count: %(n)s" % {
            'n': len(lst)
            })

    else:
        logging.error("Error getting response list")
        ret = lst

    return ret

def client(wsp):
    """
    Central client function before `get' and `search' functions.
    """

    what = None
    how = None
    sensitive = None
    value = None

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
        logging.error("Wrong parameters")
        ret = 1

    else:

        proto = None
        host = None
        port = None
        prefix = None

        for i in ['proto', 'host', 'port', 'prefix']:
            exec("%(i)s = config['client_%(i)s']" % {
                    'i': i
                    })

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

        logging.info("Requesting: %(req)s" % {
            'req': request
            })

        try:
            req_res = urllib.request.urlopen(request)
        except:
            exception = sys.exc_info()
            if isinstance(exception[1], IOError):
                logging.error("Connection refused")
            org.wayround.utils.error.print_exception_info(
                exception
                )
            ret = 1
        else:
            code = int(req_res.getcode())
            if code != 200:
                logging.error("Response code: %(n)d" % {
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


def fn_version_filter(lst, wsp):
    """
    Filter list by version.
    """

    # NOTE: The problem of this function, is what:
    #       to filter filenames by version - we need
    #       to parse them again :-( .
    #
    #       Additionally we need to keep in mind possibility
    #       of a large list before filter in client!
    #       So we needed to separate version filter in to
    #       different function -- to save memory, maybe
    #       in a price on performance

    ret = []
    if not wsp['ver'] in ['MAX', 'MIN', 'ANY']:

        for i in lst:
            if org.wayround.aipsetup.name.source_name_parse(
                i,
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

    List must be sorted using version.version_comparator
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
