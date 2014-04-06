
import functools
import os.path
import re

import org.wayround.aipsetup.client_pkg
import org.wayround.aipsetup.client_src
import org.wayround.utils.tarball_name_parser
import org.wayround.utils.terminal
import org.wayround.utils.types
import org.wayround.utils.version


VERSION_TARGETED_NAMES = {
    'baobab': {},
    'empathy': {},
    'eog': {},
    'epiphany': {},
    'evince': {},
    'evolution-data-server': {},
    'gcr': {},
    'gdm': {},
    'geocode-glib': {},
    'gnome-backgrounds': {},
    'gnome-bluetooth': {},
    'gnome-calculator': {},
    'gnome-contacts': {},
    'gnome-control-center': {},
    'gnome-desktop': {},
    'gnome-dictionary': {},
    'gnome-disk-utility': {},
    'gnome-font-viewer': {},
    'gnome-icon-theme': {},
    'gnome-icon-theme-extras': {},
    'gnome-icon-theme-symbolic': {},
    'gnome-keyring': {},
    'gnome-menus': {},
    'gnome-online-accounts': {},
    'gnome-online-miners': {},
    'gnome-packagekit': {},
    'gnome-screenshot': {},
    'gnome-session': {},
    'gnome-settings-daemon': {},
    'gnome-shell': {},
    'gnome-shell-extensions': {},
    'gnome-system-log': {'daa': True, 'nmaa': True},
    'gnome-system-monitor': {},
    'gnome-terminal': {},
    'gnome-themes-standard': {},
    'gnome-user-docs': {},
    'gnome-user-share': {},
    'gsettings-desktop-schemas': {},
    'gtk+': {},
    'gtkmm': {'daa': True, 'nmaa': False},
    'gtksourceview': {},
    'gucharmap': {},
    'libgweather': {},
    'mousetweaks': {},
    'mutter': {},
    'nautilus': {},
    'pygobject': {},
    'seed': {},
    'sushi': {'daa': True, 'nmaa': True},
    'totem': {},
    'totem-pl-parser': {},
    'vino': {},
    'yelp': {},
    'yelp-tools': {},
    'yelp-xsl': {},
    'zenity': {}
    }

GNOMMY_NAMES = {
    'gtk-engines': {'nmaa': False, 'daa': False}
    }

