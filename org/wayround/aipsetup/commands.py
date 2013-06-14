
import copy
import datetime
import functools
import glob
import logging
import os.path
import pprint
import shlex
import sys

import org.wayround.aipsetup.classes
import org.wayround.aipsetup.info
import org.wayround.aipsetup.sysupdates
import org.wayround.aipsetup.version
import org.wayround.aipsetup.package_name_parser
import org.wayround.aipsetup.infoeditor


import org.wayround.utils.path
import org.wayround.utils.getopt
import org.wayround.utils.log
import org.wayround.utils.time

def commands():
    return {

    'config': {
        'init': config_init
        },

    'build': {
        'full': build_full,
        'build': build_build,
        'build+': build_script,
        'pack': build_pack,
        'complete': build_complete
        },

    'pkg': {
        'check':package_check,
        },

    'bsite': {
        'init': building_site_init,
        'apply': building_site_apply_info
        },

    'server': {
        'start': server_start_host,
        },
    'client': {},

    'info': {
        'editor': info_editor,
        'delete': info_delete_pkg_info_records,
        'save': info_backup_package_info_to_filesystem,
        'load': info_load_package_info_from_filesystem,
        'list': info_list_pkg_info_records,
        'missing': info_find_missing_pkg_info_records,
        'outdated': info_find_outdated_pkg_info_records,
        'update': info_update_outdated_pkg_info_records,
        'print': info_print_pkg_record,
        'save_tags': save_info_tags,
        'load_tags': load_info_tags,
        'script': info_mass_script_apply,
        'parse': info_parse_pkg_name,
        'parse_tar': info_parse_tarball
        },

    'sys': {
        '_help': 'SystemCtl actions: install, uninstall, etc...',
        'list': system_package_list,
        'lista': system_package_list_asps,
        'install': system_install_package,
        'remove': system_remove_package,
        'reduce': system_reduce_asp_to_latest,
        'find': system_find_package_files,
        'generate_deps': system_make_asp_deps,
        'files': system_list_package_files
        },

    'sys_clean': {
        'find_broken': clean_packages_with_broken_files,
        'elf_readiness': clean_check_elfs_readiness,
        'so_problems': clean_find_so_problems,
        'find_old': clean_find_old_packages,
        'explicit_asps': clean_check_list_of_installed_packages_and_asps_auto,
        'find_garbage': clean_find_garbage,
        'find_invalid_deps_lists':clean_find_invalid_deps_lists
        },

    'sys_deps': {
        'asps_asp_depends_on': pkgdeps_print_asps_asp_depends_on,
        'asp_depends': pkgdeps_print_asp_depends,
        'asps_depending_on_asp':pkgdeps_print_asps_depending_on_asp,
        },

    'repo': {
        'index': pkg_repo_index_and_update,
        'put': pkg_repo_put_file,
        'clean': pkg_repo_cleanup,
        },

    'src': {
        'index': src_repo_index,
        'search': src_find_name,
        'paths': src_get_paths
        }

    }

def config_init(config, opts, args):

    import org.wayround.aipsetup.config

    org.wayround.aipsetup.config.save_config(
        org.wayround.aipsetup.config.DEFAULT_CONFIG
        )

    return 0


def test_test(config, opts, args):

    """
    Test documentation

    123
    """

    print("""\
config: {}

opts: {}

args: {}
""".format(config, opts, args))

    return 0


def system_install_package(config, opts, args):
    """
    Install package(s)

    [-b=DIRNAME] [--force] NAMES

    If -b is given - it is used as destination root
    """

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

            pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

            info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

            syst = org.wayround.aipsetup.classes.sys_ctl(
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


def system_package_list(config, opts, args):
    """
    List installed packages

    [-b=DIRNAME] MASK

    -b is same as in install
    """

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

        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)
        pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

        system = org.wayround.aipsetup.classes.sys_ctl(
            config, info_ctl, pkg_repo_ctl, basedir
            )

        lst = system.list_installed_packages(mask)

        lst.sort()

        org.wayround.utils.text.columned_list_print(
            lst, fd=sys.stdout.fileno()
            )

    return ret

