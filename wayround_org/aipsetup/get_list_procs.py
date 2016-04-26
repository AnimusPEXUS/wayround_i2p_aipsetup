
import functools
import json
import logging
import os.path
import re
import pprint

import wayround_org.aipsetup.client_pkg
import wayround_org.aipsetup.client_src
import wayround_org.utils.path
import wayround_org.utils.tarball
import wayround_org.utils.terminal
import wayround_org.utils.types
import wayround_org.utils.version


def check_nineties(parsed):

    ret = False

    vl = parsed['groups']['version_list']

    vl_l = len(vl)

    if vl_l > 1:

        for i in range(1, vl_l):

            res = re.match(r'^9\d+$', vl[i]) is not None

            if res:
                ret = True
                break

    # print("9x? : {} ? {}".format(vl, ret))

    return ret


def check_development(parsed):

    ret = re.match(
        r'^\d*[13579]$',
        parsed['groups']['version_list'][1]
        ) is not None

    return ret


def find_gnome_tarball_name(
        pkg_client,
        pkgname,
        required_v1=None,
        required_v2=None,
        find_lower_version_if_required_missing=True,
        development_are_acceptable=False,
        nineties_minors_are_acceptable=False,
        acceptable_extensions_order_list=None
        ):

    # print('nineties_minors_are_acceptable: {}'.format(
    #    nineties_minors_are_acceptable))

    if acceptable_extensions_order_list is None:
        acceptable_extensions_order_list = ['.tar.xz', '.tar.bz2', '.tar.gz']

    def source_version_comparator(v1, v2):
        return wayround_org.utils.version.source_version_comparator(
            v1, v2,
            acceptable_extensions_order_list
            )

    tarballs = pkg_client.tarballs(pkgname)

    if tarballs is None:
        tarballs = []

    tarballs.sort(
        reverse=True,
        key=functools.cmp_to_key(
            source_version_comparator
            )
        )
    #print("required_v1: {}, required_v2: {}".format(required_v1, required_v2))
    #print("tarballs: {}".format(pprint.pformat(tarballs)))

    if (required_v1 is None or required_v2 is None) and len(tarballs) != 0:

        for i in tarballs:

            parsed = wayround_org.utils.tarball.parse_tarball_name(
                i,
                mute=True
            )

            parsed_groups_version_list = parsed['groups']['version_list']

            is_nineties = check_nineties(parsed)

            is_development = check_development(parsed)

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
                #print("  {} passed".format(i))
                if required_v1 is None:
                    required_v1 = int(parsed['groups']['version_list'][0])

                if required_v2 is None:
                    required_v2 = int(parsed['groups']['version_list'][1])

                break
            # else:
                #print("  {} didn't passed".format(i))

    #print("required_v1: {}, required_v2: {}".format(required_v1, required_v2))
    found_required_targeted_tarballs = []

    for i in tarballs:

        parsed = wayround_org.utils.tarball.\
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

    # print("found_required_targeted_tarballs: {}".format(
    #    found_required_targeted_tarballs))

    if (len(found_required_targeted_tarballs) == 0
            and find_lower_version_if_required_missing == True):

        next_found_acceptable_tarball = None

        for i in tarballs:

            parsed = wayround_org.utils.tarball.\
                parse_tarball_name(i, mute=True)

            if parsed:

                parsed_groups_version_list = \
                    parsed['groups']['version_list']

                int_parsed_groups_version_list_1 = \
                    int(parsed_groups_version_list[1])

                if required_v2 is not None:
                    if int_parsed_groups_version_list_1 >= required_v2:
                        continue

                is_nineties = check_nineties(parsed)

                is_development = check_development(parsed)

                if next_found_acceptable_tarball is None:

                    if (is_nineties
                            and nineties_minors_are_acceptable == True
                            and int_parsed_groups_version_list_1 < required_v2
                            ):
                        next_found_acceptable_tarball = i

                    if (next_found_acceptable_tarball is None
                            and is_development
                            and development_are_acceptable == True
                            and int_parsed_groups_version_list_1 < required_v2
                            ):
                        next_found_acceptable_tarball = i

                    if (next_found_acceptable_tarball is None
                            and not is_nineties
                            and not is_development
                            and int_parsed_groups_version_list_1 < required_v2
                            ):
                        next_found_acceptable_tarball = i

                if next_found_acceptable_tarball is not None:
                    break

        if next_found_acceptable_tarball is not None:

            for i in tarballs:
                if wayround_org.utils.version.source_version_comparator(
                        i,
                        next_found_acceptable_tarball,
                        acceptable_extensions_order_list
                        ) == 0:
                    found_required_targeted_tarballs.append(i)

    ret = None
    for j in found_required_targeted_tarballs:
        for i in acceptable_extensions_order_list:
            if j.endswith(i):
                ret = j
                break
        if ret is not None:
            break

    if ret is None and len(found_required_targeted_tarballs) != 0:
        ret = found_required_targeted_tarballs[0]

    return ret


