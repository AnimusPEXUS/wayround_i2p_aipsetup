
import collections
import datetime
import functools
import logging
import os.path
import pprint
import shlex
import sys

import org.wayround.utils.getopt


def commands():
    return collections.OrderedDict([
        ('local_sys', {
            'check': package_check,
            }),

        ('sys', {
            '_help': 'SystemCtl actions: install, uninstall, etc...',
            'list': system_package_list,
            'lista': system_package_list_asps,
            'install': system_install_package,
            'remove': system_remove_package,
            'reduce': system_reduce_asp_to_latest,
            'find': system_find_package_files,
            'generate_deps': system_make_asp_deps,
            'files': system_list_package_files
            }),

        ('sys_clean', {
            'find_broken': clean_packages_with_broken_files,
            'elf_readiness': clean_check_elfs_readiness,
            'so_problems': clean_find_so_problems,
            'find_old': clean_find_old_packages,
            'explicit_asps':
                clean_check_list_of_installed_packages_and_asps_auto,
            'find_garbage': clean_find_garbage,
            'find_invalid_deps_lists': clean_find_invalid_deps_lists
            }),

        ('sys_deps', {
            'asps_asp_depends_on': pkgdeps_print_asps_asp_depends_on,
            'asp_depends': pkgdeps_print_asp_depends,
            'asps_depending_on_asp': pkgdeps_print_asps_depending_on_asp,
            }),

        ])


def system_install_package(command_name, opts, args, adds):
    """
    Install package(s)

    [-b=DIRNAME] [--force] NAMES

    If -b is given - it is used as destination root
    """

    config = adds['config']

    ret = org.wayround.utils.getopt.check_options(
        opts,
        ['-b', '--force']
        )

    if ret == 0:

        basedir = '/'
        if '-b' in opts:
            basedir = opts['-b']

        force = '--force' in opts

        if len(args) == 0:
            logging.error("Package name(s) required!")
            ret = 2
        else:
            names = args

            fpi = []

            pkg_repo_ctl = \
                org.wayround.aipsetup.controllers.\
                    pkg_repo_ctl_by_config(config)

            info_ctl = \
                org.wayround.aipsetup.controllers.info_ctl_by_config(config)

            syst = org.wayround.aipsetup.controllers.sys_ctl_by_config(
                config,
                info_ctl,
                pkg_repo_ctl,
                basedir
                )

            for name in names:
                ret = syst.install_package(
                    name, force,
                    )
                if ret != 0:
                    logging.error(
                        "Failed to install package: `{}'".format(name)
                        )
                    fpi.append(name)

            if len(fpi) != 0:
                logging.error(
                    "Failed installing packages:"
                    )

                fpi.sort()

                for i in fpi:
                    logging.error("       {}".format(i))

                ret = 3

            org.wayround.aipsetup.sysupdates.all_actions()

    return ret


def system_package_list(command_name, opts, args, adds):

    """
    List installed packages

    [-b=DIRNAME] MASK

    -b is same as in install
    """

    config = adds['config']

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    mask = '*'
    if len(args) > 0:
        mask = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if ret == 0:

        info_ctl = \
            org.wayround.aipsetup.controllers.info_ctl_by_config(config)

        pkg_repo_ctl = \
            org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

        system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
            config, info_ctl, pkg_repo_ctl, basedir
            )

        lst = system.list_installed_packages(mask)

        lst.sort()

        org.wayround.utils.text.columned_list_print(
            lst, fd=sys.stdout.fileno()
            )

    return ret


