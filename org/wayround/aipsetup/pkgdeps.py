
"""
Package dependency tools
"""

import copy
import logging
import os.path
import pprint
import io

import org.wayround.utils.deps_c
import org.wayround.utils.format.elf
import org.wayround.utils.path
import org.wayround.utils.archive

import org.wayround.aipsetup.package
import org.wayround.aipsetup.name
import org.wayround.aipsetup.config

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

    asp_name_latest = None

    package_name_parsed = org.wayround.aipsetup.name.package_name_parse(asp_name)
    package_name = None

    if not isinstance(package_name_parsed, dict):
        if not mute:
            logging.error("Can't parse package name {}".format(asp_name))

        ret = 0
    else:
        package_name = package_name_parsed['groups']['name']

        if not mute:
            logging.info(
                "Looking for latest installed asp of package {}".format(
                    package_name
                    )
                )

        asp_name_latest = (
            org.wayround.aipsetup.package.latest_installed_package_s_asp(
                package_name,
                destdir
                )
            )

        if not mute:
            logging.info("Latest asp is {}".format(asp_name_latest))

        asp_name_latest_files = []

        if asp_name_latest:

            if asp_name_latest == asp_name:
                if not mute:
                    logging.info("Selected asp is latest")
            else:

                if not mute:
                    logging.info("Loading it's file list")

                asp_name_latest_files = (
                    org.wayround.aipsetup.package.list_files_installed_by_asp(
                        destdir,
                        asp_name_latest
                        )
                    )

                asp_name_latest_files = org.wayround.utils.path.prepend_path(
                    asp_name_latest_files, destdir
                    )

                asp_name_latest_files = org.wayround.utils.path.realpaths(
                    asp_name_latest_files
                    )

                asp_name_latest_files2 = []
                for i in asp_name_latest_files:
                    if os.path.isfile(i):
                        asp_name_latest_files2.append(i)

                asp_name_latest_files = asp_name_latest_files2

                del(asp_name_latest_files2)

                asp_name_latest_files2 = []

                for i in range(len(asp_name_latest_files)):

                    e = org.wayround.utils.format.elf.ELF(asp_name_latest_files[i])
                    if e.is_elf:
                        asp_name_latest_files2.append(asp_name_latest_files[i])

                asp_name_latest_files = asp_name_latest_files2

                del(asp_name_latest_files2)

        if not mute:
            logging.info("Loading file list of {}".format(asp_name))

        asp_name_files = (
            org.wayround.aipsetup.package.list_files_installed_by_asp(
                destdir, asp_name, mute=mute
                )
            )

        asp_name_files = org.wayround.utils.path.prepend_path(
            asp_name_files, destdir
            )

        asp_name_files = org.wayround.utils.path.realpaths(
            asp_name_files
            )

        asp_name_files2 = []
        for i in asp_name_files:
            if os.path.isfile(i):
                asp_name_files2.append(i)

        asp_name_files = asp_name_files2

        del(asp_name_files2)

        asp_name_files2 = []

        for i in range(len(asp_name_files)):

            e = org.wayround.utils.format.elf.ELF(asp_name_files[i])
            if e.is_elf:
                asp_name_files2.append(asp_name_files[i])

        asp_name_files = asp_name_files2

        del(asp_name_files2)

        if len(asp_name_latest_files) != 0:
            if not mute:
                logging.info("Excluding latest asp files from selected asp files")

            asp_name_files = list(
                set(asp_name_files) - set(asp_name_latest_files)
                )

        if not mute:
            logging.info("Getting list of all asps installed in system")

        installed_asp_names = org.wayround.aipsetup.package.list_installed_asps(
            destdir, mute=mute
            )

    #    installed_asp_names = ['xf86-video-rendition-4.2.4-20110808210334-i486-pc-linux-gnu.xz']
#        installed_asp_names = ['Parallel-ForkManager-0.7.9-20110825111041-i486-pc-linux-gnu.xz']


        deps_list = dict()

        if not mute:
            logging.info("setting list of asps depending on asp")

        installed_asp_names_c = len(installed_asp_names)
        installed_asp_names_i = 0

        last_found = None

        for i in set(installed_asp_names):

            if not i in deps_list:

                files_list = (
                    org.wayround.aipsetup.package.list_files_installed_by_asp(
                        destdir, i, mute=True
                        )
                    )
#                print("file: {}".format(i))

