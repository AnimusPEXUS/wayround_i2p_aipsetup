
import functools
import json
import logging
import os.path
import re

import org.wayround.aipsetup.client_pkg
import org.wayround.aipsetup.client_src
import org.wayround.utils.path
import org.wayround.utils.tarball_name_parser
import org.wayround.utils.terminal
import org.wayround.utils.types
import org.wayround.utils.version


def check_nineties(parsed):

    parsed_groups_version_list = parsed['groups']['version_list']

    ret = False

    if len(parsed_groups_version_list) > 2:
        ret = re.match(
            r'^9\d+$',
            parsed_groups_version_list[1]
            ) != None

    return ret


def check_development(parsed):

    parsed_groups_version_list = parsed['groups']['version_list']

    ret = re.match(
        r'^\d*[13579]$',
        parsed_groups_version_list[1]
        ) != None

    return ret


def find_gnome_tarball_name(
    pkg_client,
    pkgname,
    required_v1=None,
    required_v2=None,
    find_lower_version_if_required_missing=True,
    development_are_acceptable=True,
    nineties_minors_are_acceptable=True,
    acceptable_extensions_order_list=None
    ):

    if acceptable_extensions_order_list == None:
        acceptable_extensions_order_list = ['.tar.xz', '.tar.bz2', '.tar.gz']

    def source_version_comparator(v1, v2):
        return org.wayround.utils.version.source_version_comparator(
            v1, v2,
            acceptable_extensions_order_list
            )

    tarballs = pkg_client.tarballs(pkgname)

    if tarballs == None:
        tarballs = []

    tarballs.sort(
        reverse=True,
        key=functools.cmp_to_key(
            source_version_comparator
            )
        )

    found_required_targeted_tarballs = []

    if (required_v1 == None or required_v2 == None) and len(tarballs) != 0:

        for i in tarballs:

            parsed = org.wayround.utils.tarball_name_parser.\
                parse_tarball_name(i, mute=True)

            parsed_groups_version_list = parsed['groups']['version_list']

            is_nineties = check_nineties(parsed)

            is_development = check_development(parsed)

            int_parsed_groups_version_list_1 = \
                int(parsed_groups_version_list[1])

            if (
                (is_nineties
                 and nineties_minors_are_acceptable == True
                 )
                or (is_development
                    and development_are_acceptable == True
                    )
                or (not is_nineties
                    and not is_development
                    )
                ):

                if required_v1 == None:
                    required_v1 = int(parsed['groups']['version_list'][0])

                if required_v2 == None:
                    required_v2 = int_parsed_groups_version_list_1

                break

    for i in tarballs:

        parsed = org.wayround.utils.tarball_name_parser.\
            parse_tarball_name(i, mute=True)

        if parsed:

            parsed_groups_version_list = parsed['groups']['version_list']
            if (int(parsed_groups_version_list[0]) == required_v1
                and
                int(parsed_groups_version_list[1]) == required_v2
                ):

                is_nineties = check_nineties(parsed)

                if ((is_nineties and nineties_minors_are_acceptable)
                    or
                    (not is_nineties)):

                    found_required_targeted_tarballs.append(i)

    if (len(found_required_targeted_tarballs) == 0
        and find_lower_version_if_required_missing == True):

        next_found_acceptable_tarball = None

        for i in tarballs:

            parsed = org.wayround.utils.tarball_name_parser.\
                parse_tarball_name(i, mute=True)

            if parsed:

                parsed_groups_version_list = \
                    parsed['groups']['version_list']

                int_parsed_groups_version_list_1 = \
                    int(parsed_groups_version_list[1])

                if int_parsed_groups_version_list_1 >= required_v2:
                    continue

                is_nineties = check_nineties(parsed)

                is_development = check_development(parsed)

                if next_found_acceptable_tarball == None:

                    if (is_nineties
                        and nineties_minors_are_acceptable == True
                        and int_parsed_groups_version_list_1 < required_v2
                        ):
                        next_found_acceptable_tarball = i

                    if (next_found_acceptable_tarball == None
                        and is_development
                        and development_are_acceptable == True
                        and int_parsed_groups_version_list_1 < required_v2
                        ):
                        next_found_acceptable_tarball = i

                    if (next_found_acceptable_tarball == None
                        and not is_nineties
                        and not is_development
                        and int_parsed_groups_version_list_1 < required_v2
                        ):
                        next_found_acceptable_tarball = i

                if next_found_acceptable_tarball != None:
                    break

        if next_found_acceptable_tarball != None:

            for i in tarballs:
                if org.wayround.utils.version.\
                    source_version_comparator(
                        i,
                        next_found_acceptable_tarball,
                        acceptable_extensions_order_list
                        ) == 0:
                    found_required_targeted_tarballs.append(i)

    ret = None
    for i in acceptable_extensions_order_list:
        for j in found_required_targeted_tarballs:
            if j.endswith(i):
                ret = j
                break

    if ret == None and len(found_required_targeted_tarballs) != 0:
        ret = found_required_targeted_tarballs[0]

    return ret


