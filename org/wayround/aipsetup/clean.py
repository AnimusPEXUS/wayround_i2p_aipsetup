
"""
System and package index cleaning tools

Detecting collisions and various errors and garbage
"""

import logging
import os
import shutil
import functools
import datetime
import pprint

import org.wayround.aipsetup.package
import org.wayround.aipsetup.name
import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkgdeps

import org.wayround.utils.path
import org.wayround.utils.deps_c
import org.wayround.utils.format.elf
import org.wayround.utils.file
import org.wayround.utils.checksum

def cli_name():
    return 'clean'


def exported_commands():
    return {
        'so_problems':  clean_find_so_problems,
        'old_packages': clean_find_old_packages,
        'packages_with_not_reduced_asps':
                        clean_check_list_of_installed_packages_and_asps_auto,
        'packages_with_broken_files':
                        clean_packages_with_broken_files,
        'repo_clean':   clean_cleanup_repo,
        'check_elfs_readiness':
                        clean_check_elfs_readiness
        }

def commands_order():
    return [
        'packages_with_not_reduced_asps',
        'so_problems',
        'old_packages',
        'packages_with_broken_files',
        'repo_clean',
        'check_elfs_readiness'
        ]

def clean_packages_with_broken_files(opts, args):

    """
    Find packages with broken files
    """

    r = org.wayround.aipsetup.package.list_installed_asps_and_their_sums(mute=False)

    logging.info("Checking Packages")

    asps = list(r.keys())
    asps_c = len(asps)

    problems = {}

    b = 0
    m = 0

    for i in range(asps_c):

        asp_name = asps[i]

        asp = r[asp_name]

        if isinstance(asp, dict):

            problems[asp_name] = {'missing':[], 'broken':[]}

            files = list(asp.keys())
            fc = len(files)
            fi = 0

            perc = 0
            if i != 0:
                perc = (100.0 / (asps_c / i))

            for j in files:

                if not os.path.exists(j):
                    problems[asp_name]['missing'].append(j)
                    m += 1

                else:

                    sum = org.wayround.utils.checksum.make_file_checksum(
                        j, method='sha512'
                        )

                    if sum != asp[j]:
                        problems[asp_name]['broken'].append(j)
                        b += 1

                fi += 1

                org.wayround.utils.file.progress_write(
                    "    ({perc:5.2f}%) {p} packages of {pc}, {f} files of {fc}. found {b} broken, {m} missing".format(
                        perc=perc,
                        p=i,
                        pc=asps_c,
                        f=fi,
                        fc=fc,
                        m=m,
                        b=b
                        )
                    )

    for i in list(problems.keys()):

        if len(problems[i]['missing']) == 0 and len(problems[i]['broken']) == 0:
            del problems[i]

    print()

    log = org.wayround.utils.log.Log(
        os.getcwd(), 'problems'
        )

    log.info(pprint.pformat(problems))

    log_name = log.log_filename

    log.close()

    logging.info("Log saved to {}".format(log_name))

    return 0

def clean_check_elfs_readiness(opts, args):

    """
    Performs system ELF files read checks

    This is mainly needed to test aipsetup elf reader, but on the other hand it
    can be used to detect broken elf files.
    """

    check_elfs_readiness()

    return 0

def clean_find_so_problems(opts, args):

    """
    Find so libraries missing in system and write package names requiring those
    missing libraries.
    """

    ret = 0

    basedir = '/'
#    if '-b' in opts:
#        basedir = opts['-b']

    problems = org.wayround.utils.deps_c.find_so_problems_in_linux_system(
        verbose=True
        )

    libs = list(problems.keys())
    libs.sort()

    log = org.wayround.utils.log.Log(
        os.getcwd(), 'problems'
        )

    print("Writing log to {}".format(log.log_filename))

    logging.info("Gathering asps file tree. Please wait...")
    tree = org.wayround.aipsetup.package.list_installed_asps_and_their_files(basedir, mute=False)
    logging.info("Now working")

    total_problem_packages_list = set()

    count_checked = 0
    libs_c = len(libs)
    for i in libs:
        log.info("Library `{}' required by following files:".format(i))

        files = problems[i]
        files.sort()

        for j in files:
            log.info("    {}".format(j))


        pkgs2 = org.wayround.aipsetup.package.find_file_in_files_installed_by_asps(
            basedir, files, mode='end', mute=False, predefined_asp_tree=tree
            )

        pkgs2_l = list(pkgs2.keys())
        pkgs2_l.sort()

        count_checked += 1

        log.info("  Contained in problem packages:")
        for j in pkgs2_l:
            log.info("    {}".format(j))

        total_problem_packages_list |= set(pkgs2_l)

        logging.info(
            "Checked libraries: {} of {}".format(count_checked, libs_c)
            )

        log.info('---------------------------------')

    pkgs = org.wayround.aipsetup.package.find_file_in_files_installed_by_asps(
        basedir, libs, mode='end', mute=False, predefined_asp_tree=tree
        )

    pkgs_l = list(pkgs.keys())
    pkgs_l.sort()

    log.info('')
    log.info("Libs found in packages:")
    for i in pkgs_l:
        log.info("    {}".format(i))

    log.info('')

    log.info("Total Problem Packages List:")
    total_problem_packages_list = list(total_problem_packages_list)
    total_problem_packages_list.sort()
    for i in total_problem_packages_list:
        log.info("    {}".format(i))

    log.stop()
    print("Log written to {}".format(log.log_filename))

    return ret