def system_package_list_asps(config, opts, args):
    """
    List installed package's ASPs

    [-b=DIRNAME] NAME

    -b is same as in install
    """

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

            info_ctl = org.wayround.aipsetup.classes.info_ctl(config)
            pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

            system = org.wayround.aipsetup.classes.sys_ctl(
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

def system_list_package_files(config, opts, args):

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

        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)
        pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

        system = org.wayround.aipsetup.classes.sys_ctl(
            config, info_ctl, pkg_repo_ctl, basedir
            )

        latest = system.latest_installed_package_s_asp(pkg_name)

        if latest == None:
            logging.error(
                "Error getting latest installed asp of package `{}'".format(pkg_name)
                )
            ret = 2
        else:
            files = system.list_files_installed_by_asp(latest, mute=True)

            files.sort()
            for i in files:
                print(i)

    return ret

def system_remove_package(config, opts, args):
    """
    Removes package matching NAME.

    [-b=DIRNAME] [--force] NAME

    --force    force removal of packages for which info is not
               available or which is not removable
    """

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

        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

        pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

        system = org.wayround.aipsetup.classes.sys_ctl(
            config,
            info_ctl,
            pkg_repo_ctl,
            basedir
            )

        ret = system.remove_package(name, force, basedir)

        org.wayround.aipsetup.sysupdates.all_actions()

    return ret

def _build_complete_subroutine(
    config,
    host,
    target,
    build,
    dirname,
    file,
    r_bds
    ):

    ret = 0

    const = org.wayround.aipsetup.classes.constitution(
        config,
        host,
        target,
        build
        )

    if const == None:
        ret = 1
    else:

        bs = org.wayround.aipsetup.classes.bsite_ctl(dirname)

        build_ctl = org.wayround.aipsetup.classes.build_ctl(bs)
        pack_ctl = org.wayround.aipsetup.classes.pack_ctl(bs)

        build_script_ctl = org.wayround.aipsetup.classes.bscript_ctl(config)

        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

        ret = bs.complete(
            build_ctl,
            pack_ctl,
            build_script_ctl,
            info_ctl,
            main_src_file=file,
            remove_buildingsite_after_success=r_bds,
            const=const
            )

    return ret

def build_complete(config, opts, args):
    """
    Complete package building process in existing building site

    [DIRNAME] [TARBALL]

    [DIRNAME1] [DIRNAME2] [DIRNAMEn]

    This command has two modes of work:

       1. Working with single dir, which is pointed or not pointed by
          first parameter. In this mode, a tarball can be passed,
          which name will be used to apply new package info to pointed
          dir. By default DIRNAME is \`.\' (current dir)

       2. Working with multiple dirs. In this mode, tarball can't be
          passed.

    options:

    ================ ====================================
    options          meaning
    ================ ====================================
    -d               remove building site on success
    --host=TRIPLET
    --build=TRIPLET
    --target=TRIPLET
    ================ ====================================
    """

    ret = 0

    dirname = '.'
    file = None

    r_bds = '-d' in opts

    host = config['system_settings']['host']
    build = config['system_settings']['build']
    target = config['system_settings']['target']

    if '--host' in opts:
        host = opts['--host']

    if '--build' in opts:
        build = opts['--build']

    if '--target' in opts:
        target = opts['--target']

    args_l = len(args)


    if args_l == 0:

        dirname = '.'
        file = None

        ret = _build_complete_subroutine(
            config,
            host,
            target,
            build,
            dirname,
            file,
            r_bds
            )

    elif args_l == 1:

        if os.path.isdir(args[0]):

            dirname = args[0]
            file = None

        elif os.path.isfile(args[0]):

            dirname = '.'
            file = args[0]

        else:

            logging.error("{} not a dir and not a file".format())
            ret = 2

        if ret == 0:

            ret = _build_complete_subroutine(
                config,
                host,
                target,
                build,
                dirname,
                file,
                r_bds
                )

    elif args_l == 2:

        if os.path.isdir(args[0]) and os.path.isfile(args[1]):

            dirname = args[0]
            file = args[1]

            ret = _build_complete_subroutine(
                config,
                host,
                target,
                build,
                dirname,
                file,
                r_bds
                )

        elif os.path.isdir(args[0]) and os.path.isdir(args[1]):

            file = None
            ret = 0
            for i in args[:2]:

                ret += _build_complete_subroutine(
                    config,
                    host,
                    target,
                    build,
                    i,
                    file,
                    r_bds
                    )

        else:
            logging.error("Wrong arguments")

    elif args_l > 2:

        file = None

        ret = 0
        for i in args[2:]:
            ret += _build_complete_subroutine(
                config,
                host,
                target,
                build,
                i,
                file,
                r_bds
                )

    else:
        raise Exception("Programming error")

    return ret