def gnome_get(
    mode,
    pkg_client, src_client, acceptable_extensions_order_list,
    pkgname, version,
    args, kwargs
    ):

    """
    """

    ret = None

    if not mode in ['tar', 'asp']:
        raise ValueError("`mode' must be in ['tar', 'asp']")

    if mode == 'tar':

        if 'version' in kwargs:
            listed_version = kwargs['version']

            if not '{asked_version}' in listed_version:
                version = listed_version
            else:
                version = listed_version.format(asked_version=version)

        version_numbers = version.split('.')

        for i in range(len(version_numbers)):
            version_numbers[i] = int(version_numbers[i])

        kwargs = {}

        if 'nmaa' in kwargs:
            kwargs['nineties_minors_are_acceptable'] = kwargs['nmaa']

        if 'daa' in kwargs:
            kwargs['development_are_acceptable'] = kwargs['daa']

        if 'flvirm' in kwargs:
            kwargs['find_lower_version_if_required_missing'] = kwargs['flvirm']

        tarball = find_gnome_tarball_name(
            pkg_client,
            pkgname,
            required_v1=version_numbers[0],
            required_v2=version_numbers[1],
            acceptable_extensions_order_list=acceptable_extensions_order_list,
            **kwargs
            )

        if tarball == None:
            ret = 2
        else:

            if not isinstance(
                org.wayround.aipsetup.client_pkg.get_tarball(tarball),
                str
                ):
                ret = 3

    elif mode == 'asp':
        ret = normal_get(
            mode,
            pkg_client, src_client, acceptable_extensions_order_list,
            pkgname, version,
            args, kwargs
            )

    return ret


def normal_get(
    mode,
    pkg_client, src_client,
    acceptable_extensions_order_list,
    pkgname, version,
    args, kwargs
    ):

    """
    Download tarball or complete ASP package


    """

    if not mode in ['tar', 'asp']:
        raise ValueError("`mode' must be in ['tar', 'asp']")

    ret = 0

    if mode == 'tar':

        res = pkg_client.tarballs_latest(pkgname)
        if isinstance(res, list) and len(res) != 0:
            found = None
            for j in acceptable_extensions_order_list:
                for k in res:
                    if k.endswith(j):
                        found = k
                        break
                if found != None:
                    break
            if found == None:
                found = res[0]

            if not isinstance(
                org.wayround.aipsetup.client_pkg.get_tarball(found),
                str
                ):
                ret = 3
        else:
            ret = 2

    elif mode == 'asp':

        if not isinstance(pkg_client.get_latest_asp(pkgname), str):
            ret = 1

    return ret


def get_by_glp(
    mode,
    conf,
    version,
    pkg_client, src_client,
    acceptable_extensions_order_list
    ):

    if not mode in ['tar', 'asp']:
        raise ValueError("`mode' must be in ['tar', 'asp']")

    if not isinstance(
        pkg_client,
        org.wayround.aipsetup.client_pkg.PackageServerClient
        ):
        raise TypeError(
            "`pkg_client' must be inst of "
            "org.wayround.aipsetup.client_pkg.PackageServerClient"
            )

    if not isinstance(
        src_client,
        org.wayround.aipsetup.client_src.SourceServerClient
        ):
        raise TypeError(
            "`pkg_client' must be inst of "
            "org.wayround.aipsetup.client_src.SourceServerClient"
            )

    ret = 0

    if ('ask_version' in conf
        and conf['ask_version'] == True
        and version == None):

        logging.error("Version is required")

        ret = 1
    else:
        errors = 0

        complex_ = isinstance(conf['names'], dict)

        for i in sorted(conf['names']):

            proc = normal_get

            args = []
            kwargs = {}

            if complex_:
                data = conf['names'][i]

                if data['proc'] == 'normal_get':
                    proc = normal_get

                if data['proc'] == 'gnome_get':
                    proc = gnome_get

            if not isinstance(
                proc(
                    mode,
                    pkg_client, src_client, acceptable_extensions_order_list,
                    i,
                    version=version,
                    args=args,
                    kwargs=kwargs
                    ),
                str
                ):

                errors += 1
                f = open('!errors!.txt', 'a')
                f.write("Can't get file for: {}\n".format(i))
                f.close()

        ret = int(errors > 0)

    return ret


def get_list(config, list_name):

    # TODO: place next to config

    list_filename = org.wayround.utils.path.abspath(
        org.wayround.utils.path.join(
            os.path.dirname(__file__),
            'distro',
            'pkg_groups',
            "{}.gpl".format(list_name)
            )
        )

    f = open(list_filename)
    conf = json.loads(f.read())
    f.close()

    return conf
