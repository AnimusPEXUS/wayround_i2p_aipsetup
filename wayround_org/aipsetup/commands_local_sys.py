
import collections
import datetime
import functools
import json
import logging
import os.path
import pprint
import shlex
import sys


import wayround_org.utils.path
import wayround_org.utils.getopt
import wayround_org.utils.archive
import wayround_org.utils.terminal
import wayround_org.utils.datetime_iso8601
import wayround_org.utils.text
import wayround_org.utils.log

import wayround_org.utils.system_type

import wayround_org.aipsetup.host_arch_params


def commands():
    return collections.OrderedDict([
        ('sys', collections.OrderedDict([
            ('_help', 'SystemCtl actions: install, uninstall, etc...'),
            ('list', system_package_list),
            ('lista', system_package_list_asps),
            ('install', system_install_package),
            ('remove', system_remove_package),
            ('reduce', system_reduce_asp_to_latest),
            ('find', system_find_package_files),
            ('generate-deps', system_make_asp_deps),
            ('files', system_list_package_files),
            ('check', package_check),
            ('parse-asp-name', info_parse_pkg_name),
            ('parse-tar-name', info_parse_tarball),
            ('convert-certdata.txt', system_convert_certdata_txt)
            ])),
        ('sys-clean', collections.OrderedDict([
            ('find-broken', clean_packages_with_broken_files),
            ('elf-readiness', clean_check_elfs_readiness),
            ('so-problems', clean_find_so_problems),
            ('find-old', clean_find_old_packages),
            ('explicit-asps',
                clean_check_list_of_installed_packages_and_asps_auto),
            ('find-garbage', clean_find_garbage),
            ('find-packages-requiring-deleteds',
                clean_find_packages_requiring_deleteds),
            ('find-invalid-deps-lists', clean_find_invalid_deps_lists),
            ('find-libtool-la-with-problems',
                clean_find_libtool_la_with_problems),
            ('gen-locale', clean_gen_locale),
            ('sys-users', clean_sys_users),
            ('sys-perms', clean_sys_perms),
            ('install-etc', clean_install_etc),
            ])),
        ('sys-deps', collections.OrderedDict([
            ('asps-asp-depends-on', pkgdeps_print_asps_asp_depends_on),
            ('asp-depends', pkgdeps_print_asp_depends),
            ('asps-depending-on-asp', pkgdeps_print_asps_depending_on_asp)
            ])),
        ('sys-replica', collections.OrderedDict([
            ('instr', system_replica_instruction),
            ('maketree', system_create_directory_tree),
            ('make-flash', system_replica_make_installation_flashdrive)
            ])),
        ('docbook', collections.OrderedDict([
            ('instr', docbook_instruction),
            ('install', docbook_install),
            ])),
        ('sys-snap', collections.OrderedDict([
            ('create', system_snapshot_create),
            ])),
        ])


_process_h_and_a_opts_specific = \
    wayround_org.aipsetup.host_arch_params.process_h_and_a_opts_specific

_process_h_and_a_opts_wide = \
    wayround_org.aipsetup.host_arch_params.process_h_and_a_opts_wide

_process_h_and_a_opts_strict = \
    wayround_org.aipsetup.host_arch_params.process_h_and_a_opts_strict