def build_full(config, opts, args):
    """
    Place named source files in new building site and build new package from them

    [-d] [-o] [--host=HOST-NAME-TRIPLET] TARBALL[, TARBALL[, TARBALL[, TARBALL...]]]

    ================ ====================================
    options          meaning
    ================ ====================================
    -d               remove building site on success
    -o               treat all tarballs as for one build
    --host=TRIPLET
    --build=TRIPLET
    --target=TRIPLET
    ================ ====================================
    """

    r_bds = '-d' in opts

    sources = []

    multiple_packages = not '-o' in opts

    ret = 0

    building_site_dir = config['builder_repo']['building_scripts_dir']

    host = config['system_settings']['host']
    build = config['system_settings']['build']
    target = config['system_settings']['target']

    if len(args) > 0:
        sources = args
        building_site_dir = org.wayround.utils.path.abspath(
            os.path.dirname(sources[0])
            )

    if len(sources) == 0:
        logging.error("No source files supplied")
        ret = 2

    if '--host' in opts:
        host = opts['--host']

    if '--build' in opts:
        build = opts['--build']

    if '--target' in opts:
        target = opts['--target']

    if ret == 0:

        const = org.wayround.aipsetup.classes.constitution(
            config,
            host,
            target,
            build
            )

        if const == None:
            ret = 1
        else:

            if multiple_packages:
                sources.sort()
                for i in sources:
                    org.wayround.aipsetup.build.build(
                        config,
                        [i],
                        remove_buildingsite_after_success=r_bds,
                        buildingsites_dir=building_site_dir,
                        const=const
                        )
                ret = 0
            else:
                ret = org.wayround.aipsetup.build.build(
                    config,
                    sources,
                    remove_buildingsite_after_success=r_bds,
                    buildingsites_dir=building_site_dir,
                    const=const
                    )

    return ret

def build_pack(config, opts, args):
    """
    Fullcircle action set for creating package

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """

    ret = 0

    dir_name = '.'
    args_l = len(args)


    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        bs = org.wayround.aipsetup.classes.bsite_ctl(dir_name)

        packer = org.wayround.aipsetup.classes.pack_ctl(bs)

        ret = packer.complete()

    return ret

def system_find_package_files(config, opts, args):
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
    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    look_meth = 'sub'
    if '-m' in opts:
        look_meth = opts['-m']

    lookfor = ''
    if len(args) > 0:
        lookfor = args[0]


    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)
    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
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

def package_check(config, opts, args):
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

        asp_pkg = org.wayround.aipsetup.classes.asp_package(file)

        ret = asp_pkg.check_package()

    return ret

