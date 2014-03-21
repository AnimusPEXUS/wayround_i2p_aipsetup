
import collections
import os.path

import org.wayround.aipsetup.client_pkg
import org.wayround.aipsetup.info
import org.wayround.utils.text


def commands():
    return collections.OrderedDict([
        ('pkg_client', collections.OrderedDict([
            ('list', list_),
            ('list_cat', list_cat),
            ('ls', ls),
            ('print', print_info),
            ('asp_list', asp_list),
            ('get', get_asp),
            ('get_lat', get_asp_latest),
            ('get_lat_cat', get_asp_lat_cat)
            ])),
        ('pkg_client_tar', collections.OrderedDict([
            ('list', tar_list),
            ('get_lat', get_tar_latest),
            ('get_lat_cat', get_tar_lat_cat)
            ]))
        ])


def list_(command_name, opts, args, adds):

    """
    List package names known to server

    [options] name

    options:
        --searchmode=NAME    must be 'filemask' or 'regexp'
        -n                   non case sensitive
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        searchmode = 'filemask'
        if '--searchmode=' in opts:
            searchmode = opts['--searchmode=']

        cs = True
        if '-n' in opts:
            cs = False

        res = org.wayround.aipsetup.client_pkg.list_(
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


def list_cat(command_name, opts, args, adds):

    """
    List all packages in category and sub categories
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        path = args[0]

        for path, cats, packs in org.wayround.aipsetup.client_pkg.walk(
            url,
            path
            ):

            print("{}:".format(path))
            catsn = []
            for i in cats:
                catsn.append('{}/'.format(i))
            packsn = []
            for i in packs:
                packsn.append('{}'.format(i))

            text = org.wayround.utils.text.return_columned_list(
                catsn
                )
            del catsn
            print(text)
            text = org.wayround.utils.text.return_columned_list(
                packsn
                )
            print(text)

        ret = 0

    return ret


def ls(command_name, opts, args, adds):

    """
    Print List of packages and categories in named category path

    arguments: path
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        path = args[0]

        while path.startswith('/'):
            path = path[1:]

        while path.endswith('/'):
            path = path[:-1]

        url = config['pkg_client']['server_url']

        res = org.wayround.aipsetup.client_pkg.ls(
            url, path
            )

        if res == None:
            ret = 2

        else:

            cats = org.wayround.utils.text.return_columned_list(
                res['categories']
                )
            packs = org.wayround.utils.text.return_columned_list(
                res['packages']
                )

            print(
                """
Categories ({} items):
{}

Packages ({} items):
{}
""".format(
                    len(res['categories']),
                    cats,
                    len(res['packages']),
                    packs
                    )
                )

            ret = 0

    return ret


def print_info(command_name, opts, args, adds):

    """
    Get and print package information

    attributes: package_name
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        res = org.wayround.aipsetup.client_pkg.info(url, args[0])

        if res == None:
            ret = 2
        else:

            text = ''

            for i in org.wayround.aipsetup.info.\
                SAMPLE_PACKAGE_INFO_STRUCTURE_TITLES.keys():

                if i in res:

                    text += "    | {}: {}\n".format(
                        org.wayround.aipsetup.info.\
                            SAMPLE_PACKAGE_INFO_STRUCTURE_TITLES[i],
                        res[i]
                        )

            print("Info on package `{}':\n{}".format(args[0], text))

            ret = 0

    return ret


def asp_list(command_name, opts, args, adds):

    """
    Get and print list of package asps on server

    attributes: package_name
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        res = org.wayround.aipsetup.client_pkg.asps(url, args[0])

        if res == None:
            ret = 2
        else:

            bases = org.wayround.utils.path.bases(res)

            text = org.wayround.utils.text.return_columned_list(
                bases
                )

            print("Package `{}' asps:\n{}".format(args[0], text))

            ret = 0

    return ret


def get_asp(command_name, opts, args, adds):

    """
    Download asp file from package server

    attributes: file_base_name
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        name = args[0]

        ret = org.wayround.aipsetup.client_pkg.asps(url, name)

    return ret