#                pprint.pprint(files_list)
#                input("debug:>")

                files_list = org.wayround.utils.path.prepend_path(
                    files_list, destdir
                    )

                files_list = org.wayround.utils.path.realpaths(
                    files_list
                    )

                files_list2 = []
                for files_list_item in files_list:
                    if os.path.isfile(files_list_item):
                        files_list2.append(files_list_item)

                files_list = files_list2

                del(files_list2)

                files_list = list(set(files_list) - set(asp_name_latest_files))

                i_deps = get_asp_dependencies(
                    destdir,
                    i,
                    mute=True,
                    predefined_asp_name_files=files_list
                    )

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

                        for k in asp_name_files:
                            if k.endswith(j):
                                if not i in deps_list:
                                    deps_list[i] = set()

                                deps_list[i].add(k)
                                last_found = "{} (depends on file {})".format(
                                    i,
                                    os.path.basename(k)
                                    )

            if ret != 0:
                break

            installed_asp_names_i += 1

            if not mute:
                org.wayround.utils.file.progress_write(
    #            print(
                    "    {} of {} ({:.2f}%) found: {}; last found: {}".format(
                        installed_asp_names_i,
                        installed_asp_names_c,
                        100.0 / (installed_asp_names_c / installed_asp_names_i),
                        len(deps_list),
                        last_found
                        )
                    )

        if not mute:
            print('')

        if ret == 0:
            ret = deps_list

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

def get_asp_dependencies(
    destdir,
    asp_name,
    mute=False,
    predefined_asp_name_files=None,
    force=False
    ):

    """
    Build dependency list for each elf in asp

    On success returns ``dict``, in which each key is file name not prepended
    with destdir

    """

    ret = 0

    destdir = org.wayround.utils.path.abspath(destdir)

    if not force:
        ret = org.wayround.aipsetup.package.load_asp_deps(destdir, asp_name, mute)

    if not isinstance(ret, dict):

        if not mute:
            logging.warning("asp requiring deps list regeneration: {}".format(asp_name))

        ret = 0

        if not mute:
            logging.info("Getting list of files installed by {}".format(asp_name))

        asp_name_files = list()
        if predefined_asp_name_files:
            asp_name_files = list(predefined_asp_name_files)
        else:
            asp_name_files = (
                org.wayround.aipsetup.package.list_files_installed_by_asp(
                    destdir, asp_name, mute=mute
                    )
                )

            if not isinstance(asp_name_files, list):
                if not mute:
                    logging.error(
                        "Can't get list of files installed by {}".format(
                            asp_name
                            )
                        )
                ret = 1
            else:

                asp_name_files = org.wayround.utils.path.prepend_path(
                    asp_name_files, destdir
                    )

                asp_name_files = org.wayround.utils.path.realpaths(
                    asp_name_files
                    )

                asp_name_files2 = []
                for i in asp_name_files:
                    if os.path.isfile(i):
                        asp_name_files2.append(i)

                asp_name_files = asp_name_files2

                del(asp_name_files2)

        if not isinstance(asp_name_files, list):
            if not mute:
                logging.error(
                    "Can't get list of files installed by {}".format(
                        asp_name
                        )
                    )
            ret = 1
        else:

            if not mute:
                logging.info("{} files".format(len(asp_name_files)))


            if not mute:
                logging.info("getting list of elf files from files installed by asp")

            asp_name_elfs = set()
            for i in asp_name_files:

                e = org.wayround.utils.format.elf.ELF(i)
                if e.is_elf:
                    asp_name_elfs.add(os.path.realpath(i))

            asp_name_elf_deps = {}

            if not mute:
                logging.info("getting elf deps")

            for i in asp_name_elfs:

                i_normal = i

                if i_normal.startswith(destdir):
                    i_normal = i_normal[len(destdir):]

                    if not i_normal.startswith(os.path.sep):
                        i_normal = os.path.sep + i_normal

                if not i_normal in asp_name_elf_deps:
                    asp_name_elf_deps[i_normal] = set()

                e = org.wayround.utils.format.elf.ELF(i_normal)
                i_libs_list = e.needed_libs_list

                if isinstance(i_libs_list, (list, set)):
                    asp_name_elf_deps[i_normal] |= set(
                        i_libs_list
                        )

            for i in list(asp_name_elf_deps.keys()):
                asp_name_elf_deps[i] = list(asp_name_elf_deps[i])

            ret = asp_name_elf_deps

    return ret

