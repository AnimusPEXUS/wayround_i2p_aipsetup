import os
import os.path
import sys
import urllib

import utils
import version
import name


def print_help():
    print """\
aipsetup client command

   search [-i] [--how=b|r|e|i|c] [--where=r|l] [--what=s|r|i] NAME [VERSION]

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

      VERSION can be 'MAX', 'MIN' or mask '3.2.*', '3.*' etc. default
              is 'ANY'

      VERSION works only with --how=i

   get [-o[=DIRNAME]] [--how=b|r|e|i|c] [--where=r|l] [--what=s|r|i]
       NAME [VERSION]

      Get files from remote or local UHT server

      All options and parameters same as in search, plus -o option

      -o - Place requested files in pointed (by default current)
           directory

"""

def workout_search_params(opts, args, config):

    import pkgindex

    args_l = len(args)

    what = ''
    how = ''
    where = ''
    sensitive = ''
    value = ''
    n_errors = False
    p_errors = False

    if args_l != 2 and args_l != 3:
        print "-e- can be one or two parameters"
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

        if args_l == 3:
            ver = args[2]

        sensitive = True

        for i in opts:
            if i[0] == '-i':
                sensitive = False


        if not how in 'breic':
            print "-e- `how' error"
            p_errors = True

        if not where in 'rl':
            print "-e- `where' error"
            p_errors = True

        if not what in 'sri':
            print "-e- `what' error"
            p_errors = True

        if how != 'i' and ver != 'ANY':
            print "-e- VERSION can only be used with --how=i"
            p_errors = True


        value = args[1]

        if not p_errors:

            n_errors = False

            if how == 'i':
                r = pkgindex.PackageDatabase(config)
                idic = r.package_info_record_to_dict(name=value)
                del(r)

                if idic == None:
                    print "-e- Can't find info for %(name)s" % {
                        'name': value
                        }
                    n_errors = True

                else:

                    if what == 's':
                        regexp = name.NAME_REGEXPS[idic['pkg_name_type']].replace('(?P<name>.+?)', value)
                        print "-i- Using regexp `%(re)s' from `%(name)s' pkg info" % {
                            're': regexp,
                            'name': value
                            }

                        value = regexp
                        how = 'r'
                        sensitive = True

                    elif what == 'r':
                        regexp = r"%(name)s-(?P<version>.*?)-(?P<date>[\d]*).asp" % {
                            'name': value
                            }
                        print "-i- Using regexp `%(re)s' for pkg name `%(name)s'" % {
                            'name': value,
                            're': regexp
                            }

                        value = regexp
                        how = 'r'
                        sensitive = True

                    elif what == 'i':
                        print "-e- Invalid parameters combination"
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


def router(opts, args, config):

    ret = 0

    if len(args) == 0:
        print "-e- not enough parameters"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
            ret = 0

        elif args[0] == 'search':

            wsp = workout_search_params(opts, args, config)

            if not wsp['p_errors'] and not wsp['n_errors']:

                result = search(config,
                                wsp
                                )

        elif args[0] == 'get':

            wsp = workout_search_params(opts, args, config)

            output = None

            for i in opts:
                if i[0] == '-o':
                    output = i[1]


            if not wsp['p_errors'] and not wsp['n_errors']:

                result = get(config,
                             output,
                             wsp
                             )


        else:
            print "-e- wrong command"
            ret = 1

    return ret


def get(config, output=None, wsp={}):

    ret = 0

    if not output == None:
        if os.path.exists(output) and not os.path.isdir(output):
            print "-e- Destination file exists and is not dir"
            ret = 1

        elif os.path.exists(output) and os.path.isdir(output):
            print "-i- using %(dir)s for output" % {
                'dir': output
                }
        elif not os.path.exists(output):
            print "-i- creating %(dir)s" % {
                'dir': output
                }
            try:
                os.path.makedirs(output)
            except:
                print "-e- Can't create output dir"
                ret = 2

    if ret != 0:
        pass
    else:

        lst = client(config, wsp)

        if not isinstance(lst, list):
            ret = lst
            print "-e- Error getting response list"

        else:

            lst.sort(version.version_comparator)

            for i in ['proto', 'host', 'port', 'prefix']:
                exec("%(i)s = config['client_%(where)s_%(i)s']" % {
                        'where': where,
                        'i': i
                        } )

            semi = ''
            if port != None and port != '':
                semi = ':'

            path = 'files_%(what)s' % {'what': what}

            for i in lst:

                name = ''
                if what == 'info':
                    name = '/%(v)s.xml' % {
                        'v': value
                        }
                else:
                    name = i

                name = urllib.quote(name)

                request = "%(proto)s://%(host)s%(semi)s%(port)s%(prefix)s%(path)s%(name)s" % {
                    'proto'     : proto,
                    'host'      : host,
                    'semi'      : semi,
                    'port'      : port,
                    'prefix'    : prefix,
                    'path'      : path,
                    'name'      : name
                    }

                print "-i- Requesting: %(req)s" % {
                    'req': request
                    }

                bn = os.path.basename(i)

                os.system("wget -O '%(bn)s' '%(url)s'" % {
                        'bn': bn,
                        'url': request
                        })

    return ret



def search(config, wsp):

    ret = 0

    lst = client(config, wsp)

    if isinstance(lst, list):
        lst.sort(version.version_comparator)

        for i in lst:
            print i

        print "count: %(n)s" % {
            'n': len(lst)
            }

    else:
        print "-e- Error getting response list"
        ret = lst

    return ret

def client(config, wsp={}):

    for i in wsp:
        exec("%(i)s = wsp['%(i)s']" % {
                'i': i
                })

    ret = 0

    if not what in ['info', 'source', 'repository'] \
            or not how in ['regexp', 'begins', 'exac', 'contains'] \
            or not isinstance(sensitive, bool) \
            or not isinstance(value, basestring):
        print "-e- Wrong parameters"
        ret = 1

    else:

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
            'value'     : urllib.quote(unicode(value))
            }

        print "-i- Requesting: %(req)s" % {
            'req': request
            }

        try:
            req_res = urllib.urlopen(request)
        except IOError:
            print "-e- Connection refused"
        except:
            e = sys.exc_info()
            utils.print_exception_info(e)
        else:
            code = req_res.getcode()
            if code != 200:
                print "-e- Response code: %(n)d" % {
                    'n': code
                    }
            else:
                lst = req_res.readlines()
                lst2 = []
                for i in lst:
                    s = i.strip()
                    if s != '':
                        lst2.append(s)
                ret = lst2

    return ret