def gnome_get(
        mode,
        pkg_client,
        src_client,
        acceptable_extensions_order_list,
        host,
        arch,
        pkgname,
        version,
        args,
        kwargs
        ):
    """
    """

    ret = None

    # if kwargs is None:
    #    kwargs = {}

    if not mode in ['tar', 'asp']:
        raise ValueError("`mode' must be in ['tar', 'asp']")

    if mode == 'tar':

        version_numbers = None, None

        if 'version' in kwargs:
            listed_version = kwargs['version']

            if not '{asked_version}' in listed_version:
                version = listed_version
            else:
                version = listed_version.format(asked_version=version)

            version_numbers = version.split('.')

            for i in range(len(version_numbers)):
                version_numbers[i] = int(version_numbers[i])

            del kwargs['version']

        # if kwargs = {}

        if 'nmaa' in kwargs:
            kwargs['nineties_minors_are_acceptable'] = kwargs['nmaa']
            del kwargs['nmaa']

        if 'daa' in kwargs:
            kwargs['development_are_acceptable'] = kwargs['daa']
            del kwargs['daa']

        if 'flvirm' in kwargs:
            kwargs['find_lower_version_if_required_missing'] = kwargs['flvirm']
            del kwargs['flvirm']

        # print("kwargs: {}".format(kwargs))

        tarball = find_gnome_tarball_name(
            pkg_client,
            pkgname,
            required_v1=version_numbers[0],
            required_v2=version_numbers[1],
            acceptable_extensions_order_list=acceptable_extensions_order_list,
            **kwargs
            )

        if tarball is None:
            ret = 2
        else:

            if not isinstance(
                    wayround_org.aipsetup.client_pkg.get_tarball(tarball),
                    str
                    ):
                ret = 3

            else:

                ret = 0

    elif mode == 'asp':
        ret = normal_get(
            mode,
            pkg_client,
            src_client,
            acceptable_extensions_order_list,
            host,
            arch,
            pkgname,
            version,
            args,
            kwargs
            )

    return ret