def system_package_list_asps(command_name, opts, args, adds):

    """
    List installed package's ASPs

    [-b=DIRNAME] NAME

    -b is same as in install
    """

    config = adds['config']

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    name = None

    if len(args) != 1:
        logging.error("Package name required")
    else:

        name = args[0]

        if not isinstance(basedir, str):
            logging.error("given basedir name is wrong")
            ret = 2

        else:

            logging.info("Searching ASPs for package `{}'".format(name))

            info_ctl = \
                org.wayround.aipsetup.controllers.info_ctl_by_config(config)

            pkg_repo_ctl = \
                org.wayround.aipsetup.controllers.\
                    pkg_repo_ctl_by_config(config)

            system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
                config, info_ctl, pkg_repo_ctl, basedir
                )

            lst = system.list_installed_package_s_asps(name)

            lst.sort(
                reverse=True,
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    )
                )

            for i in lst:
                print("    {}".format(i))

    return ret


def system_list_package_files(command_name, opts, args, adds):

    config = adds['config']

    ret = 0

    basedir = '/'

    if '-b' in opts:
        basedir = opts['-b']

    pkg_name = None

    if len(args) != 1:
        logging.error("One package name required")
        ret = 1
    else:

        pkg_name = args[0]

        info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)
        pkg_repo_ctl = \
            org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

        system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
            config, info_ctl, pkg_repo_ctl, basedir
            )

        latest = system.latest_installed_package_s_asp(pkg_name)

        if latest == None:
            logging.error(
                "Error getting latest installed asp of package `{}'".format(
                    pkg_name
                    )
                )
            ret = 2
        else:
            files = system.list_files_installed_by_asp(latest, mute=True)

            files.sort()
            for i in files:
                print(i)

    return ret


def system_remove_package(command_name, opts, args, adds):

    """
    Removes package matching NAME.

    [-b=DIRNAME] [--force] NAME

    --force    force removal of packages for which info is not
               available or which is not removable
    """

    config = adds['config']

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    force = '--force' in opts

    name = None
    if len(args) > 0:
        name = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if not isinstance(name, str):
        logging.error("package to remove not named!")
        ret = 3

    if ret == 0:

        info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

        pkg_repo_ctl = \
            org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

        system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
            config,
            info_ctl,
            pkg_repo_ctl,
            basedir
            )

        ret = system.remove_package(name, force, basedir)

        org.wayround.aipsetup.sysupdates.all_actions()

    return ret


def system_find_package_files(command_name, opts, args, adds):

    """
    Looks for LOOKFOR in all installed packages using one of methods:

    [-b=DIRNAME] [-m=beg|re|plain|sub|fm] LOOKFOR

    ================ ===================================
    -m option value  meaning
    ================ ===================================
    sub              (default) filename contains LOOKFOR
    re               LOOKFOR is RegExp
    beg              file name starts with LOOKFOR
    plain            Exact LOOKFOR match
    fm               LOOKFOR is file mask
    ================ ===================================
    """

    config = adds['config']

    basedir = '/'

    if '-b' in opts:
        basedir = opts['-b']

    look_meth = 'sub'
    if '-m' in opts:
        look_meth = opts['-m']

    lookfor = ''
    if len(args) > 0:
        lookfor = args[0]

    info_ctl = \
        org.wayround.aipsetup.controllers.info_ctl_by_config(config)
    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir
        )

    ret = system.find_file_in_files_installed_by_asps(
        lookfor, mode=look_meth
        )

    if isinstance(ret, dict):

        rd_keys = list(ret.keys())
        if len(rd_keys) == 0:
            logging.info("Not found")
        else:
            logging.info(
                "Found {num} packages with `{inc}'".format_map(
                    {
                        'num': len(rd_keys),
                        'inc': lookfor
                        }
                    )
                )

            print("")
            rd_keys.sort()

            for i in rd_keys:
                print("\t{}:".format(i))

                pp_lst = ret[i]
                pp_lst.sort()

                for j in pp_lst:
                    print("\t\t{}".format(j))

                print("")
        ret = 0

    else:
        ret = 1

    return ret