def system_reduce_asp_to_latest(config, opts, args):
    """
    Forcibly reduces named asp, excluding files installed by latest package's asp

    [-b=DESTDIR] ASP_NAME
    """

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

                info_ctl = org.wayround.aipsetup.classes.info_ctl(config)
                pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

                system = org.wayround.aipsetup.classes.sys_ctl(
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

def system_make_asp_deps(config, opts, args):
    """
    generates dependencies listing for named asp and places it under
    /destdir/var/log/packages/deps
    """

    ret = 0

    destdir = '/'

    if '-b' in opts:
        destdir = opts['-b']

    if len(args) != 1:
        logging.error("Must be exactly one argument")
        ret = 1
    else:

        asp_name = args[0]

        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)
        pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

        system = org.wayround.aipsetup.classes.sys_ctl(
            config,
            info_ctl,
            pkg_repo_ctl,
            destdir
            )

        ret = system.make_asp_deps(asp_name, mute=False)

    return ret


def pkg_repo_index_and_update(config, opts, args):
    """
    Perform scan and templates creation
    """

    ret = 0

    if package_repository_index(
        config, opts={}, args=[]
        ) != 0:

        ret = 1

    else:

        if info_find_missing_pkg_info_records(
            config, opts={'-t': None}, args=[]
            ) != 0:

            ret = 2

        else:

            if info_load_package_info_from_filesystem(
                config, opts={}, args=[]
                ) != 0:

                ret = 3

    return ret


def package_repository_index(config, opts, args):
    """
    Scan repository and save it's categories and packages indexes
    to database
    """

    ret = 0

    pkgindex = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    res = pkgindex.scan_repo_for_pkg_and_cat()

    if not isinstance(res, dict):
        ret = 1
    else:
        res2 = pkgindex.detect_package_collisions(
            res['cats'],
            res['packs']
            )

        if res2 != 0:
            ret = 2
        else:

            res3 = pkgindex.save_cats_and_packs_to_db(
                res['cats'],
                res['packs']
                )

            if res3 != 0:
                ret = 2

    return ret


def src_repo_index(config, opts, args):
    """
    Create sources and repositories indexes

    [-f] [SUBDIR]


    SUBDIR - index only one of subdirectories

    -f - force reindexing files already in index
    -c - only index clean
    """

    ret = 0

    forced_reindex = '-f' in opts
    clean_only = '-c' in opts

    subdir_name = org.wayround.utils.path.realpath(
        org.wayround.utils.path.abspath(
                config['sources_repo']['dir']
            )
        )


    if len(args) > 1:
        logging.error("Wrong argument count: can be only one")
        ret = 1
    else:

        if len(args) > 0:
            subdir_name = args[0]
            subdir_name = org.wayround.utils.path.realpath(
                org.wayround.utils.path.abspath(subdir_name)
                )

        if (
            not (
                org.wayround.utils.path.realpath(
                    org.wayround.utils.path.abspath(subdir_name)
                    ) + '/'
                 ).startswith(
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(
                            config['sources_repo']['dir']
                            )
                        ) + '/'
                    )
            or not os.path.isdir(org.wayround.utils.path.abspath(subdir_name))
            ):
            logging.error("Not a subdir of pkg_source: {}".format(subdir_name))
            logging.debug(
"""\
passed: {}
config: {}
exists: {}
""".format(
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(subdir_name)
                        ),
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(
                            config['sources_repo']['dir']
                            )
                        ),
                    os.path.isdir(subdir_name)
                    )
                )
            ret = 2

        else:

            src_ctl = org.wayround.aipsetup.classes.src_repo_ctl(config)

            ret = src_ctl.index_sources(
                org.wayround.utils.path.realpath(subdir_name),
                acceptable_src_file_extensions=
                    config['general']['acceptable_src_file_extensions'].split(),
                force_reindex=forced_reindex,
                clean_only=clean_only
                )

    return ret


def info_find_missing_pkg_info_records(config, opts, args):
    """
    Search packages which have no corresponding info records

    [-t] [-f]

    -t creates non-existing .json file templates in info dir

    -f forces rewrite existing .json files
    """

    ret = 0

    t = '-t' in opts

    f = '-f' in opts

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_index_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    try:
        info_ctl.get_missing_info_records_list(pkg_index_ctl, t, f)
    except:
        logging.exception("Error while searching for missing records")
        ret = 1
    else:
        ret = 0

    return ret