def system_install_package(command_name, opts, args, adds):
    """
    Install package(s)

    [-b=DIRNAME] [--force]
    [-h=all|cpu-vend-os-triplet] [-a=all|cpu-vend-os-triplet]
    NAMES

    If -b is given - it is used as destination root
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.sysupdates

    config = adds['config']

    ret = wayround_org.utils.getopt.check_options(
        opts,
        ['-b', '--force', '-h', '-a']
        )

    if ret == 0:

        host, arch = _process_h_and_a_opts_specific(opts, config)

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

            pkg_client = \
                wayround_org.aipsetup.controllers.pkg_client_by_config(
                    config
                    )

            syst = wayround_org.aipsetup.controllers.sys_ctl_by_config(
                config,
                pkg_client,
                basedir
                )

            for name in names:
                ret = syst.install_package(
                    name,
                    force,
                    host=host,
                    arch=arch
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

            wayround_org.aipsetup.sysupdates.all_actions()

    return ret


def system_package_list(command_name, opts, args, adds):
    """
    List installed packages

    [-b=DIRNAME]
    [-h=all|cpu-vend-os-triplet] [-a=all|cpu-vend-os-triplet]
    MASK

    -b is same as in install
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    host, arch = _process_h_and_a_opts_wide(opts, config)

    mask = '*'
    if len(args) > 0:
        mask = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if ret == 0:

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(
                config
                )

        system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
            config, pkg_client, basedir
            )

        lst = sorted(
            system.list_installed_packages(
                mask,
                host=host,
                arch=arch
                )
            )

        wayround_org.utils.text.columned_list_print(
            lst, fd=sys.stdout.fileno()
            )

    return ret


def system_package_list_asps(command_name, opts, args, adds):
    """
    List installed package's ASPs

    [-b=DIRNAME]
    [-h=all|cpu-vend-os-triplet] [-a=all|cpu-vend-os-triplet]
    NAME

    -b is same as in install
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.version

    config = adds['config']

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    host, arch = _process_h_and_a_opts_wide(opts, config)

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

            pkg_client = \
                wayround_org.aipsetup.controllers.pkg_client_by_config(
                    config
                    )

            system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
                config, pkg_client, basedir
                )

            lst = system.list_installed_package_s_asps(
                name,
                host=host,
                arch=arch
                )

            lst.sort(
                reverse=True,
                key=functools.cmp_to_key(
                    wayround_org.aipsetup.version.package_version_comparator
                    )
                )

            for i in lst:
                print("    {}".format(i))

    return ret


def system_list_package_files(command_name, opts, args, adds):
    """
    Print list of files installed by package

    [-h=cpu-vend-os-triplet] [-a=cpu-vend-os-triplet]
    PKG_NAME
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 0

    basedir = '/'

    if '-b' in opts:
        basedir = opts['-b']

    host, arch = _process_h_and_a_opts_strict(opts, config)

    pkg_name = None

    if len(args) != 1:
        logging.error("One package name required")
        ret = 1
    else:

        pkg_name = args[0]

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(
                config
                )

        system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
            config, pkg_client, basedir
            )

        latest = system.latest_installed_package_s_asp(
            pkg_name,
            host=host,
            arch=arch
            )

        print('{}'.format(os.path.basename(latest)))
        print('------------------------')

        if latest is None:
            logging.error(
                "Error getting latest installed asp of package `{}'".format(
                    pkg_name
                    )
                )
            ret = 2
        else:
            files = sorted(
                system.list_files_installed_by_asp(
                    latest,
                    mute=True
                    )
                )

            for i in files:
                print(i)

    return ret


