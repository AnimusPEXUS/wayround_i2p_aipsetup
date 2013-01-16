
"""
System cleaning tools
"""

import logging
import os

import org.wayround.aipestup.package

import org.wayround.utils.deps_c

def cli_name():
    return 'clean'


def exported_commands():
    return {
        'so_problems'   : clean_find_so_problems,
        'packages_with_not_reduced_asps': clean_check_list_of_installed_packages_and_asps_auto
        }

def commands_order():
    return [
        'packages_with_not_reduced_asps',
        'so_problems'
        ]

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
    tree = org.wayround.aipestup.package.list_installed_asps_and_their_files(basedir, mute=False)
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


        pkgs2 = org.wayround.aipestup.package.find_file_in_files_installed_by_asps(
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

    pkgs = org.wayround.aipestup.package.find_file_in_files_installed_by_asps(
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


def clean_check_list_of_installed_packages_and_asps_auto(opts, args):

    """
    Searches for packages with more when one asp installed
    """

    return check_list_of_installed_packages_and_asps_auto()


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