def info_find_outdated_pkg_info_records(config, opts, args):
    """
    Finds pkg info records which differs to FS .json files
    """
    ret = 0

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    try:
        res = info_ctl.get_outdated_info_records_list(
            mute=False
            )

    except:
        logging.exception("Error getting outdated info records list")
        ret = 2
        raise

    else:
        if len(res) > 0:
            logging.warning("Total {} warnings".format(len(res)))
        else:
            logging.info("No warnings")

    return ret

def info_update_outdated_pkg_info_records(config, opts, args):
    """
    Loads pkg info records which differs to FS .json files
    """

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    info_ctl.update_outdated_pkg_info_records()

    # TODO: ret is need to be made

    return 0

def info_delete_pkg_info_records(config, opts, args):
    """
    mask must be given or operation will fail

    MASK
    """
    ret = 0

    mask = None

    if len(args) > 0:
        mask = args[0]

    if mask != None:

        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

        ret = info_ctl.delete_info_records(mask)

    else:
        logging.error("Mask is not given")
        ret = 1

    return ret

def info_backup_package_info_to_filesystem(config, opts, args):
    """
    Save package information from database to info directory.

    [-f] [MASK]

    Existing files are skipped, unless -f is set
    """
    mask = '*'

    if len(args) > 0:
        mask = args[0]

    force = '-f' in opts

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    ret = info_ctl.save_info_records_to_fs(mask, force)

    return ret

def info_load_package_info_from_filesystem(config, opts, args):
    """
    Load missing package information from named files

    [-a] [file names]

    If no files listed - assume all files in info dir.

    -a force load all records, not only missing.
    """

    ret = 0

    filenames = []
    if len(args) == 0:
        filenames = (
            glob.glob(
                org.wayround.utils.path.join(
                    config['info_repo']['dir'],
                    '*'
                    )
                )
            )
    else:
        filenames = copy.copy(args)

    rewrite_all = '-a' in opts

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    info_ctl.load_info_records_from_fs(
        filenames, rewrite_all
        )

    return ret

def info_list_pkg_info_records(config, opts, args):
    """
    List records containing in index

    [FILEMASK]

    Default MASK is *
    """
    mask = '*'

    if len(args) > 0:
        mask = args[0]

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    info_ctl.get_info_records_list(mask)

    return 0

def info_print_pkg_record(config, opts, args):
    """
    Print package info record information
    """

    ret = 0

    name = None

    if len(args) > 0:
        name = args[0]

    if name != None:

        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

        pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

        tag_ctl = org.wayround.aipsetup.classes.tag_ctl(config)

        info_ctl.print_info_record(
            name, pkg_repo_ctl, tag_ctl
            )

    else:
        logging.error("Name is not given")
        ret = 1

    return ret

def load_info_tags(config, opts, args):

    tag_ctl = org.wayround.aipsetup.classes.tag_ctl(config)

    tag_ctl.load_tags_from_fs()

    return 0

def save_info_tags(config, opts, args):

    tag_ctl = org.wayround.aipsetup.classes.tag_ctl(config)

    tag_ctl.save_tags_to_fs()

    return 0


def pkg_repo_put_file(config, opts, args):
    """
    Copy package to index repository

    -m      move, not copy
    """

    ret = 0

    move = False
    if '-m' in opts:
        move = True

    files = []
    if len(args) > 0:
        files = args[:]

    if len(files) == 0:
        logging.error("Filenames required")
        ret = 2
    else:

        index = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

        ret = index.put_asps_to_index(files, move=move)

    return ret

def info_editor(config, opts, args):
    """
    Start special info-file editor
    """

    ret = 0

    file_name = None
    len_args = len(args)
    if len_args == 0:
        pass
    elif len_args == 1:
        file_name = args[0]
    else:
        ret = 1

    if ret == 0:

        if isinstance(file_name, str) and os.path.isfile(file_name):


            info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

            pkg_name = (
                info_ctl.get_package_name_by_tarball_filename(file_name)
                )

            del info_ctl

            if not pkg_name:
                logging.error(
                    "Could not find package name of `{}'".format(
                        file_name
                        )
                    )
                ret = 4
            else:
                file_name = pkg_name

        if isinstance(file_name, str):
            if not file_name.endswith('.json'):
                file_name = file_name + '.json'

        org.wayround.aipsetup.infoeditor.main(file_name, config)

    return ret