def system_remove_package(command_name, opts, args, adds):
    """
    Removes package matching NAME.

    [-b=DIRNAME] [--force]
    [-h=all|cpu-vend-os-triplet] [-a=all|cpu-vend-os-triplet]
    NAME

    --force    force removal of packages for which info is not
               available or which is not removable
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.sysupdates

    config = adds['config']

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    force = '--force' in opts

    host, arch = _process_h_and_a_opts_specific(opts, config)

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

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(
                config
                )

        system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
            config,
            pkg_client,
            basedir
            )

        ret = system.remove_package(
            name,
            force,
            basedir,
            host=host,
            arch=arch
            )

        wayround_org.aipsetup.sysupdates.all_actions()

    return ret


def system_find_package_files(command_name, opts, args, adds):
    """
    Looks for LOOKFOR in all installed packages using one of methods:

    [-b=DIRNAME] [-h=all|cpu-vend-os-triplet] [-a=all|cpu-vend-os-triplet]
    [-m=beg|re|plain|sub|fm] TARGET

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

    import wayround_org.aipsetup.controllers

    config = adds['config']

    basedir = '/'

    if '-b' in opts:
        basedir = opts['-b']

    look_meth = 'sub'
    if '-m' in opts:
        look_meth = opts['-m']

    host, arch = _process_h_and_a_opts_wide(opts, config)

    lookfor = ''
    if len(args) > 0:
        lookfor = args[0]

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        basedir
        )

    ret = system.find_file_in_files_installed_by_asps(
        lookfor,
        mode=look_meth,
        host=host,
        arch=arch
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

                pp_lst = sorted(ret[i])

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
    [-h=cpu-vend-os-triplet] [-a=cpu-vend-os-triplet]
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.package_name_parser

    config = adds['config']

    ret = 0

    destdir = '/'
    if '-b' in opts:
        destdir = opts['-b']

    host, arch = _process_h_and_a_opts_strict(opts, config)

    if len(args) < 1:
        logging.error("One or more argument required")
        ret = 1
    else:

        asp_name = args

        for asp_name in args:
            package_name_parsed = \
                wayround_org.aipsetup.package_name_parser.package_name_parse(
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

                pkg_client = \
                    wayround_org.aipsetup.controllers.pkg_client_by_config(
                        config
                        )

                system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
                    config,
                    pkg_client,
                    destdir
                    )

                asp_name_latest = system.latest_installed_package_s_asp(
                    package_name,
                    host=host,
                    arch=arch
                    )

                system.reduce_asps(
                    asp_name_latest,
                    [asp_name],
                    host=host,
                    arch=arch
                    )

    return ret


def system_make_asp_deps(command_name, opts, args, adds):
    """
    generates dependencies listing for named asp and places it under
    /destdir/var/log/packages/deps
    """

    import wayround_org.aipsetup.controllers

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

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(
                config
                )

        system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
            config,
            pkg_client,
            destdir
            )

        ret = system.make_asp_deps(asp_name, mute=False)

    return ret


def system_create_directory_tree(command_name, opts, args, adds):

    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 0

    destdir = '/'

    if len(args) != 1:
        logging.error("Must be exactly one argument")
        ret = 1
    else:

        destdir = args[0]

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(
                config
                )

        system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
            config,
            pkg_client,
            destdir
            )

        ret = system.create_directory_tree()

    return ret


def clean_packages_with_broken_files(command_name, opts, args, adds):
    """
    Find packages with broken files
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
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

                    _sum = wayround_org.utils.checksum.make_file_checksum(
                        j, method='sha512'
                        )

                    if _sum != asp[j]:
                        problems[asp_name]['broken'].append(j)
                        b += 1

                fi += 1

                wayround_org.utils.terminal.progress_write(
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

    log = wayround_org.utils.log.Log(
        os.getcwd(), 'problems'
        )

    log.info(pprint.pformat(problems))

    log_name = log.log_filename

    # log.close()

    logging.info("Log saved to {}".format(log_name))

    return 0


def clean_check_elfs_readiness(command_name, opts, args, adds):
    """
    Performs system ELF files read checks

    This is mainly needed to test aipsetup elf reader, but on the other hand it
    can be used to detect broken elf files.
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        basedir='/'
        )

    ret = system.check_elfs_readiness()

    return ret


