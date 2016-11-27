
import collections
import logging

import wayround_org.utils.path
import wayround_org.utils.text

import wayround_org.aipsetup.host_arch_params


def commands():
    return collections.OrderedDict([
        ('pkg-client', collections.OrderedDict([
            ('search', list_),
            ('list-cat', list_cat),
            ('ls', ls),
            ('print', print_info),
            ('asp-list', asp_list),
            ('snapshot-list', snapshot_list),
            ('get', get_asp),
            ('get-lat', get_asp_latest),
            ('get-lat-cat', get_asp_lat_cat),
            ('get-by-list', get_asp_by_list),
            ('get-by-snap', get_by_snapshot),
            ])),
        ('pkg-client-src', collections.OrderedDict([
            ('search', tar_list),
            ('get-lat', get_tar_latest),
            ('get-lat-cat', get_tar_lat_cat),
            ('get-by-list', get_tar_by_list),
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

    import wayround_org.aipsetup.client_pkg
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

        res = wayround_org.aipsetup.client_pkg.list_(
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


def list_cat(command_name, opts, args, adds):
    """
    List all packages in category and sub categories
    """

    import wayround_org.aipsetup.client_pkg
    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        path = args[0]

        for path, cats, packs in wayround_org.aipsetup.client_pkg.walk(
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

            text = wayround_org.utils.text.return_columned_list(
                catsn
                )
            del catsn
            print(text)
            text = wayround_org.utils.text.return_columned_list(
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

    import wayround_org.aipsetup.client_pkg

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

        res = wayround_org.aipsetup.client_pkg.ls(
            url, path
            )

        if res is None:
            ret = 2

        else:

            cats = wayround_org.utils.text.return_columned_list(
                res['categories']
                )
            packs = wayround_org.utils.text.return_columned_list(
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

    import wayround_org.aipsetup.info
    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        res = wayround_org.aipsetup.client_pkg.info(url, args[0])

        if res is None:
            ret = 2
        else:

            text = ''

            for i in wayround_org.aipsetup.info.\
                    SAMPLE_PACKAGE_INFO_STRUCTURE_TITLES.keys():

                if i in res:

                    text += "    | {}: {}\n".format(
                        wayround_org.aipsetup.info.
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

    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        res = wayround_org.aipsetup.client_pkg.asps(url, args[0])

        if res is None:
            ret = 2
        else:

            bases = wayround_org.utils.path.bases(res)

            text = wayround_org.utils.text.return_columned_list(
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

    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        name = args[0]

        ret = wayround_org.aipsetup.client_pkg.asps(url, name)

    return ret


def get_asp_latest(command_name, opts, args, adds):
    """
    Download latest asp file from package server

    attributes: file_base_name
    """

    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    host, arch = \
        wayround_org.aipsetup.host_arch_params.process_h_and_a_opts_strict(
            opts,
            config
            )

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        name = args[0]

        res = wayround_org.aipsetup.client_pkg.get_latest_asp(
            url,
            name,
            host,
            arch
            )

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

    import wayround_org.aipsetup.client_pkg

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

        res = wayround_org.aipsetup.client_pkg.get_recurcive_package_list(
            url,
            path
            )

        if res is None:
            ret = 2
        else:

            errors = False

            res.sort()

            for i in res:

                info = wayround_org.aipsetup.client_pkg.info(url, i)

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

                    res2 = wayround_org.aipsetup.client_pkg.get_latest_asp(
                        url,
                        i,
                        out_dir,
                        False
                        )
                    if res2 is None:
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

    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    ret = 1

    if not len(args) == 1:
        print("Must be one argument")

    else:

        url = config['pkg_client']['server_url']

        res = wayround_org.aipsetup.client_pkg.tarballs(url, args[0])

        if res is None:
            ret = 2
        else:

            bases = wayround_org.utils.path.bases(res)

            text = wayround_org.utils.text.return_columned_list(
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

        ret = _get_tarballs_latest(url, name, config, mute=False)

    return ret


def _get_tarballs_latest(url, name, config, out_dir=None, mute=True):

    import wayround_org.aipsetup.client_pkg

    ret = 1

    exts = config['pkg_client']['acceptable_src_file_extensions'].split()

    res = wayround_org.aipsetup.client_pkg.tarballs_latest(
        url, name, exts
        )

    if res is not None and len(res) != 0:

        res = wayround_org.utils.path.select_by_prefered_extension(res, exts)

        res = wayround_org.aipsetup.client_pkg.get_tarball(
            res,
            out_dir=out_dir,
            mute_downloader=mute
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
    import wayround_org.aipsetup.client_pkg

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

        res = wayround_org.aipsetup.client_pkg.get_recurcive_package_list(
            url,
            path
            )

        if res is None:
            ret = 2
        else:

            errors = False

            res.sort()

            for i in res:

                logging.info("Getting tarball for `{}'".format(i))

                info = wayround_org.aipsetup.client_pkg.info(url, i)

                can_continue = False
                if info['deprecated'] and not deprecated:
                    f = open('!deprecated.txt', 'a')
                    f.write(
                        "{}\n".format(i)
                        )
                    f.close()
                    errors = True
                elif info['non_installable'] and not non_installable:
                    f = open('!non_installable.txt', 'a')
                    f.write(
                        "{}\n".format(i)
                        )
                    f.close()
                    errors = True
                else:
                    can_continue = True

                if can_continue:

                    res = _get_tarballs_latest(url, i, config, out_dir=out_dir)

                    if res != 0:
                        f = open('!can not get.txt', 'a')
                        f.write(
                            "{}\n".format(i)
                            )
                        f.close()
                        errors = True

            ret = int(errors)

    return ret


def get_x_by_list(command_name, opts, args, adds, mode='tar'):
    """
    Gets tarball or asp by criteries

    listname [selected_item [selected_item [selected_item [selected_item ...]]]]

    -v=VERSION
    """

    import wayround_org.aipsetup.get_list_procs
    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 1

    host, arch = \
        wayround_org.aipsetup.host_arch_params.process_h_and_a_opts_strict(
            opts,
            config
            )

    list_name = None
    if len(args) > 0:
        list_name = args[0]

    version = None
    if '-v' in opts:
        version = opts['-v']

    if list_name is None:
        logging.error("list name is required parameter")
        ret = 1
    else:

        logging.info("Loading list `{}'".format(list_name))

        conf = wayround_org.aipsetup.get_list_procs.get_list(config, list_name)

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(config)
        src_client = \
            wayround_org.aipsetup.controllers.src_client_by_config(config)

        acceptable_extensions_order_list = []
        if mode == 'tar':
            acceptable_extensions_order_list = \
                config['pkg_client']['acceptable_src_file_extensions'].split()

        ret = wayround_org.aipsetup.get_list_procs.get_by_glp(
            mode,
            conf,
            version,
            pkg_client,
            src_client,
            acceptable_extensions_order_list,
            host=host,
            arch=arch
            )

    return ret


def get_asp_by_list(*args, **kwargs):
    return get_x_by_list(*args, mode='asp', **kwargs)

get_asp_by_list.__doc__ = get_x_by_list.__doc__


def get_tar_by_list(*args, **kwargs):
    return get_x_by_list(*args, mode='tar', **kwargs)

get_tar_by_list.__doc__ = get_x_by_list.__doc__


def snapshot_list(command_name, opts, args, adds):

    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    url = config['pkg_client']['server_url']

    res = wayround_org.aipsetup.client_pkg.snapshot_list(url)

    if res is None:
        ret = 2
    else:

        bases = wayround_org.utils.path.bases(res)

        bases.sort(reverse=True)

        text = wayround_org.utils.text.return_columned_list(
            bases
            )

        print(text)

        ret = 0

    return ret


def snapshot_get(command_name, opts, args, adds):

    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    url = config['pkg_client']['server_url']

    res = wayround_org.aipsetup.client_pkg.snapshot_get(url, name)

    if res is None:
        ret = 2
    else:

        ret = 0

    return ret


def get_by_snapshot(command_name, opts, args, adds):

    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    url = config['pkg_client']['server_url']

    name = None

    ret = 1

    if len(args) != 1:
        logging.error("Must be one arg")
        ret = 1
    else:

        name = args[0]

        res = wayround_org.aipsetup.client_pkg.snapshot_get(url, name)

        if res is None:
            ret = 2
        else:

            errors = False

            for i in res['asps']:
                asp_obj = wayround_org.aipsetup.package.ASPackage(i)
                if not isinstance(
                        wayround_org.aipsetup.client_pkg.get_asp(
                            url,
                            asp_obj.host,
                            asp_obj.arch,
                            i + '.asp'
                            ),
                        str
                        ):
                    errors = True

                    f = open('!errors!.txt', 'a')
                    f.write("Can't get asp package: {}\n".format(i))
                    f.close()

            if errors:
                ret = 3

    return ret