def info_parse_tarball(config, opts, args):

    tarball = None

    ret = 0

    if len(args) != 1:
        logging.error("Tarball name must be supplied")
        ret = 1
    else:

        tarball = args[0]

        parsed = org.wayround.utils.tarball_name_parser.parse_tarball_name(
            tarball,
            mute=False
            )

        if not parsed:
            logging.error("Can't parse {}".format(tarball))
            ret = 2
        else:

            pprint.pprint(parsed)

            info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

            pkg_name = (
                info_ctl.get_package_name_by_tarball_filename(tarball)
                )

            print("Package name: {}".format(pkg_name))

    return ret


def info_mass_script_apply(config, opts, args):
    """
    Mass buildscript applience

    scriptname [-f] [tarballs list]

    -f    force (by default new script name will not be applied to
          records with existing ones)
    """

    ret = 0

    sources = []

    force = '-f' in opts


    script_name = None

    if len(args) > 0:
        script_name = args[0]

    if len(args) > 1:
        sources = args[1:]

    if script_name == None:
        logging.error("Script name required")
        ret = 3

    if len(sources) == 0:
        logging.error("No source files named")
        ret = 2

    if ret == 0:


        info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

        for i in sources:

            pkg_name = info_ctl.get_package_name_by_tarball_filename(i)

            if not pkg_name:
                logging.error("Could not find package name of `{}'".format(i))
                ret = 4
            else:

                info_dir = config['info_repo']['dir']

                p1 = org.wayround.utils.path.join(
                    info_dir,
                    pkg_name + '.json'
                    )

                info = org.wayround.aipsetup.info.read_info_file(p1)

                if not isinstance(info, dict):
                    logging.error("Wrong info {}".format(p1))
                    ret = 5
                else:

                    if force or info['buildscript'] == '':
                        info['buildscript'] = script_name

                        org.wayround.aipsetup.info.write_info_file(p1, info)

                        logging.info("Applied to {}".format(pkg_name))
                    else:
                        logging.warning(
                            "{} already have defined script".format(
                                pkg_name
                                )
                            )

        info_ctl.update_outdated_pkg_info_records()

    return ret

def info_parse_pkg_name(config, opts, args):
    """
    Parse package name

    NAME
    """

    ret = 0

    if len(args) != 1:
        logging.error("File name required")
        ret = 1
    else:

        filename = args[0]

        p_re = org.wayround.aipsetup.package_name_parser.package_name_parse(
            filename
            )

        if p_re == None:
            ret = 2
        else:
            pprint.pprint(p_re)

    return ret

def building_site_init(config, opts, args):
    """
    Initiate new building site dir, copying spplyed tarballs to 00.TARBALLS

    [DIRNAME] [TARBALL [TARBALL [TARBALL ...]]]
    """

    init_dir = '.'

    if len(args) > 0:
        init_dir = args[0]

    files = None
    if len(args) > 1:
        files = args[1:]


    bs = org.wayround.aipsetup.classes.bsite_ctl(init_dir)
    ret = bs.init(files)

    return ret


def building_site_apply_info(config, opts, args):
    """
    Apply info to building dir

    [DIRNAME [FILENAME]]
    """

    dirname = '.'
    file = None

    if len(args) > 0:
        dirname = args[0]

    if len(args) > 1:
        file = args[1]

    # TODO: add check for dirname correctness
    bs = org.wayround.aipsetup.classes.bsite_ctl(dirname)
    ret = bs.apply_info(file)

    return ret