def clean_find_so_problems(command_name, opts, args, adds):
    """
    Find so libraries missing in system and write package names requiring those
    missing libraries.
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 0

    basedir = '/'

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config, pkg_client, basedir
        )

    problems = system.find_so_problems_in_system(
        verbose=True
        )

    libs = sorted(problems.keys())

    log = wayround_org.utils.log.Log(
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

        pkgs2_l = sorted(pkgs2.keys())

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

    print("Log written to {}".format(log.log_filename))

    return ret


def clean_find_old_packages(command_name, opts, args, adds):
    """
    Find packages older then month
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.package_name_parser

    # TODO: add arguments
    # TODO: must work with basedir!

    config = adds['config']

    get_tarballs = '-g' in opts

    ret = 0

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        basedir='/'
        )

    res = sorted(system.find_old_packages())

    errors = False

    for i in res:
        parsed_name = \
            wayround_org.aipsetup.package_name_parser.package_name_parse(i)

        if not parsed_name:
            logging.warning("Can't parse package name `{}'".format(i))
        else:

            package_date = \
                wayround_org.aipsetup.package_name_parser.parse_timestamp(
                    parsed_name['groups']['timestamp']
                    )

            package_name = parsed_name['groups']['name']

            if not package_date:
                logging.error(
                    "Can't parse timestamp {} in {}".format(
                        parsed_name['groups']['timestamp'],
                        i
                        )
                    )
            else:

                logging.info(
                    "    {:30}: {}: {}".format(
                        str(datetime.datetime.now() - package_date),
                        wayround_org.aipsetup.package_name_parser.parse_timestamp(
                            parsed_name['groups']['timestamp']
                            ),
                        i
                        )
                    )

                if get_tarballs:

                    logging.info("        getting..")

                    lat = pkg_client.tarballs_latest(package_name)
                    if lat is not None and len(lat) > 0:
                        res = wayround_org.utils.path.select_by_prefered_extension(
                            lat, config
                            )
                        res = wayround_org.aipsetup.client_pkg.get_tarball(
                            res
                            )
                        if not isinstance(res, str):
                            f = open("!errors!.txt", 'a')
                            f.write(
                                "Can't get tarball for package `{}'\n".format(
                                    package_name
                                    )
                                )
                            f.close()
                            errors = True
                    else:
                        f = open("!errors!.txt", 'a')
                        f.write(
                            "Can't get latest tarball name "
                            "from server for package `{}'\n".format(
                                package_name
                                )
                            )
                        f.close()
                        errors = True

    if errors:
        ret = 10

    return ret


def clean_find_invalid_deps_lists(command_name, opts, args, adds):

    import wayround_org.aipsetup.controllers

    config = adds['config']

    ret = 0

    basedir = '/'

    if '-b' in opts:
        basedir = opts['-b']

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
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
                                "{} has wrong dependencies list items for {}".format(
                                    i, j)
                                )

    return ret


