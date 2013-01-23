
"""
Package dependency tools
"""

import logging
import os.path
import pprint

import org.wayround.utils.deps_c
import org.wayround.utils.format.elf

import org.wayround.aipsetup.package

def cli_name():
    """
    aipsetup CLI related functionality
    """
    return 'deps'

def exported_commands():
    """
    aipsetup CLI related functionality
    """

    return {
        'asp_dependings': pkgdeps_print_asps_asp_depends_on,
        'asp_depends': pkgdeps_print_asp_depends,
        'asps_depending_on_asp': pkgdeps_print_asps_depending_on_asp
        }

def commands_order():
    """
    aipsetup CLI related functionality
    """
    return [
        'asp_dependings',
        'asp_depends',
        'asps_depending_on_asp'
        ]


def pkgdeps_print_asps_asp_depends_on(opts, args):

    r = get_asps_asp_depends_on('/', args[0], mute=False)

    pprint.pprint(r)

    return 0

def pkgdeps_print_asp_depends(opts, args):

    ret = 0

    r = get_asp_dependencies('/', args[0], mute=False)

    if not isinstance(r, dict):
        logging.error(
            "Couldn't get {} dependencies".format(
                args[0]
                )
            )
        ret = 1
    else:

        pprint.pprint(r)

    return ret


def pkgdeps_print_asps_depending_on_asp(opts, args):

    r = get_asps_depending_on_asp('/', args[0], mute=False)

    pprint.pprint(r)

    return 0


def get_asps_depending_on_asp(destdir, asp_name, mute=False):

    ret = 0

    asp_name_installed_asps = (
        org.wayround.aipsetup.package.list_files_installed_by_asp(
            destdir, asp_name, mute=mute
            )
        )

    asp_name_installed_asps = org.wayround.utils.path.prepend_path(
        asp_name_installed_asps, destdir
        )

    asp_name_installed_asps = org.wayround.utils.path.realpaths(
        asp_name_installed_asps
        )

    asp_name_installed_asps2 = []

    for i in range(len(asp_name_installed_asps)):

        e = org.wayround.utils.format.elf.ELF(asp_name_installed_asps[i])
        if e.is_elf:
            asp_name_installed_asps2.append(asp_name_installed_asps[i])

    asp_name_installed_asps = asp_name_installed_asps2

    del(asp_name_installed_asps2)

    if not mute:
        logging.info("Getting list of all asps installed in system")

#    all_asps_and_files = org.wayround.aipsetup.package.list_installed_asps(
#        destdir, mute=mute
#        )

    all_asps_and_files = ['xf86-video-rendition-4.2.4-20110808210334-i486-pc-linux-gnu.xz']

    deps_list = set()

    if not mute:
        logging.info("setting list of asps depending on asp")

    all_asps_and_files_c = len(all_asps_and_files)
    all_asps_and_files_i = 0

    last_found = None

# error with 'xf86-video-rendition-4.2.4-20110808210334-i486-pc-linux-gnu.xz'
    print(repr(all_asps_and_files))
    for i in set(all_asps_and_files):

        if not i in deps_list:

            i_deps = get_asp_dependencies(destdir, i, mute=False)

            if not isinstance(i_deps, dict):
                if not mute:
                    logging.error(
                        "Couldn't get {} dependencies".format(
                            i
                            )
                        )
                ret = 1
            else:
                for j in i_deps:

                    for k in asp_name_installed_asps:
                        if k.endswith(j):
                            deps_list.add(i)
                            last_found = i
                            break

                    if i in deps_list:
                        break
        if ret != 0:
            break

        all_asps_and_files_i += 1

        if not mute:
#            org.wayround.utils.file.progress_write(
            print(
                "    {} of {} ({:.2f}%) found: {}; last found: {}".format(
                    all_asps_and_files_i,
                    all_asps_and_files_c,
                    100.0 / (all_asps_and_files_c / all_asps_and_files_i),
                    len(deps_list),
                    last_found
                    )
                )

    if not mute:
        print('')

    if ret == 0:
        ret = list(deps_list)

    return ret

def get_asps_asp_depends_on(destdir, asp_name, mute=False):

    # TODO: optimizations required

    """
    Returns ``list`` on success
    """

    ret = 0

    elfs_installed_by_asp_name_deps = get_asp_dependencies(
        destdir, asp_name, mute=mute
        )

    if not isinstance(elfs_installed_by_asp_name_deps, dict):
        if not mute:
            logging.error(
                "Couldn't get {} dependencies".format(
                    asp_name
                    )
                )
        ret = 1

    else:

        if not mute:
            logging.info("summarizing elf deps")

        all_deps = set()

        for i in set(elfs_installed_by_asp_name_deps.keys()):
            all_deps |= set(elfs_installed_by_asp_name_deps[i])

        if not mute:
            logging.info("Getting list of all files installed in system")

        all_asps_and_files = (
            org.wayround.aipsetup.package.list_installed_asps_and_their_files(
                destdir=destdir,
                mute=mute
                )
            )

        required_asps = set()

        if not mute:
            logging.info("setting list of required asps. final action.")

        for i in set(all_asps_and_files.keys()):

            for j in all_asps_and_files[i]:

                for k in all_deps:

                    if j.endswith(k):
                        required_asps.add(i)

        ret = list(required_asps)

    return ret

def get_asp_dependencies(destdir, asp_name, mute=False):

    """
    Build dependency list for each elf in asp

    On success returns ``dict``
    """

    ret = 0

    if not mute:
        logging.info("Getting list of files installed by {}".format(asp_name))

    files_installed_by_asp_name = (
        org.wayround.aipsetup.package.list_files_installed_by_asp(
            destdir, asp_name, mute=mute
            )
        )

    if not isinstance(files_installed_by_asp_name, list):
        if not mute:
            logging.error(
                "Can't get list of files installed by {}".format(
                    asp_name
                    )
                )
        ret = 1
    else:

        if not mute:
            logging.info("{} files".format(len(files_installed_by_asp_name)))

        files_installed_by_asp_name = org.wayround.utils.path.prepend_path(
            files_installed_by_asp_name, destdir
            )

        files_installed_by_asp_name = org.wayround.utils.path.realpaths(
            files_installed_by_asp_name
            )

        if not mute:
            logging.info("destdir prepended")

            logging.info("getting list of elf files from files installed by asp")

        elfs_installed_by_asp_name = set()
        for i in files_installed_by_asp_name:

            e = org.wayround.utils.format.elf.ELF(i)
            if e.is_elf:
                elfs_installed_by_asp_name.add(os.path.realpath(i))

        elfs_installed_by_asp_name_deps = {}

        if not mute:
            logging.info("getting elf deps")

        for i in elfs_installed_by_asp_name:

            if not i in elfs_installed_by_asp_name_deps:
                elfs_installed_by_asp_name_deps[i] = set()

            e = org.wayround.utils.format.elf.ELF(i)
            i_libs_list = e.needed_libs_list

            if isinstance(i_libs_list, (list, set)):
                elfs_installed_by_asp_name_deps[i] |= set(
                    i_libs_list
                    )

        ret = elfs_installed_by_asp_name_deps

    return ret