def build_script(config, opts, args):
    """
    Starts named action from script applied to current building site

    [-b=DIR] action_name

    -b - set building site

    if action name ends with + (plus) all remaining actions will be also started
    (if not error will occur)
    """

    ret = 0

    args_l = len(args)

    if args_l != 1:
        logging.error("one argument must be")
        ret = 1
    else:

        action = args[0]

        dirname = '.'
        if '-b' in opts:
            dirname = opts['-b']

        bs = org.wayround.aipsetup.classes.bsite_ctl(dirname)
        build_ctl = org.wayround.aipsetup.classes.build_ctl(bs)
        script = org.wayround.aipsetup.classes.bscript_ctl(config)
        ret = build_ctl.start_building_script(script, action=action)

    return ret



def build_build(config, opts, args):
    """
    Configures, builds, distributes and prepares software accordingly to info

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """

    ret = 0

    dir_name = '.'
    args_l = len(args)


    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]


        bs = org.wayround.aipsetup.classes.bsite_ctl(dir_name)

        build_ctl = org.wayround.aipsetup.classes.build_ctl(bs)

        buildscript_ctl = org.wayround.aipsetup.classes.bscript_ctl(config)

        ret = build_ctl.complete(buildscript_ctl)

    return ret




#def buildscript_list_files(opts, args):
#    """
#    List building scripts files
#    """
#
#    # TODO: redo
#
#    return org.wayround.aipsetup.info.info_list_files(
#        opts, args, 'buildscript', mask='*.py'
#        )
#
#def buildscript_edit_file(opts, args):
#    """
#    Edit building script
#
#    FILENAME
#    """
#
#    # TODO: redo
#
#    return org.wayround.aipsetup.info.info_edit_file(opts, args, 'buildscript')


def clean_packages_with_broken_files(config, opts, args):

    """
    Find packages with broken files
    """

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
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

def clean_check_elfs_readiness(config, opts, args):

    """
    Performs system ELF files read checks

    This is mainly needed to test aipsetup elf reader, but on the other hand it
    can be used to detect broken elf files.
    """

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    ret = system.check_elfs_readiness()

    return ret

def clean_find_so_problems(config, opts, args):

    """
    Find so libraries missing in system and write package names requiring those
    missing libraries.
    """

    ret = 0

    basedir = '/'
#    if '-b' in opts:
#        basedir = opts['-b']

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
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

def clean_find_old_packages(config, opts, args):

    """
    Find packages older then month
    """

    # TODO: add arguments
    # TODO: must work with basedir!

    ret = 0

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    res = system.find_old_packages()

    res.sort()

    for i in res:
        parsed_name = org.wayround.aipsetup.package_name_parser.package_name_parse(i)

        if not parsed_name:
            logging.warning("Can't parse package name `{}'".format(i))
        else:

            package_date = org.wayround.aipsetup.package_name_parser.parse_timestamp(
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


def pkg_repo_cleanup(config, opts, args):

    """
    Removes old packages from package repository
    """

    # TODO: more descriptive help text required

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    pkg_repo_ctl.cleanup_repo()

    return 0

def clean_check_list_of_installed_packages_and_asps_auto(config, opts, args):

    """
    Searches for packages with more when one asp installed
    """

    logging.info("Working. Please wait, it will be not long...")

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    return pkg_repo_ctl.check_list_of_installed_packages_and_asps_auto()


def pkgdeps_print_asps_asp_depends_on(config, opts, args):

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    r = system.get_asps_asp_depends_on(args[0], mute=False)

    pprint.pprint(r)

    return 0

def pkgdeps_print_asp_depends(config, opts, args):

    ret = 0

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
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


def pkgdeps_print_asps_depending_on_asp(config, opts, args):

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
        config,
        info_ctl,
        pkg_repo_ctl,
        basedir='/'
        )

    r = system.get_asps_depending_on_asp(args[0], mute=False)

    pprint.pprint(r)

    return 0