def clean_find_garbage(command_name, opts, args, adds):
    """
    Search system for garbage making log and cleaning script

    [-h=all|cpu-vend-os-triplet] [-a=all|cpu-vend-os-triplet]

    -b=BASENAME        - system root path
    --script-type=bash - system cleaning script language (only bash supported)
    --so               - look only for .so files garbage in /usr/lib directory
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.package_name_parser
    import wayround_org.aipsetup.client_pkg
    import wayround_org.aipsetup.system

    config = adds['config']

    ret = 0

    if wayround_org.utils.getopt.check_options(
            opts,
            opts_list=[
                '-b=',
                '--script-type=',
                '--so',
                '-h=',
                '-a='
                ]
            ) != 0:
        ret = 1

    if ret == 0:

        timestamp = wayround_org.utils.time.currenttime_stamp()

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

        host, arch = _process_h_and_a_opts_specific(opts, config)

        log = wayround_org.utils.log.Log(
            os.getcwd(), 'system_garbage', timestamp=timestamp
            )

        if not script_type in ['bash']:
            logging.error("Invalid --script-type value")
            ret = 1
        else:

            pkg_client = \
                wayround_org.aipsetup.controllers.pkg_client_by_config(
                    config
                    )

            system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
                config,
                pkg_client,
                basedir=basedir
                )

            log.info("Searching for garbage")
            res = system.find_system_garbage(
                mute=False,
                only_lib=only_lib,
                host=host
                )

            if not isinstance(res, list):
                log.error("Some error while searching for garbage")
                ret = 1
            else:

                log.info("Garbage search complete")
                log.info(
                    "Separating garbage .so files to know "
                    "which packages depending on them"
                    )

                libs = wayround_org.utils.path.exclude_files_not_in_dirs(
                    res,
                    system.library_paths(host=host),
                    )

                libs = wayround_org.aipsetup.system.filter_so_files(
                    libs,
                    verbose=True
                    )

                if only_lib:
                    res = libs

                libs = wayround_org.utils.path.bases(libs)

                asp_deps = system.load_asp_deps_all(mute=False)

                asps_lkd_to_garbage = {}

                log.info("Calculating garbage dependencies")

                for asp_name in list(asp_deps.keys()):

                    if not asp_name in asps_lkd_to_garbage:
                        asps_lkd_to_garbage[asp_name] = dict()

                    for file_name in list(asp_deps[asp_name].keys()):

                        file_name_with_dest_dir = \
                            wayround_org.utils.path.insert_base(
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
                    p = wayround_org.aipsetup.package_name_parser.\
                        package_name_parse(i)

                    if not p:
                        log.error(
                            "Can't parse ASP name `{}' to add it to download script".format(
                                i)
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

            # log.close()

    return ret


def clean_find_packages_requiring_deleteds(
        command_name, opts, args, adds
        ):
    """
    gets list of installed files, searches elfs in them, detects elfs, which
    pointing on garbage elfs

    -b=DIRNAME   - root directory
    -l=FILENAME  - log
    -g           - get sources for all found packages
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.package_name_parser
    import wayround_org.aipsetup.client_pkg

    config = adds['config']

    base_dir = '/'
    if '-b' in opts:
        base_dir = opts['-b']

    log = None
    if '-l' in opts:
        log = opts['-l']

    get_sources = '-g' in opts

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        base_dir
        )

    res = system.find_asps_requireing_sos_not_installed_by_asps(False)

    if log:

        t = pprint.pformat(res)
        f = open(log, 'w')
        f.write(t)
        f.close()
        del t
        del f

    errors = False

    ret = 0

    if get_sources:

        for i in res.keys():

            name = \
                wayround_org.aipsetup.package_name_parser.package_name_parse(i)

            if name is None:
                x = "Can't parse as package name: `{}'".format(i)
                logging.error(x)
                f = open("!errors!.txt", 'a')
                f.write("{}\n".format(x))
                f.close()
                errors = True
            else:
                name = name['groups']['name']

                print("    {}".format(name))

                lat = pkg_client.tarballs_latest(name)
                if lat is not None and len(lat) > 0:
                    res = wayround_org.utils.path.select_by_prefered_extension(
                        lat, config
                        )
                    res = wayround_org.aipsetup.client_pkg.get_tarball(
                        res
                        )
                    if not isinstance(res, str):
                        f = open("!errors!.txt", 'a')
                        f.write(
                            "Can't get tarball for package `{}'\n".format(name)
                            )
                        f.close()
                        errors = True
                else:
                    f = open("!errors!.txt", 'a')
                    f.write(
                        "Can't get latest tarball name "
                        "from server for package `{}'\n".format(name)
                        )
                    f.close()
                    errors = True

    if errors:
        ret = 1

    return ret