def normal_get(
        mode,
        pkg_client, src_client,
        acceptable_extensions_order_list,
        host, arch,
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
                    if not isinstance(k, str):
                        pass
                    else:
                        if k.endswith(j):
                            found = k
                            break
                if found is not None:
                    break
            if found is None:
                found = res[0]

            if found is None:
                logging.error("Could not get tarball for `{}'".format(pkgname))
                ret = 4
            else:
                if not isinstance(
                        wayround_org.aipsetup.client_pkg.get_tarball(found),
                        str
                        ):
                    ret = 3
        else:
            ret = 2

    elif mode == 'asp':

        if not isinstance(
                pkg_client.get_latest_asp(
                    pkgname,
                    host,
                    arch
                    ),
                str
                ):
            ret = 1

    return ret


def _get_by_glp_subroutine(
        mode,
        pkg_client,
        src_client,
        name,
        acceptable_extensions_order_list,
        host,
        arch,
        version,
        proc,
        args,
        kwargs,
        mute
        ):

    ret = 0

    res = proc(
        mode,
        pkg_client,
        src_client,
        acceptable_extensions_order_list,
        host,
        arch,
        name,
        version=version,
        args=args,
        kwargs=kwargs
        )

    res_text = None

    if isinstance(res, int) and res != 0:
        res_text = 'ERROR'
        ret = 1

    else:
        res_text = 'OK'

    if not mute:
        print("   getting {:/<40}: {}".format("`{}'".format(name), res_text))

    return ret


def _get_by_glp_subroutine2(data):

    proc = normal_get
    args = []
    kwargs = {}

    if 'proc' in data:
        if data['proc'] == 'normal_get':
            proc = normal_get

        elif data['proc'] == 'gnome_get':
            proc = gnome_get

        else:
            raise Exception("invalid `proc' value: {}".format(data['proc']))

    if 'args' in data:
        args = data['args']

    if 'kwargs' in data:
        kwargs = data['kwargs']

    return proc, args, kwargs


def get_by_glp(
        mode,
        conf,
        version,
        pkg_client, src_client,
        acceptable_extensions_order_list,
        host,
        arch,
        mute=False
        ):

    if not mode in ['tar', 'asp']:
        raise ValueError("`mode' must be in ['tar', 'asp']")

    if not isinstance(
            pkg_client,
            wayround_org.aipsetup.client_pkg.PackageServerClient
            ):
        raise TypeError(
            "`pkg_client' must be inst of "
            "wayround_org.aipsetup.client_pkg.PackageServerClient"
            )

    if not isinstance(
            src_client,
            wayround_org.aipsetup.client_src.SourceServerClient
            ):
        raise TypeError(
            "`pkg_client' must be inst of "
            "wayround_org.aipsetup.client_src.SourceServerClient"
            )

    ret = 0

    if ('ask_version' in conf
            and conf['ask_version'] == True
            and version is None):

        logging.error("Version is required")

        ret = 1
    else:

        names_obj = conf['names']
        names_obj_t = type(names_obj)

        if names_obj_t not in [list, dict]:
            logging.error("invalid type of `names' section")
            ret = 2

        if ret == 0:

            errors = 0

            if names_obj_t == list:

                data_dict = {}

                for i in names_obj:

                    i_type = type(i)

                    if i_type == str:
                        if i in data_dict:
                            logging.warning(
                                "`{}' already in names."
                                " duplicated. using new..".format(i)
                                )
                        data_dict[i] = {
                            'name': i,
                            'proc': 'normal_get',
                            'args': (),
                            'kwargs': {}
                            }
                    elif i_type == dict:
                        if i['name'] in data_dict:
                            logging.warning(
                                "`{}' already in names."
                                " duplicated. using new..".format(i['name'])
                                )
                        data_dict[i['name']] = i
                        if 'name' in i:
                            del i['name']

                    else:
                        raise Exception("invalid data. programming error")

                names_obj = data_dict
                # names_obj_t = dict

            for i in sorted(list(names_obj.keys())):
                i_name = i

                if ('name' in names_obj[i]
                        and names_obj[i]['name'] != i_name):
                    logging.error(
                        "`{}' != `{}'".format(
                            names_obj[i]['name'],
                            i_name
                            )
                        )

                proc, args, kwargs = _get_by_glp_subroutine2(names_obj[i])

                errors += _get_by_glp_subroutine(
                    mode,
                    pkg_client,
                    src_client,
                    i_name,
                    acceptable_extensions_order_list,
                    host,
                    arch,
                    version,
                    proc,
                    args,
                    kwargs,
                    mute
                    )

            ret = int(errors > 0)

    return ret


def get_list(config, list_name):

    # TODO: place next to config

    list_filename = wayround_org.utils.path.abspath(
        wayround_org.utils.path.join(
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