def server_start_host(config, opts, args):
    """
    Start serving UNICORN Web Host
    """

    import org.wayround.aipsetup.server

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)
    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)
    tag_ctl = org.wayround.aipsetup.classes.tag_ctl(config)

    app = org.wayround.aipsetup.server.AipsetupASPServer(
        config,
        pkg_repo_ctl,
        info_ctl,
        tag_ctl
        )

    app.start()

    return 0

def clean_find_invalid_deps_lists(config, opts, args):

    ret = 0

    basedir = '/'

    if '-b' in opts:
        basedir = opts['-b']

    info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

    pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

    system = org.wayround.aipsetup.classes.sys_ctl(
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

def clean_find_garbage(config, opts, args):

    """
    Search system for garbage making log and cleaning script

    -b=BASENAME        - system root path
    --script-type=bash - system cleaning script language (only bash supported)
    --so               - look only for .so files garbage in /usr/lib directory
    """

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
        basedir = '/'
        script = 'system_garbage_{}.sh'.format(org.wayround.utils.time.currenttime_stamp())
        script_type = 'bash'
        only_lib = False

        if '-b' in opts:
            basedir = opts['-b']

        if '--script-type' in opts:
            script_type = opts['--script-type']

        only_lib = '--so' in opts

        log = org.wayround.utils.log.Log(
            os.getcwd(), 'system_garbage'
            )


        if not script_type in ['bash']:
            logging.error("Invalid --script-type value")
            ret = 1
        else:

            info_ctl = org.wayround.aipsetup.classes.info_ctl(config)

            pkg_repo_ctl = org.wayround.aipsetup.classes.pkg_repo_ctl(config)

            system = org.wayround.aipsetup.classes.sys_ctl(
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
                log.info("Separating garbage .so files to know which packages depending on them")

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

                        file_name_with_dest_dir = org.wayround.utils.path.insert_base(
                            file_name, basedir
                            )

                        if not file_name_with_dest_dir in asps_lkd_to_garbage[asp_name]:
                            asps_lkd_to_garbage[asp_name][file_name_with_dest_dir] = set()

                        asps_lkd_to_garbage[asp_name][file_name_with_dest_dir] |= (set(libs) & set(asp_deps[asp_name][file_name]))

                        if len(asps_lkd_to_garbage[asp_name][file_name_with_dest_dir]) == 0:
                            del asps_lkd_to_garbage[asp_name][file_name_with_dest_dir]

                    if len(asps_lkd_to_garbage[asp_name]) == 0:
                        del asps_lkd_to_garbage[asp_name]


                if script:
                    s = open(script, 'w')

                log.info("Writing report and cleaning script")

                res.sort()

                for i in res:
                    try:
                        log.info("    {}".format(i), echo=False)
                    except:
                        log.error("Error logging {}".format(repr(i)))

                    if script:
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

                if script:
                    s.close()

                logging.warning("""
Do not run cleaning script at once!
Check everything is correct!
Wrong cleaning can ruin your system
"""
                    )

            log.close()

    return ret

def src_find_name(config, opts, args):

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[
                '-r',
                '-s'
                ]
            ) != 0:
        ret = 1

    if ret == 0:

        mode = 'fm'
        mask = '*'
        case_sensetive = False

        if '-r' in opts:
            mode = 're'

        if '-s' in opts:
            case_sensetive = True

        if len(args) > 0:
            mask = args[0]

        logging.info("Loading")

        src_index = org.wayround.aipsetup.classes.src_repo_ctl(config)

        logging.info("Searching")

        names = src_index.find_name(mode, mask, cs=case_sensetive)

        names.sort()

        for i in names:
            print("    {}".format(i))

    return ret


def src_get_paths(config, opts, args):

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[]
            ) != 0:
        ret = 1

    if ret == 0:

        name = None

        if not len(args) == 1:
            ret = 1
            logging.error("One argument required")
        else:
            name = args[0]
            src_index = org.wayround.aipsetup.classes.src_repo_ctl(config)
            objects = src_index.get_name_paths(name)
            objects.sort()
            for i in objects:
                print('    {}'.format(i))

    return ret