def clean_find_libtool_la_with_problems(
        command_name, opts, args, adds
        ):
    """
    Search for .la files depending non-existing dependencies

    Search for .la files depending on other non-existing .la files or on absent
    .so files
    """

    import wayround_org.aipsetup.controllers
    import wayround_org.aipsetup.package_name_parser
    import wayround_org.aipsetup.client_pkg

    ret = 0

    config = adds['config']

    base_dir = '/'
    if '-b' in opts:
        base_dir = opts['-b']

    log = None
    if '-l' in opts:
        log = opts['-l']

    host = config['system_settings']['host']
    if '-h' in opts:
        host = str(opts['-h'])

    get_sources = '-g' in opts

    write_remove_script = '-s' in opts

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        base_dir
        )

    res = system.find_libtool_la_with_problems(mute=False, host=host)
    res_for_script = res

    if log:

        t = pprint.pformat(res)
        f = open(log, 'w')
        f.write(t)
        f.close()
        del t
        del f

    pprint.pprint(res)

    errors = False

    if get_sources:

        asp_names = set()

        asps_and_files = system.list_installed_asps_and_their_files(mute=False)
        asps_and_files_list = list(asps_and_files.keys())

        for each in list(res.keys()):
            for each1 in asps_and_files_list:
                if each in asps_and_files[each1]:
                    asp_names.add(each1)

        asp_names = sorted(asp_names)

        pkg_names = set()

        for each in asp_names:
            name = \
                wayround_org.aipsetup.package_name_parser.package_name_parse(
                    each
                    )

            if name is not None:
                pkg_names.add(name['groups']['name'])
            else:
                logging.error("Can't parse ASP name: {}".format(each))

        del(asp_names)

        pkg_names = list(pkg_names)
        pkg_names.sort()

        logging.info(
            "Packages to download: {}. ({} item[s])".format(
                ', '.join(pkg_names),
                len(pkg_names)
                )
            )

        for name in pkg_names:
            print("    {}".format(name))
            lat = pkg_client.tarballs_latest(name)
            if lat is not None and len(lat) > 0:
                res = wayround_org.utils.path.select_by_prefered_extension(
                    lat, config
                    )
                res = wayround_org.aipsetup.client_pkg.get_tarball(
                    res
                    )
                if not isinstance(res, str):
                    f = open("!errors!.txt", 'a')
                    f.write(
                        "Can't get tarball for package `{}'\n".format(name)
                        )
                    f.close()
                    errors = True
            else:
                f = open("!errors!.txt", 'a')
                f.write(
                    "Can't get latest tarball name "
                    "from server for package `{}'\n".format(name)
                    )
                f.close()
                errors = True

    if write_remove_script:

        with open('la_remove_script.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('\n')
            f.write('exit 1 # fuse\n')

            for i in sorted(list(res_for_script.keys())):
                f.write("rm '{}'\n".format(i))

            f.write('\n')
            f.write('echo done\n')
            f.write('exit 0\n')

    if errors:
        ret = 1

    return ret


def clean_check_list_of_installed_packages_and_asps_auto(
        command_name, opts, args, adds
        ):
    """
    Searches for packages with more when one asp installed
    """

    import wayround_org.aipsetup.controllers

    config = adds['config']

    logging.info("Working. Please wait, it will be not long...")

    pkg_repo_ctl = \
        wayround_org.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    return pkg_repo_ctl.check_list_of_installed_packages_and_asps_auto()


def pkgdeps_print_asps_asp_depends_on(command_name, opts, args, adds):

    import wayround_org.aipsetup.controllers

    config = adds['config']

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        basedir='/'
        )

    r = system.get_asps_asp_depends_on(args[0], mute=False)

    pprint.pprint(r)

    return 0


def pkgdeps_print_asp_depends(command_name, opts, args, adds):

    import wayround_org.aipsetup.controllers

    ret = 0

    config = adds['config']

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
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

    import wayround_org.aipsetup.controllers

    config = adds['config']

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        basedir='/'
        )

    host, arch = _process_h_and_a_opts_specific(opts, config)

    r = system.get_asps_depending_on_asp(
        args[0],
        mute=False,
        host=host,
        arch=arch
        )

    pprint.pprint(r)

    return 0


def package_check(command_name, opts, args, adds):
    """
    Check package for errors
    """

    # TODO: move it to build commands?

    import wayround_org.aipsetup.controllers

    ret = 0

    file = None

    if len(args) == 1:
        file = args[0]

    if file is None:
        logging.error("Filename required")
        ret = 2

    else:

        asp_pkg = wayround_org.aipsetup.controllers.asp_package(file)

        ret = asp_pkg.check_package()

    return ret


def clean_gen_locale(command_name, opts, args, adds):
    """
    (only root) Generate general unicode locale
    """

    import wayround_org.aipsetup.controllers

    ret = 0

    if os.getuid() != 0:
        logging.error("Only root allowed to use this command")
        ret = 1
    else:

        config = adds['config']

        base_dir = '/'
        if '-b' in opts:
            base_dir = opts['-b']

        pkg_client = \
            wayround_org.aipsetup.controllers.pkg_client_by_config(
                config
                )

        system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
            config,
            pkg_client,
            basedir=base_dir
            )

        host, arch = _process_h_and_a_opts_strict(opts, config)

        ret = system.gen_locale(host=host)

    return ret