ADDITIONAL_NAMES = {
    'NetworkManager': {},
    'at-spi2-atk': {},
    'at-spi2-core': {},
    'atk': {},
    'atkmm': {},
    'cantarell-fonts': {},
    'caribou': {},
    'clutter': {},
    'clutter-gst': {},
    'clutter-gtk': {},
    'cogl': {},
    'dconf': {},
    'folks': {},
    'gdk-pixbuf': {},
    'gjs': {},
    'glib': {},
    'glib-networking': {},
    'glibmm': {},
    'gmime': {},
    'gnome-js-common': {},
    'gnome-video-effects': {},
    'gobject-introspection': {},
    'grilo': {},
    'grilo-plugins': {},
    'gssdp': {},
    'gst-plugins-base': {},
    'gst-plugins-good': {},
    'gstreamer': {},
    'gtk+2': {},
    'gtk-doc': {},
    'gupnp': {},
    'gupnp-igd': {},
    'gvfs': {},
    'json-glib': {},
    'libchamplain': {},
    'libcroco': {},
    'libgdata': {},
    'libgee': {},
    'libgnomekbd': {},
    'libgsf': {},
    'libgtop': {},
    'libgxps': {},
    'libmediaart': {},
    'libnotify': {},
    'libpeas': {},
    'librsvg': {},
    'libsecret': {},
    'libsigc++': {},
    'libsoup': {},
    'libwnck': {},
    'libzapojit': {},
    'mm-common': {},
    'network-manager-applet': {},
    'pango': {},
    'pangomm': {},
    'rest': {},
    'tracker': {},
    'vala': {},
    'vte': {}
    }


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

    tarballs = pkg_client.tarballs(pkgname)

    if tarballs == None:
        tarballs = []

    tarballs.sort(
        reverse=True,
        key=functools.cmp_to_key(
            org.wayround.utils.version.source_version_comparator
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
                        next_found_acceptable_tarball
                        ) == 0:
                    found_required_targeted_tarballs.append(i)

    ret = None
    for i in found_required_targeted_tarballs:
        for j in acceptable_extensions_order_list:
            if i.endswith(j):
                ret = i
                break

    if ret == None and len(found_required_targeted_tarballs) != 0:
        ret = found_required_targeted_tarballs[0]

    return ret


def process_gnommy_names_dict(
    inp_dict,
    pkg_client,
    required_v1=None,
    required_v2=None,
    verbose=False,
    find_lower_version_if_required_missing=True,
    development_are_acceptable=False,
    nineties_minors_are_acceptable=False,
    acceptable_extensions_order_list=None
    ):

    if acceptable_extensions_order_list == None:
        acceptable_extensions_order_list = ['.tar.xz', '.tar.bz2', '.tar.gz']

    found = []
    for i in sorted(list(inp_dict.keys())):
        if verbose:
            org.wayround.utils.terminal.progress_write(
                "Looking for `{}' `{}.{}'".format(i, required_v1, required_v2)
                )

        kwargs = {}

        if 'flvirm' in inp_dict[i]:
            kwargs['find_lower_version_if_required_missing'] = \
                inp_dict[i]['flvirm']
        else:
            if find_lower_version_if_required_missing != None:
                kwargs['find_lower_version_if_required_missing'] = \
                    find_lower_version_if_required_missing

        if 'daa' in inp_dict[i]:
            kwargs['development_are_acceptable'] = \
                inp_dict[i]['daa']
        else:
            if development_are_acceptable != None:
                kwargs['development_are_acceptable'] = \
                    development_are_acceptable

        if 'nmaa' in inp_dict[i]:
            kwargs['nineties_minors_are_acceptable'] = \
                inp_dict[i]['nmaa']
        else:
            if nineties_minors_are_acceptable != None:
                kwargs['nineties_minors_are_acceptable'] = \
                    nineties_minors_are_acceptable

        res = find_gnome_tarball_name(
            pkg_client,
            i,
            required_v1,
            required_v2,
            acceptable_extensions_order_list=acceptable_extensions_order_list,
            **kwargs
            )

        if res != None:
            found.append(res)
            if verbose:
                org.wayround.utils.terminal.progress_write(
                    "   found `{}'".format(os.path.basename(res)), True
                    )
        else:
            if verbose:
                org.wayround.utils.terminal.progress_write(
                    "   not found `{}' `{}.{}'".format(
                        i,
                        required_v1,
                        required_v2
                        ),
                    True
                    )

    return found


def get_gnome(
    pkg_client,
    src_client,
    required_v1,
    required_v2,
    acceptable_extensions_order_list,
    verbose=False
    ):

    if acceptable_extensions_order_list == None:
        acceptable_extensions_order_list = ['.tar.xz', '.tar.bz2', '.tar.gz']

    if not isinstance(required_v1, int):
        raise TypeError("`required_v1' must be int")

    if not isinstance(required_v2, int):
        raise TypeError("`required_v2' must be int")

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

    if not org.wayround.utils.types.struct_check(
        acceptable_extensions_order_list,
        {'t': list, '.': {'t': str}}
        ):
        raise TypeError(
            "`acceptable_extensions_order_list' must be list of str"
            )

    found = process_gnommy_names_dict(
        VERSION_TARGETED_NAMES,
        pkg_client,
        required_v1,
        required_v2,
        verbose,
        True,
        acceptable_extensions_order_list
        )

    for i in found:
        org.wayround.aipsetup.client_pkg.get_tarball(i)

    found = process_gnommy_names_dict(
        GNOMMY_NAMES,
        pkg_client,
        None,
        None,
        verbose,
        True,
        acceptable_extensions_order_list
        )

    for i in found:
        org.wayround.aipsetup.client_pkg.get_tarball(i)

    for i in sorted(list(ADDITIONAL_NAMES.keys())):
        res = pkg_client.tarballs_latest(i)
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

            org.wayround.aipsetup.client_pkg.get_tarball(found)

    return 0