def get_asp_latest(command_name, opts, args, adds):

    """
    Download latest asp file from package server

    attributes: file_base_name
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        name = args[0]

        res = org.wayround.aipsetup.client_pkg.get_latest_asp(url, name)

        if isinstance(res, str):
            ret = 0
        else:
            ret = 1

    return ret


def get_asp_lat_cat(command_name, opts, args, adds):

    """
    Download all latest asps in category and subcategories

    -d out_dir
    -o           include deprecated
    -n           include non-installable
    """

    config = adds['config']
    out_dir = ''
    if '-d' in opts:
        out_dir = opts['-d']

    deprecated = '-o' in opts
    non_installable = '-n' in opts

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        path = args[0]

        res = org.wayround.aipsetup.client_pkg.get_recurcive_package_list(
            url,
            path
            )

        if res == None:
            ret = 2
        else:

            errors = False

            res.sort()

            for i in res:

                info = org.wayround.aipsetup.client_pkg.info(url, i)

                can_continue = False
                if info['deprecated'] and not deprecated:
                    f = open('!deprecated.txt', 'a')
                    f.write(
                        "Package `{}' is deprecated\n".format(i)
                        )
                    f.close()
                elif info['non_installable'] and not non_installable:
                    f = open('!non_installable.txt', 'a')
                    f.write(
                        "Package `{}' is non-installable\n".format(i)
                        )
                    f.close()
                else:
                    can_continue = True

                if can_continue:

                    res2 = org.wayround.aipsetup.client_pkg.get_latest_asp(
                        url,
                        i,
                        out_dir,
                        False
                        )
                    if res2 == None:
                        errors = True
                        f = open('!errors.txt', 'a')
                        f.write(
                            "Can't get latest asp for package `{}'\n".format(i)
                            )
                        f.close()

            ret = int(not errors)

    return ret


def tar_list(command_name, opts, args, adds):

    """
    List all tarballs for named package
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        res = org.wayround.aipsetup.client_pkg.tarballs(url, args[0])

        if res == None:
            ret = 2
        else:

            bases = org.wayround.utils.path.bases(res)

            text = org.wayround.utils.text.return_columned_list(
                bases
                )

            print("Package `{}' tarballs:\n{}".format(args[0], text))

            ret = 0

    return ret


def get_tar_latest(command_name, opts, args, adds):

    """
    Dwonload latest tarball for named package
    """

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        name = args[0]

        ret = _get_tarballs_latest(url, name, config)

    return ret


def _get_tarballs_latest(url, name, config, out_dir=None):

    ret = 1

    res = org.wayround.aipsetup.client_pkg.tarballs_latest(url, name)

    if res != None and len(res) != 0:

        exts = \
            config['pkg_client']['acceptable_src_file_extensions'].\
                split(' ')

        found = None
        for i in exts:
            for j in res:
                if j.endswith(i):
                    found = j
                    break
            if found != None:
                break

        if found:
            res = found

        res = org.wayround.aipsetup.client_pkg.get_tarball(
            res,
            out_dir=out_dir
            )

        if isinstance(res, str):
            ret = 0
        else:
            ret = 1

    return ret


def get_tar_lat_cat(command_name, opts, args, adds):

    """
    Download all latest tarballs in category and subcategories

    -d out_dir
    -o           include deprecated
    -n           include non-installable
    """

    config = adds['config']
    out_dir = ''
    if '-d' in opts:
        out_dir = opts['-d']

    deprecated = '-o' in opts
    non_installable = '-n' in opts

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        path = args[0]

        res = org.wayround.aipsetup.client_pkg.get_recurcive_package_list(
            url,
            path
            )

        if res == None:
            ret = 2
        else:

            errors = False

            res.sort()

            for i in res:

                info = org.wayround.aipsetup.client_pkg.info(url, i)

                can_continue = False
                if info['deprecated'] and not deprecated:
                    f = open('!deprecated.txt', 'a')
                    f.write(
                        "Package `{}' is deprecated\n".format(i)
                        )
                    f.close()
                    errors = True
                elif info['non_installable'] and not non_installable:
                    f = open('!non_installable.txt', 'a')
                    f.write(
                        "Package `{}' is non-installable\n".format(i)
                        )
                    f.close()
                    errors = True
                else:
                    can_continue = True

                if can_continue:

                    res = _get_tarballs_latest(url, i, config, out_dir=out_dir)

                    if res != 0:
                        errors = True

            ret = int(not errors)

    return ret