def clean_find_old_packages(opts, args):

    """
    Find packages older then month
    """

    # TODO: add arguments

    ret = 0

    res = find_old_packages()

    res.sort()

    for i in res:
        parsed_name = org.wayround.aipsetup.name.package_name_parse(i)

        if not parsed_name:
            logging.warning("Can't parse package name `{}'".format(i))
        else:

            package_date = org.wayround.aipsetup.name.parse_timestamp(
                parsed_name['groups']['timestamp']
                )

            if not package_date:
                logging.error(
                    "Can't parse timestamp {} in {}".format(
                        parsed_name['groups']['timestamp'],
                        i
                        )
                    )
            else:

                print(
                    "    {:30}: {}: {}".format(
                        datetime.datetime.now() - package_date,
                        org.wayround.aipsetup.name.parse_timestamp(
                            parsed_name['groups']['timestamp']
                            ),
                        i
                        )
                      )

    return ret


def clean_cleanup_repo(opts, args):

    """
    Removes old packages from package repository
    """

    # TODO: more descriptive help text required

    cleanup_repo()

    return 0

def clean_check_list_of_installed_packages_and_asps_auto(opts, args):

    """
    Searches for packages with more when one asp installed
    """

    logging.info("Working. Please wait, it will be not long...")

    return check_list_of_installed_packages_and_asps_auto()


def check_elfs_readiness(mute=False):

    # TODO: complete

    paths = org.wayround.utils.deps_c.elf_paths()
    elfs = org.wayround.utils.deps_c.find_all_elf_files(paths, verbose=True)

    elfs = org.wayround.utils.path.realpaths(elfs)

    elfs.sort()

    elfs_c = len(elfs)
    elfs_i = 0

    for i in elfs:
        elfs_i += 1

        if not mute:
            logging.info("({} of {}) Trying to read file {}".format(elfs_i, elfs_c , i))

        org.wayround.utils.format.elf.ELF(i)

    return 0

def check_list_of_installed_packages_and_asps_auto():

    content = org.wayround.aipsetup.package.list_installed_packages_and_asps()

    ret = check_list_of_installed_packages_and_asps(content)

    return ret


def check_list_of_installed_packages_and_asps(in_dict):

    ret = 0

    keys = list(in_dict.keys())

    keys.sort()

    errors = 0

    for i in keys:

        if len(in_dict[i]) > 1:

            errors += 1
            ret = 1

            logging.warning("Package with too many ASPs found `{}'".format(i))

            in_dict[i].sort()

            for j in in_dict[i]:

                print("       {}".format(j))

    if errors > 0:
        logging.warning("Total erroneous packages: {}".format(errors))

    return ret

def find_old_packages(age=None, destdir='/', mute=True):

    if age == None:
        age = (60 * 60 * 24 * 30)  # 30 days

    ret = []

    asps = org.wayround.aipsetup.package.list_installed_asps(destdir, mute=mute)

    for i in asps:

        parsed_name = org.wayround.aipsetup.name.package_name_parse(i, mute=mute)

        if not parsed_name:
            logging.warning("Can't parse package name `{}'".format(i))
        else:

            package_date = org.wayround.aipsetup.name.parse_timestamp(
                parsed_name['groups']['timestamp']
                )

            if not package_date:
                logging.error(
                    "Can't parse timestamp {} in {}".format(
                        parsed_name['groups']['timestamp'],
                        i
                        )
                    )
            else:

                if datetime.datetime.now() - package_date > datetime.timedelta(seconds=age):
                    ret.append(i)

#            if datetime
#            print(
#                "timestamp: {}: {}: {}".format(
#                    parsed_name['groups']['timestamp'],
#                    org.wayround.aipsetup.name.parse_timestamp(
#                        parsed_name['groups']['timestamp']
#                        ),
#                    i
#                    )
#                  )


    return ret


