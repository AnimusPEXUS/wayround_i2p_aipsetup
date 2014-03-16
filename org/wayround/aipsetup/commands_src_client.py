
import collections

import org.wayround.aipsetup.client_src
import org.wayround.utils.text


def commands():
    return collections.OrderedDict([
        ('src_client', collections.OrderedDict([
            ('list', list_),
            ('files', files),
            ('get', get)
            ])
            )
        ])


def list_(command_name, opts, args, adds):

    """
    List tarball names known to server

    [options] name

    options:
        --searchmode=NAME    must be 'filemask' or 'regexp'
        -n                   non case sensitive
        -d
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['src_client']['server_url']

        searchmode = 'filemask'
        if '--searchmode=' in opts:
            searchmode = opts['--searchmode=']

        cs = True
        if '-n' in opts:
            cs = False

        res = org.wayround.aipsetup.client_src.list_(
            url,
            args[0],
            searchmode,
            cs
            )

        columned_list = org.wayround.utils.text.return_columned_list(res)
        c = len(res)
        print(
            "Result ({} items):\n{}Result ({} items)".format(
                c, columned_list, c
                )
            )

        ret = 0

    return ret


def files(command_name, opts, args, adds):

    """
    List tarballs of pointed names

    [options] name
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['src_client']['server_url']

        res = org.wayround.aipsetup.client_src.files(
            url,
            args[0]
            )

        columned_list = org.wayround.utils.text.return_columned_list(res)
        c = len(res)
        print(
            "Result ({} items):\n{}Result ({} items)".format(
                c, columned_list, c
                )
            )

        ret = 0

    return ret


def get(command_name, opts, args, adds):

    """
    List tarballs of pointed names

    [options] name
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['src_client']['server_url']

        res = org.wayround.aipsetup.client_src.get(
            url,
            args[0]
            )

        print("Result code {}".format(res))

        ret = res

    return ret