def system_reduce_asp_to_latest(command_name, opts, args, adds):

    """
    Forcibly reduces named asp, excluding files installed by latest package's
    asp

    [-b=DESTDIR] ASP_NAME
    """

    config = adds['config']

    ret = 0

    destdir = '/'
    if '-b' in opts:
        destdir = opts['-b']

    if len(args) < 1:
        logging.error("One or more argument required")
        ret = 1
    else:

        asp_name = args

        for asp_name in args:
            package_name_parsed = \
                org.wayround.aipsetup.package_name_parser.package_name_parse(
                    asp_name
                    )
            package_name = None

            if not isinstance(package_name_parsed, dict):
                logging.error("Can't parse package name {}".fomat(asp_name))

                ret = 2
            else:
                package_name = package_name_parsed['groups']['name']

                logging.info(
                    "Looking for latest installed asp of package {}".format(
                        package_name
                        )
                    )

                info_ctl = \
                    org.wayround.aipsetup.controllers.\
                        info_ctl_by_config(config)
                pkg_repo_ctl = \
                    org.wayround.aipsetup.controllers.\
                        pkg_repo_ctl_by_config(config)

                system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
                    config,
                    info_ctl,
                    pkg_repo_ctl,
                    destdir
                    )

                asp_name_latest = system.latest_installed_package_s_asp(
                    package_name
                    )

                system.reduce_asps(asp_name_latest, [asp_name])

    return ret


def system_make_asp_deps(command_name, opts, args, adds):

    """
    generates dependencies listing for named asp and places it under
    /destdir/var/log/packages/deps
    """

    config = adds['config']

    ret = 0

    destdir = '/'

    if '-b' in opts:
        destdir = opts['-b']

    if len(args) != 1:
        logging.error("Must be exactly one argument")
        ret = 1
    else:

        asp_name = args[0]

        info_ctl = \
            org.wayround.aipsetup.controllers.info_ctl_by_config(config)
        pkg_repo_ctl = \
            org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

        system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
            config,
            info_ctl,
            pkg_repo_ctl,
            destdir
            )

        ret = system.make_asp_deps(asp_name, mute=False)

    return ret