def clean_install_etc(command_name, opts, args, adds):
    """
    (only root) Install new clean basic UNICORN /etc files

    use -b=dir for changing target root directory
    """

    ret = 0

    '''
    # NOTE: necesserity of such measure is questionabe
    if os.getuid() != 0:
        logging.error("Only root allowed to use this command")
        ret = 1
    else:
    '''
    if True:
        base_dir = '/'
        if '-b' in opts:
            base_dir = opts['-b']

        # TODO: move to system.py?
        # TODO: do over config, not constant

        src_etc_dir = wayround_org.utils.path.join(
            os.path.dirname(__file__),
            'distro',
            'etc',
            'etc.tar.xz'
            )

        ret = wayround_org.utils.archive.extract_tar_canonical(
            src_etc_dir,
            base_dir,
            'xz',
            verbose_tar=True,
            verbose_compressor=True,
            add_tar_options=[
                '--no-same-owner',
                '--no-same-permissions'
                ]
            )

    return ret


def clean_sys_users(command_name, opts, args, adds):
    """
    (only root) Creates system users and their directories under /daemons
    """

    import wayround_org.aipsetup.sysuser

    ret = 0

    if os.getuid() != 0:
        logging.error("Only root allowed to use this command")
        ret = 1
    else:

        config = adds['config']

        base_dir = '/'
        if '-b' in opts:
            base_dir = opts['-b']

        # TODO: find and fix everywhere config['system_paths']['daemons']
        daemons_dir = wayround_org.aipsetup.system.DAEMONS_DIR

        ret = wayround_org.aipsetup.sysuser.sys_users(base_dir, daemons_dir)

    return ret


def clean_sys_perms(command_name, opts, args, adds):
    """
    (only root) Ensures system files and dirs permissions
    """

    import wayround_org.aipsetup.sysuser

    ret = 0

    if os.getuid() != 0:
        logging.error("Only root allowed to use this command")
        ret = 1
    else:

        base_dir = '/'
        if '-b' in opts:
            base_dir = opts['-b']

        chroot = ['chroot', '--userspec=0:0', base_dir]

        ret = wayround_org.aipsetup.sysuser.sys_perms(chroot)

    return ret


def info_parse_pkg_name(command_name, opts, args, adds):
    """
    Parse package name

    NAME
    """

    import wayround_org.aipsetup.package_name_parser

    ret = 0

    if len(args) != 1:
        logging.error("File name required")
        ret = 1
    else:

        filename = args[0]

        p_re = wayround_org.aipsetup.package_name_parser.package_name_parse(
            filename
            )

        if p_re is None:
            ret = 2
        else:
            pprint.pprint(p_re)

    return ret


def info_parse_tarball(command_name, opts, args, adds):

    import wayround_org.aipsetup.controllers
    import wayround_org.utils.tarball

    config = adds['config']

    tarball = None

    ret = 0

    if len(args) != 1:
        logging.error("Tarball name must be supplied")
        ret = 1
    else:

        tarball = args[0]

        parsed = wayround_org.utils.tarball.parse_tarball_name(
            tarball,
            mute=False
            )

        if not parsed:
            logging.error("Can't parse {}".format(tarball))
            ret = 2
        else:

            pprint.pprint(parsed)

            info_ctl = \
                wayround_org.aipsetup.controllers.info_ctl_by_config(config)

            pkg_name = (
                info_ctl.get_package_name_by_tarball_filename(tarball)
                )

            print("Package name: {}".format(pkg_name))

    return ret


