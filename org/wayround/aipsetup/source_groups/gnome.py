
import functools
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
    'gnome-system-log': {},
    'gnome-system-monitor': {},
    'gnome-user-docs': {},
    'gnome-user-share': {},
    'gsettings-desktop-schemas': {},
    'gtk+': {},
    'gtkmm': {},
    'gtksourceview': {},
    'gucharmap': {},
    'libgweather': {},
    'mousetweaks': {},
    'mutter': {},
    'nautilus': {},
    'pygobject': {},
    'seed': {'daa': True},
    'sushi': {},
    'totem': {},
    'totem-pl-parser': {},
    'vino': {},
    'yelp': {},
    'yelp-tools': {},
    'yelp-xsl': {},
    'zenity': {},
    }


ADDITIONAL_NAMES = [
    'NetworkManager',
    'at-spi2-atk',
    'at-spi2-core',
    'atk',
    'atkmm',
    'cantarell-fonts',
    'caribou',
    'clutter',
    'clutter-gst',
    'clutter-gtk',
    'cogl',
    'dconf',
    'folks',
    'gdk-pixbuf',
    'gjs',
    'glib',
    'glib-networking',
    'glibmm',
    'gmime',
    'gnome-js-common',
    'gnome-js-common',
    'gnome-video-effects',
    'gobject-introspection',
    'grilo',
    'grilo-plugins',
    'gssdp',
    'gst-plugins-base',
    'gst-plugins-good',
    'gstreamer',
    'gtk+3',
    'gtk-doc',
    'gtk-engines',
    'gtk-engines',
    'gupnp',
    'gupnp-igd',
    'gvfs',
    'json-glib',
    'libchamplain',
    'libcroco',
    'libgdata',
    'libgee',
    'libgnomekbd',
    'libgsf',
    'libgtop',
    'libgxps',
    'libmediaart',
    'libnotify',
    'libpeas',
    'librsvg',
    'libsecret',
    'libsigc++',
    'libsoup',
    'libwnck',
    'libzapojit',
    'mm-common',
    'network-manager-applet',
    'pango',
    'pangomm',
    'rest',
    'tracker',
    'vala',
    'vte'
    ]


def find_gnome_tarball_name(
    pkg_client,
    pkgname,
    required_v1,
    required_v2,
    find_lower_version_if_required_missing=True,
    development_are_acceptable=False,
    nineties_minors_are_acceptable=False,
    acceptable_extensions_order_list=['.tar.xz', '.tar.bz2', '.tar.gz']
    ):

#    print()

    tarballs = pkg_client.tarballs(pkgname)

#    print("tarballs:\n{}".format(tarballs))

    if tarballs == None:
        tarballs = []

    tarballs.sort(
        reverse=True,
        key=functools.cmp_to_key(
            org.wayround.utils.version.source_version_comparator
            )
        )

    found_required_targeted_tarballs = []

#    print("sorted tarballs:\n{}".format(tarballs))

    for i in tarballs:

        parsed = org.wayround.utils.tarball_name_parser.\
            parse_tarball_name(i, mute=True)

        if parsed:

            parsed_groups_version_list = parsed['groups']['version_list']
            if (int(parsed_groups_version_list[0]) == required_v1
                and
                int(parsed_groups_version_list[1]) == required_v2
                ):
                found_required_targeted_tarballs.append(i)

    if (len(found_required_targeted_tarballs) == 0
        and find_lower_version_if_required_missing == True):

        next_found_middle_version = None

        for i in tarballs:

            parsed = org.wayround.utils.tarball_name_parser.\
                parse_tarball_name(i, mute=True)

            if parsed:

                parsed_groups_version_list = \
                    parsed['groups']['version_list']

                is_nineties = \
                    re.match(
                        r'9\d+',
                        parsed_groups_version_list[2]
                        ) != None

                is_development = \
                    re.match(
                        r'\d+[13579]',
                        parsed_groups_version_list[1]
                        ) != None

                if next_found_middle_version == None:

                    if (len(parsed_groups_version_list) > 2
                        and is_nineties
                        and nineties_minors_are_acceptable == True
                        and int(parsed_groups_version_list[0]) == required_v1
                        ):

                        next_found_middle_version = \
                            int(parsed_groups_version_list[1])

                    if (next_found_middle_version == None
                        and is_development
                        and development_are_acceptable == True
                        and int(parsed_groups_version_list[0]) == required_v1
                        ):

                        next_found_middle_version = \
                            int(parsed_groups_version_list[1])

                    if (next_found_middle_version == None
                        and not is_nineties
                        and not is_development
                        and int(parsed_groups_version_list[0]) == required_v1
                        ):

                        next_found_middle_version = \
                            int(parsed_groups_version_list[1])

                if next_found_middle_version != None:
                    if (int(parsed_groups_version_list[0]) == required_v1
                        and int(parsed_groups_version_list[1]) == \
                            next_found_middle_version
                        and ((not is_nineties and not is_development)
                             or (is_nineties
                                 and nineties_minors_are_acceptable == True)
                             or (is_development
                                 and development_are_acceptable == True)
                             )
                        ):
                        found_required_targeted_tarballs.append(i)

#    print("req tarballs:\n{}".format(found_required_targeted_tarballs))

    ret = None
    for i in found_required_targeted_tarballs:
        for j in acceptable_extensions_order_list:
            if i.endswith(j):
                ret = i
                break

    if ret == None and len(found_required_targeted_tarballs) != 0:
        ret = found_required_targeted_tarballs[0]

    return ret


def get_gnome(
    pkg_client,
    src_client,
    required_v1,
    required_v2,
    acceptable_extensions_order_list,
    verbose=False
    ):

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

    found = []
    for i in sorted(list(VERSION_TARGETED_NAMES.keys())):
        if verbose:
            org.wayround.utils.terminal.progress_write(
                "Looking for `{}' `{}.{}'".format(i, required_v1, required_v2)
                )
        res = find_gnome_tarball_name(
            pkg_client,
            i,
            required_v1,
            required_v2,
            find_lower_version_if_required_missing=True,
            development_are_acceptable=(
                'daa' in VERSION_TARGETED_NAMES[i]
                and VERSION_TARGETED_NAMES[i]['daa'] == True
                ),
            nineties_minors_are_acceptable=(
                'nmaa' in VERSION_TARGETED_NAMES[i]
                and VERSION_TARGETED_NAMES[i]['nmaa'] == True
                ),
            acceptable_extensions_order_list=acceptable_extensions_order_list
            )
        if res != None:
            found.append(res)
            if verbose:
                org.wayround.utils.terminal.progress_write(
                    "   found `{}'".format(res), True
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

    for i in found:
        org.wayround.aipsetup.client_pkg.get_tarball(i)

    return 0
