import urllib

def print_help():
    print """\
aipsetup client command

   search p|r|e|i|c|s r|l s|r|i NAME

      List source packages containing on remote or local UHT server

      First parameter:

      p - NAME is prefix
      r - NAME is regular expression
      e - NAME is exact name
      i - assume NAME tobe package info name and get re for it
      c - NAME is package name substring
      s - NAME is case sensitive

      Second parameter:

      'r' or 'l' - is for remote or local access

      Third parameter:
      's', 'r' or 'i' - is for source, repository or info access

   get [-p] [-r] [-e] [-c] [-s] [-d[=DIRNAME]]
       [-u[=(T|YES|TRUE|ON)|(F|NO|FALSE|OFF)]] r|l s|r|i NAME

      Get files from remote UHT server

      -p - same as in `search'
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

            if len(args) != 4:
                print "-e- must be axactly 4 parameters"

            else:

                where = args[1]
                what = args[2]
                value = args[3]
                how = 'byinfo'

                search(config,)

        else:
            print "-e- wrong command"
            ret = 1

    return ret


def client(config, what='repository', how='begins',
           sensitive=True, value=''):

    ret = 0

    if not what in ['info', 'source', 'repository'] \
            or not how in ['regexp', 'begins', 'exac', 'contains'] \
            or not isinstance(sensitive, bool) \
            or not isinstance(value, basestring):
        ret = 1

    else:

        semi = ''
        if port != None and port != '':
            semi = ':'

        sens = ''
        if sensitive:
            sens = '&sensitive=on'

        request = ("%(proto)s://%(host)s%(semi)s%(port)s%(path)search?"\
                       + "what=%(what)s&how=%(how)s&"\
                       + "view=list%(sensitive)s&"\
                       + "value=%(value)s") % {
            'proto'     : config['client_proto'],
            'host'      : config['client_host'],
            'semi'      : semi,
            'port'      : str(port),
            'path'      : config['client_prefix'],
            'sensitive' : sens,
            'value'     : urllib.quote(unicode(value))
            }

        print request

    return ret

def search(config, what='repository', how='begins',
           sensitive=True, value=''):

    client(config, what, how, sensitive, value)
