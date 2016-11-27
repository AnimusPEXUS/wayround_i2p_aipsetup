
import collections


import wayround_org.utils.path
import wayround_org.utils.text


def commands():
    return collections.OrderedDict([
        ('src-client', collections.OrderedDict([
            ('search', search),
            ('files', files),
            ('get', get)
            ]))
        ])


def search(command_name, opts, args, adds):
    """
    Search tarball names known to server

    [options] name

    options:
        --searchmode=NAME    must be 'filemask' or 'regexp'
        -n                   non case sensitive
        -p=NAME              reduce search to package name paths
    """

    import wayround_org.aipsetup.client_src

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

        res = wayround_org.aipsetup.client_src.search(
            url,
            args[0],
            searchmode,
            cs
            )

        columned_list = wayround_org.utils.text.return_columned_list(res)
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

    import wayround_org.aipsetup.client_src

    config = adds['config']

    ret = 1

    if len(args) not in range(1, 3):
        print("Must be one argument one or two")

    else:

        url = config['src_client']['server_url']

        name = args[0]

        res = wayround_org.aipsetup.client_src.files(
            url,
            name,
            []
            )

        if res is None:
            ret = 1
            print("No result")
        else:
            columned_list = wayround_org.utils.text.return_columned_list(res)
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
    Get tarball

    This command internally uses wget to download named file to current
    directory
    """

    import wayround_org.aipsetup.client_src

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['src_client']['server_url']

        res = wayround_org.aipsetup.client_src.get(
            url,
            args[0]
            )

        print("Result code {}".format(res))

        ret = res

    return ret
