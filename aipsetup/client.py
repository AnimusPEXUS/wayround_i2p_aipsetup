import urllib
import sys


import pkgindex
import utils


def print_help():
    print """\
aipsetup client command

   search [-s] [-h=b|r|e|i|c] [-w=r|l] [-a=s|r|i] [NAME]

      List source packages containing on remote or local UHT server

      -s - NAME is case sensitive

      -h values:

      b - package name begins with NAME
      r - NAME is regular expression
      e - NAME is exact name
      i - assume NAME tobe package info name and get RE for it
      c - NAME is package name substring

      -w values: 'r' or 'l' - is for remote or local access

      -a values: 's', 'r' or 'i' - is for source, repository or info
                 access


   get [-p] [-r] [-e] [-c] [-s] [-d[=DIRNAME]]
       [-u[=(T|YES|TRUE|ON)|(F|NO|FALSE|OFF)]] r|l s|r|i NAME

      Get files from remote UHT server

      -b - same as in `search'
      -r - ...
      -e - ...
      -c - ...
      -s - ...

      -u - Place requested files into local UHT server
      -d - Place requested files in pointed (by default current)
           directory

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

        elif args[0] == 'search':

            if len(args) != 2:
                print "-e- must be axactly 1 parameter"

            else:

                p_errors = False

                how = 'i'

                for i in opts:
                    if i[0] == '-h':
                        how = i[1]

                where = 'r'

                for i in opts:
                    if i[0] == '-w':
                        where = i[1]

                what = 'r'

                for i in opts:
                    if i[0] == '-a':
                        what = i[1]


                sensitive = False

                for i in opts:
                    if i[0] == '-s':
                        sensitive = True


                if not how in 'breic':
                    p_errors = True

                if not where in 'rl':
                    p_errors = True

                if not what in 'sri':
                    p_errors = True

                value = args[1]


                name_errs = False
                if how == 'i':
                    r = pkgindex.PackageDatabase(config)
                    idic = r.package_info_record_to_dict(name=value)
                    del(r)

                    if idic == None:
                        print "-e- Can't find info for %(name)s" % {
                            'name': value
                            }
                        name_errs = True
                    else:
                        print "-i- Using regexp `%(re)s' from `%(name)s' pkg info" % {
                            're': idic['regexp'],
                            'name': value
                            }

                        value = idic['regexp']
                        how = 'r'

                if not name_errs:

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

                    result = search(config, what=what, how=how,
                                    where=where, sensitive=sensitive,
                                    value=value
                                    )



        else:
            print "-e- wrong command"
            ret = 1

    return ret


def search(config, what='repository', how='begins', where='remote',
           sensitive=True, value=''):

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

        request = ("%(proto)s://%(host)s%(semi)s%(port)s%(path)ssearch?"\
                       + "what=%(what)s&how=%(how)s&"\
                       + "view=list%(sensitive)s&"\
                       + "value=%(value)s") % {
            'proto'     : proto,
            'host'      : host,
            'semi'      : semi,
            'port'      : port,
            'path'      : prefix,
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
                print req_res.read()

    return ret
