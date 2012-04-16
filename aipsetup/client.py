import urllib
import sys


import pkgindex
import utils


def print_help():
    print """\
aipsetup client command

   search [-i] [--how=b|r|e|i|c] [--where=r|l] [--what=s|r|i]
          [--ver=[ANY|MAX|MIN|ver]] [--ver-limit=VER] [NAME]

      Search contents of remote or local UHT server

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

      --ver   values:

          MIN - filter minimal version


   get [-o[=DIRNAME]] [-s] [-h=b|r|e|i|c] [-w=r|l] [-a=s|r|i] [NAME]

      Get files from remote or local UHT server

      All options and parameters same as in search, plus -d option

      -o - Place requested files in pointed (by default current)
           directory

"""

def workout_search_params(opts, args, config):

    what = ''
    how = ''
    where = ''
    sensitive = ''
    value = ''
    n_errors = False
    p_errors = False

    if len(args) != 2:
        print "-e- must be axactly 1 parameter"
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
            if i[0] == '--ver':
                ver = i[1]


        ver_limit = None

        for i in opts:
            if i[0] == '--ver-limit':
                ver_limit = i[1]


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

        if not ver in ['ANY', 'MAX', 'MIN']:
            print "-e- `ver' error"
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
                        regexp = idic['regexp']
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
        ver_limit = ver_limit,
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

            if not p_errors and not n_errors:

                result = search(config,
                                wsp['what'],
                                wsp['how'],
                                wsp['where'],
                                wsp['sensitive'],
                                wsp['ver'],
                                wsp['ver_limit'],
                                wsp['value']
                                )

        elif args[0] == 'get':

            wsp = workout_search_params(opts, args, config)

            output = None

            for i in opts:
                if i[0] == '-o':
                    output = i[1]


            if not p_errors and not n_errors:

                result = get(config,
                             output,
                             wsp['what'],
                             wsp['how'],
                             wsp['where'],
                             wsp['sensitive'],
                             wsp['ver'],
                             wsp['ver_limit'],
                             wsp['value']
                             )


        else:
            print "-e- wrong command"
            ret = 1

    return ret


def get(config, output=None, what='repository', how='begins',
        where='remote', sensitive=True, value=''):

    ret = 0

    lst = client(config, what, how, where, sensitive, value)

    if not isinstance(lst, list):
        ret = lst

    else:

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

            # name = urllib.quote(name)


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


def search(config, what='repository', how='begins', where='remote',
           sensitive=True, ver='ANY', ver_limit=None, value=''):

    lst = client(config, what, how, where,  sensitive, value)

    for i in lst:
        print i

    print "count: %(n)s" % {
        'n': len(lst)
        }

def client(config, what='repository', how='begins', where='remote',
           sensitive=True, ver='ANY', ver_limit=None, value=''):

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
            print "-e- Connection Refused"
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