def system_replica_instruction(command_name, opts, args, adds):

    print("""\
--
This instruction provids information on how to replicate current
Lailalo system core to other filesystem partition.
--

 => TARGET SYSTEM PARTITION TABLES PREPERATIONS <=

    1. Create partition table. You can use cfdisk if You want msdos (old) style
       MBR table. To manipulate GPT (modern) tables, You can use fdisk or
       parted. syslinux (extlinux) can be used in both cases. GRUB2 recommended
       to be used with GPT, not with msdos MBR!

    2. Install bootloader.

        `grub-install --boot-directory=/mnt/sdb2/boot /dev/sdb`

 => CORE ELEMENTS PREPERATIONS <=

    3. Use command `aipsetup3 sys-replica maketree /mnt/sdb2` to create needed
       directories in pointed path. (/mnt/sdb2 here and farther in this text -
       is path to mounted root of new future system)

    4. Locate already built core components or download them using command:

        `aipsetup pkg-client get-by-list core`

       or get sources

        `aipsetup pkg-client-src get-by-list core`

       and build them

    5. Install core packages:

        `aipsetup sys install -b=/mnt/sdb2 *.asp`

    6. Install /etc structure (default setting for shells, PAM and other basic
       system components)

        `aipsetup sys-clean install-etc -b=/mnt/sdb2`

    7. Install en_US.UTF-8 locale:

        `aipsetup sys-clean gen-locale -b=/mnt/sdb2`

    8. Use commands:

        `aipsetup sys-clean sys-users -b=/mnt/sdb2`
        `aipsetup sys-clean sys-perms -b=/mnt/sdb2`

        to install system users and correct permissions on executables and
        directories.

 => THE LAST THING TO DO <=

    9. chroot to new system and do passwd for root user.

--
That's it! Basic system should be installed by now.

Remember not to use root as Your primary profile. Create a user profile for
Your self.
""")

    return 0


def system_replica_make_installation_flashdrive(
        command_name, opts, args, adds):

    import wayround_org.aipsetup.bootimage

    ret = wayround_org.aipsetup.bootimage.create_flashdrive_image('.')

    return ret


def system_convert_certdata_txt(command_name, opts, args, adds):
    ret = 0

    import wayround_org.aipsetup.system

    filename = None
    if len(args) != 1:
        print("(only) filename must be passed")
        ret = 1
    else:
        filename = args[0]

    if ret == 0:
        res = wayround_org.aipsetup.system.convert_certdata_txt_for_system(
            filename
            )
        f = open('cert.pem.tmp', 'wb')
        f.write(res)
        f.close()

        print(
            "'cert.pem.tmp' written."
            " copy it into /etc/ssl and rename as 'cert.pem'\n"
            " (NOTE: some sources tells it should be named 'ca-bundle.crt')"
            )

    return ret


def docbook_instruction(command_name, opts, args, adds):
    import wayround_org.aipsetup.docbook
    print(wayround_org.aipsetup.docbook.INSTRUCTION)
    return 0


def docbook_install(command_name, opts, args, adds):
    import wayround_org.aipsetup.docbook
    wayround_org.aipsetup.docbook.install()
    return 0


def system_snapshot_create(command_name, opts, args, adds):

    import wayround_org.aipsetup.controllers

    ret = 0

    config = adds['config']

    pkg_client = \
        wayround_org.aipsetup.controllers.pkg_client_by_config(
            config
            )

    system = wayround_org.aipsetup.controllers.sys_ctl_by_config(
        config,
        pkg_client,
        '/'
        )

    snapshot_struct = collections.OrderedDict([
        ('info', {
            'timestamp': None
            }),
        ('asps', [])
        ])

    res = system.list_installed_asps(host=None, remove_extensions=True)

    if res is None:
        ret = 1
    else:
        snapshot_struct['asps'] = res
        snapshot_struct['info']['timestamp'] = \
            wayround_org.utils.time.currenttime_stamp()

        filename = '{}.json'.format(snapshot_struct['info']['timestamp'])

        with open(filename, 'w') as f:
            f.write(json.dumps(snapshot_struct, indent=2))

        logging.info("Saved to {}".format(filename))

    return ret