def clean_packages_with_broken_files(command_name, opts, args, adds):

    """
    Find packages with broken files
    """

    config = adds['config']

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    r = system.list_installed_asps_and_their_sums(mute=False)

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

            problems[asp_name] = {'missing': [], 'broken': []}

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

                    _sum = org.wayround.utils.checksum.make_file_checksum(
                        j, method='sha512'
                        )

                    if _sum != asp[j]:
                        problems[asp_name]['broken'].append(j)
                        b += 1

                fi += 1

                org.wayround.utils.file.progress_write(
                    "    ({perc:5.2f}%) {p} packages of {pc}, {f} files of "
                    "{fc}. found {b} broken, {m} missing".format(
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

        if (len(
            problems[i]['missing']
            ) == 0
            and len(problems[i]['broken']) == 0):
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


def clean_check_elfs_readiness(command_name, opts, args, adds):

    """
    Performs system ELF files read checks

    This is mainly needed to test aipsetup elf reader, but on the other hand it
    can be used to detect broken elf files.
    """

    config = adds['config']

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    ret = system.check_elfs_readiness()

    return ret


def clean_find_so_problems(command_name, opts, args, adds):

    """
    Find so libraries missing in system and write package names requiring those
    missing libraries.
    """

    config = adds['config']

    ret = 0

    basedir = '/'
#    if '-b' in opts:
#        basedir = opts['-b']

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config, info_ctl, pkg_repo_ctl, basedir
        )

    problems = system.find_so_problems_in_system(
        verbose=True
        )

    libs = list(problems.keys())
    libs.sort()

    log = org.wayround.utils.log.Log(
        os.getcwd(), 'problems'
        )

    print("Writing log to {}".format(log.log_filename))

    logging.info("Gathering asps file tree. Please wait...")
    tree = system.list_installed_asps_and_their_files(mute=False)
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

        pkgs2 = system.find_file_in_files_installed_by_asps(
            files, mode='end', mute=False, predefined_asp_tree=tree
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

    pkgs = system.find_file_in_files_installed_by_asps(
        libs, mode='end', mute=False, predefined_asp_tree=tree
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


def clean_find_old_packages(command_name, opts, args, adds):

    """
    Find packages older then month
    """

    # TODO: add arguments
    # TODO: must work with basedir!

    config = adds['config']

    ret = 0

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    res = system.find_old_packages()

    res.sort()

    for i in res:
        parsed_name = \
            org.wayround.aipsetup.package_name_parser.package_name_parse(i)

        if not parsed_name:
            logging.warning("Can't parse package name `{}'".format(i))
        else:

            package_date = \
                org.wayround.aipsetup.package_name_parser.parse_timestamp(
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
                org.wayround.aipsetup.package_name_parser.parse_timestamp(
                    parsed_name['groups']['timestamp']
                    ),
                i
                )
                      )

    return ret


def clean_find_invalid_deps_lists(command_name, opts, args, adds):

    config = adds['config']

    ret = 0

    basedir = '/'

    if '-b' in opts:
        basedir = opts['-b']

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir=basedir
        )

    asps = system.list_installed_asps(mute=False)

    # TODO: move it to System class

    for i in asps:

        asp_deps = system.load_asp_deps(i, mute=False)

        if not isinstance(asp_deps, dict):
            logging.error("{} has wrong dependencies dict".format(i))

        else:

            for j in asp_deps.keys():

                if not isinstance(asp_deps[j], list):
                    logging.error(
                        "{} has wrong dependencies list for {}".format(i, j)
                        )

                else:

                    for k in asp_deps[j]:
                        if not isinstance(k, str):
                            logging.error(
                    "{} has wrong dependencies list items for {}".format(i, j)
                                )

    return ret


def clean_find_garbage(command_name, opts, args, adds):

    """
    Search system for garbage making log and cleaning script

    -b=BASENAME        - system root path
    --script-type=bash - system cleaning script language (only bash supported)
    --so               - look only for .so files garbage in /usr/lib directory
    """

    config = adds['config']

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[
                '-b=',
                '--script-type=',
                '--so'
                ]
            ) != 0:
        ret = 1

    if ret == 0:

        timestamp = org.wayround.utils.time.currenttime_stamp()

        basedir = '/'
        script = 'system_garbage_remove_{}.sh'.format(timestamp)
        script_type = 'bash'
        only_lib = False
        down_script = 'get_required_sources_{}.sh'.format(timestamp)

        if '-b' in opts:
            basedir = opts['-b']

        if '--script-type' in opts:
            script_type = opts['--script-type']

        only_lib = '--so' in opts

        log = org.wayround.utils.log.Log(
            os.getcwd(), 'system_garbage', timestamp=timestamp
            )

        if not script_type in ['bash']:
            logging.error("Invalid --script-type value")
            ret = 1
        else:

            info_ctl = \
                org.wayround.aipsetup.controllers.info_ctl_by_config(config)

            pkg_repo_ctl = \
                org.wayround.aipsetup.controllers.\
                    pkg_repo_ctl_by_config(config)

            system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
                config,
                info_ctl,
                pkg_repo_ctl,
                basedir=basedir
                )

            log.info("Searching for garbage")
            res = system.find_system_garbage(mute=False, only_lib=only_lib)

            if not isinstance(res, list):
                log.error("Some error while searching for garbage")
                ret = 1
            else:

                log.info("Garbage search complete")
                log.info(
                    "Separating garbage .so files to know "
                    "which packages depending on them"
                    )

                libs = org.wayround.utils.path.exclude_files_not_in_dirs(
                    res,
                    system.library_paths()
                    )

                libs = org.wayround.aipsetup.system.filter_so_files(
                    libs,
                    verbose=True
                    )

                if only_lib:
                    res = libs

                libs = org.wayround.utils.path.bases(libs)

                asp_deps = system.load_asp_deps_all(mute=False)

                asps_lkd_to_garbage = {}

                log.info("Calculating garbage dependencies")

                for asp_name in list(asp_deps.keys()):

                    if not asp_name in asps_lkd_to_garbage:
                        asps_lkd_to_garbage[asp_name] = dict()

                    for file_name in list(asp_deps[asp_name].keys()):

                        file_name_with_dest_dir = \
                            org.wayround.utils.path.insert_base(
                                file_name, basedir
                                )

                        if (not file_name_with_dest_dir
                            in asps_lkd_to_garbage[asp_name]):
                            asps_lkd_to_garbage[
                                asp_name
                                ][file_name_with_dest_dir] = set()

                        asps_lkd_to_garbage[
                            asp_name
                            ][file_name_with_dest_dir] |= \
                            (set(libs) & set(asp_deps[asp_name][file_name]))

                        if len(
                            asps_lkd_to_garbage[
                                asp_name][file_name_with_dest_dir]
                               ) == 0:
                            del asps_lkd_to_garbage[
                                    asp_name][file_name_with_dest_dir]

                    if len(asps_lkd_to_garbage[asp_name]) == 0:
                        del asps_lkd_to_garbage[asp_name]

                s = open(script, 'w')

                s.write("""\
#!/bin/bash

# This is fuse to ensure You are know what You are doing
exit 1


""")

                log.info("Writing report and cleaning script")

                res.sort()

                for i in res:
                    try:
                        log.info("    {}".format(i), echo=False)
                    except:
                        log.error("Error logging {}".format(repr(i)))

                    try:
                        s.write("rm {}\n".format(shlex.quote(i)))
                    except:
                        log.error("Error writing {}".format(repr(i)))

                log.info(
                    "Packages linked to garbage libraries:\n{}".format(
                        pprint.pformat(asps_lkd_to_garbage)
                        ),
                    echo=False
                    )

                log.info("Generating download script")
                required_packages = set()

                for i in list(asps_lkd_to_garbage.keys()):
                    p = org.wayround.aipsetup.package_name_parser.\
                        package_name_parse(i)

                    if not p:
                        log.error(
            "Can't parse ASP name `{}' to add it to download script".format(i)
                            )
                    else:
                        required_packages.add(p['groups']['name'])

                log.info("Writing download script")
                ds = open(down_script, 'w')
                ds.write(
                    """\
#!/bin/bash

aipsetup3 src getl {}
""".format(' '.join(required_packages))
                    )

                ds.close()

                s.close()

                logging.warning("""
Do not run cleaning script at once!
Check everything is correct!
Wrong cleaning can ruin your system
"""
                    )

            log.close()

    return ret