def detect_package_collisions(category_locations, package_locations):

    ret = 0

    lst_dup = {}
    pkg_paths = {}

    for each in package_locations.keys():

        l = package_locations[each]['name'].lower()

        if not l in pkg_paths:
            pkg_paths[l] = []

        pkg_paths[l].append(each)

    for each in package_locations.keys():

        l = package_locations[each]['name'].lower()

        if len(pkg_paths[l]) > 1:
            lst_dup[l] = pkg_paths[l]


    if len(lst_dup) == 0:
        logging.info(
            "Found {} duplicated package names. Package locations looks good!".format(
                len(lst_dup)
                )
            )
        ret = 0
    else:
        logging.warning(
            "Found {} duplicated package names\n        listing:".format(
                len(lst_dup)
                )
            )

        sorted_keys = list(lst_dup.keys())
        sorted_keys.sort()

        for each in sorted_keys:
            print("          {}:".format(each))

            lst_dup[each].sort()

            for each2 in lst_dup[each]:
                print("             {}".format(each2))
        ret = 1

    return ret

def cleanup_repo_package_pack(name):

    g_path = org.wayround.aipsetup.config.config['garbage'] + os.path.sep + name

    if not os.path.exists(g_path):
        os.makedirs(g_path, exist_ok=True)

    path = (
        org.wayround.aipsetup.config.config['repository'] + os.path.sep +
        org.wayround.aipsetup.pkgindex.get_package_path_string(name) +
        os.path.sep + 'pack'
        )


    path = org.wayround.utils.path.abspath(path)

    files = os.listdir(path)
    files.sort()

    for i in files:
        p1 = path + os.path.sep + i

        if os.path.exists(p1):

            if org.wayround.aipsetup.pkgindex.put_asp_to_index(
                path + os.path.sep + i
                ) != 0:

                logging.warning("Can't move file to index. moving to garbage")

                shutil.move(path + os.path.sep + i, g_path + os.path.sep + i)

    files = os.listdir(path)
    files.sort()

    for i in files:

        p1 = path + os.path.sep + i

        if os.path.exists(p1):

            p2 = g_path + os.path.sep + i

            if org.wayround.aipsetup.package.check_package(
                p1, True
                ) != 0:
                logging.warning(
                    "Wrong package, garbaging: `{}'\n\tas `{}'".format(
                        os.path.basename(p1),
                        p2
                        )
                    )
                try:
                    shutil.move(p1, p2)
                except:
                    logging.exception("Can't garbage")

    files = os.listdir(path)
    files.sort(
        key=functools.cmp_to_key(
            org.wayround.aipsetup.version.package_version_comparator
            ),

        reverse=True
        )

    if len(files) > 5:
        for i in files[5:]:
            p1 = path + os.path.sep + i

            logging.warning("Removing outdated package: {}".format(os.path.basename(p1)))
            try:
                os.unlink(p1)
            except:
                logging.exception("Error")


def cleanup_repo_package(name):

    g_path = org.wayround.aipsetup.config.config['garbage'] + os.path.sep + name

    if not os.path.exists(g_path):
        os.makedirs(g_path)

    path = (
        org.wayround.aipsetup.config.config['repository'] + os.path.sep +
        org.wayround.aipsetup.pkgindex.get_package_path_string(name)
        )

    path = org.wayround.utils.path.abspath(path)

    org.wayround.aipsetup.pkgindex.create_required_dirs_at_package(path)

    files = os.listdir(path)

    for i in files:
        if not i in ['.package', 'pack']:

            p1 = path + os.path.sep + i
            p2 = g_path
            logging.warning(
                "moving `{}'\n\tto {}".format(
                    os.path.basename(p1),
                    p2
                    )
                )
            try:
                shutil.move(p1, p2)
            except:
                logging.exception("Can't move file or dir")


def cleanup_repo():

    garbage_dir = org.wayround.aipsetup.config.config['garbage']

    if not os.path.exists(garbage_dir):
        os.makedirs(garbage_dir)

    logging.info("Getting packages information from DB")

    pkgs = org.wayround.aipsetup.pkgindex.get_package_idname_dict(None)

    logging.info("Scanning repository for garbage in packages")

    lst = list(pkgs.keys())
    lst.sort()
    lst_l = len(lst)
    lst_i = -1

    for i in lst:

        lst_i += 1
        perc = 0

        if lst_i == 0:
            perc = 0.0
        else:
            perc = 100.0 / (float(lst_l) / lst_i)

        org.wayround.utils.file.progress_write(
                "    {:6.2f}% (package {})".format(
                    perc,
                    pkgs[i]
                    )
            )

        cleanup_repo_package(pkgs[i])
        cleanup_repo_package_pack(pkgs[i])

    g_files = os.listdir(garbage_dir)

    for i in g_files:
        p1 = garbage_dir + os.path.sep + i
        if not os.path.islink(p1):
            if os.path.isdir(p1):
                if org.wayround.utils.file.isdirempty(p1):
                    try:
                        os.rmdir(p1)
                    except:
                        logging.exception("Error")

#        pkgs[i] = org.wayround.aipsetup.pkgindex.get_package_path_string(
#            i, index_db=index_db
#            )

    return