def clean_check_list_of_installed_packages_and_asps_auto(
    command_name, opts, args, adds
    ):

    """
    Searches for packages with more when one asp installed
    """

    config = adds['config']

    logging.info("Working. Please wait, it will be not long...")

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    return pkg_repo_ctl.check_list_of_installed_packages_and_asps_auto()


def pkgdeps_print_asps_asp_depends_on(command_name, opts, args, adds):

    config = adds['config']

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    r = system.get_asps_asp_depends_on(args[0], mute=False)

    pprint.pprint(r)

    return 0


def pkgdeps_print_asp_depends(command_name, opts, args, adds):

    ret = 0

    config = adds['config']

    info_ctl = \
        org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    r = system.get_asp_dependencies(args[0], mute=False)

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


def pkgdeps_print_asps_depending_on_asp(command_name, opts, args, adds):

    config = adds['config']

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_repo_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    system = org.wayround.aipsetup.controllers.sys_ctl_by_config(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    r = system.get_asps_depending_on_asp(args[0], mute=False)

    pprint.pprint(r)

    return 0


def package_check(command_name, opts, args, adds):

    """
    Check package for errors
    """

    ret = 0

    file = None

    if len(args) == 1:
        file = args[0]

    if file == None:
        logging.error("Filename required")
        ret = 2

    else:

        asp_pkg = org.wayround.aipsetup.controllers.asp_package(file)

        ret = asp_pkg.check_package()

    return ret
