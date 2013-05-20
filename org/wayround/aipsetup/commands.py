
import os.path
import logging

import org.wayround.utils.path

def commands():
    return {
    '_order': [
        ],

    'build': {
        'build': build_build
        },

    'bsite': {
        'init': building_site_init
        },

    'server': {},
    'client': {},

    'pkg': {
        },

    'system': {
        '_help': 'System actions: install, uninstall, etc...',
        'install_package': system_install_package,
        },

    'pkg_repo': {},
    'src_repo': {},
    'info_repo': {},
    'build_repo': {},

    'test': {
        'test': test_test
        }

    }


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

    ret = org.wayround.utils.opts.is_wrong_opts(
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

            for name in names:
                ret = install_package(
                    name, force, basedir
                    )
                if ret != 0:
                    logging.error("Failed to install package: `{}'".format(name))
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


def package_list(config, opts, args):
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
        lst = list_installed_packages(mask, basedir)

        lst.sort()

        org.wayround.utils.text.columned_list_print(
            lst, fd=sys.stdout.fileno()
        )

    return ret

def package_list_asps(config, opts, args):
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

            lst = list_installed_package_s_asps(name, basedir)

            lst.sort(
                reverse=True,
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    )
                )

            for i in lst:
                print("    {}".format(i))

    return ret

def package_list_files(config, opts, args):

    ret = 0

    return ret

def package_remove(config, opts, args):
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
        ret = remove_package(name, force, basedir)

        org.wayround.aipsetup.sysupdates.all_actions()

    return ret

def package_complete(config, opts, args):
    """
    Complete package building process: build complete; pack complete

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

    -d - remove buildingsite on success
    """

    dirname = '.'
    file = None

    r_bds = '-d' in opts


    ret = 0

    args_l = len(args)

    if args_l == 0:

        dirname = '.'
        file = None

        ret = complete(
            dirname, file, remove_buildingsite_after_success=r_bds
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

            ret = complete(
                dirname, file, remove_buildingsite_after_success=r_bds
                )

    elif args_l == 2:

        if os.path.isdir(args[0]) and os.path.isfile(args[1]):

            dirname = args[0]
            file = args[1]

            ret = complete(
                dirname, file, remove_buildingsite_after_success=r_bds
                )

        elif os.path.isdir(args[0]) and os.path.isdir(args[1]):

            file = None
            ret = 0
            for i in args[:2]:
                if complete(
                    i, file, remove_buildingsite_after_success=r_bds
                    ) != 0:

                    ret += 1

        else:
            logging.error("Wrong arguments")


    elif args_l > 2:

        file = None

        ret = 0
        for i in args[2:]:
            if complete(i, file, remove_buildingsite_after_success=r_bds) != 0:
                ret += 1

    else:
        raise Exception("Programming error")

    return ret

def build_build(config, opts, args):
    """
    Place named source files in new building site and build new package from them

    [-d] [-o] TARBALL[, TARBALL[, TARBALL[, TARBALL...]]]

    ======= ====================================
    options meaning
    ======= ====================================
    -d      remove building site on success
    -o      treat all tarballs as for one build
    ======= ====================================
    """

    r_bds = '-d' in opts

    sources = []

    multiple_packages = not '-o' in opts

    ret = 0

    if len(args) > 0:
        sources = args

    if len(sources) == 0:
        logging.error("No source files named")
        ret = 2

    if ret == 0:

        if multiple_packages:
            sources.sort()
            for i in sources:
                build([i], remove_buildingsite_after_success=r_bds)
            ret = 0
        else:
            ret = build(sources, remove_buildingsite_after_success=r_bds)

    return ret

def package_find_files(config, opts, args):
    """
    Looks for LOOKFOR in all installed packages using one of methods:

    [-b=DIRNAME] [-m=beg|re|plain|sub|fm] LOOKFOR

    ================ ===================================
    -m option values meanings
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

    ret = find_file_in_files_installed_by_asps(
        basedir, lookfor, mode=look_meth
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

def package_check_package(config, opts, args):
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

        ret = check_package(file)

    return ret

def package_asp_reduce_to_latest(config, opts, args):
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
            package_name_parsed = org.wayround.aipsetup.name.package_name_parse(asp_name)
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

                asp_name_latest = (
                    org.wayround.aipsetup.package.latest_installed_package_s_asp(
                        package_name,
                        destdir
                        )
                    )

                reduce_asps(asp_name_latest, [asp_name], destdir)

    return ret

def package_make_asp_deps(config, opts, args):

    ret = 0

    destdir = '/'

    if '-b' in opts:
        destdir = opts['-b']

    if len(args) != 1:
        logging.error("Must be exactly one argument")
        ret = 1
    else:

        asp_name = args[0]

        ret = make_asp_deps(destdir, asp_name, mute=False)

    return ret


def repoman_scan_creating_templates(opts, args):
    """
    Perform scan and templates creation
    """

    ret = 0

    if repoman_scan_repo_for_pkg_and_cat(
        opts={}, args=[]
        ) != 0:

        ret = 1

    else:

        if repoman_find_missing_pkg_info_records(
            opts={'-t': None}, args=[]
            ) != 0:

            ret = 2

        else:

            if repoman_load_package_info_from_filesystem(
                opts={}, args=[]
                ) != 0:

                ret = 3

    return ret


def repoman_scan_repo_for_pkg_and_cat(opts, args):
    """
    Scan repository and save it's categories and packages indexes
    to database
    """

    ret = 0

    res = org.wayround.aipsetup.pkgindex.scan_repo_for_pkg_and_cat()

    if not isinstance(res, dict):
        ret = 1
    else:
        res2 = org.wayround.aipsetup.clean.detect_package_collisions(
            res['cats'],
            res['packs']
            )

        if res2 != 0:
            ret = 2
        else:

            res3 = org.wayround.aipsetup.pkgindex.save_cats_and_packs_to_db(
                res['cats'],
                res['packs']
                )

            if res3 != 0:
                ret = 2

    return ret


def repoman_index_sources(opts, args):
    """
    Create sources and repositories indexes

    [-f] [SUBDIR]

    -d - before saving delete all found files from index
    -f - force reindexation of already indexed files

    SUBDIR - index only one of subderictories
    """
    ret = 0
    subdir_name = org.wayround.utils.path.realpath(
        org.wayround.utils.path.abspath(
                org.wayround.aipsetup.config.config['source']
            )
        )

    first_delete_found = '-d' in opts
    force_reindex = '-f' in opts

    if len(args) > 1:
        logging.error("Wrong argument count: can be only one")
        ret = 1
    else:

        if len(args) > 0:
            subdir_name = args[0]
            subdir_name = org.wayround.utils.path.realpath(org.wayround.utils.path.abspath(subdir_name))

        if (
            not (
                org.wayround.utils.path.realpath(
                    org.wayround.utils.path.abspath(subdir_name)
                    ) + '/'
                 ).startswith(
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(
                            org.wayround.aipsetup.config.config['source']
                            )
                        ) + '/'
                    )
            or not os.path.isdir(org.wayround.utils.path.abspath(subdir_name))
            ):
            logging.error("Not a subdir of pkg_source")
            logging.debug(
"""\
passed: {}
config: {}
exists: {}
""".format(
                    org.wayround.utils.path.realpath(org.wayround.utils.path.abspath(subdir_name)),
                    org.wayround.utils.path.realpath(
                        org.wayround.utils.path.abspath(
                            org.wayround.aipsetup.config.config['source']
                            )
                        ),
                    os.path.isdir(subdir_name)
                    )
                )
            ret = 2

        else:
            ret = org.wayround.aipsetup.pkgindex.index_sources(
                org.wayround.utils.path.realpath(subdir_name),
                force_reindex=force_reindex,
                first_delete_found=first_delete_found
                )

    return ret

def repoman_latest_editor(opts, args):

    ret = 0

    name = None
    len_args = len(args)
    if len_args == 0:
        pass
    elif len_args == 1:
        name = args[0]
    else:
        ret = 1

    if ret == 0:
        org.wayround.aipsetup.pkglatest.latest_editor(name)

    return ret

def repoman_find_missing_pkg_info_records(opts, args):
    """
    Search packages which have no corresponding info records

    [-t] [-f]

    -t creates non-existing .json file templates in info dir

    -f forces rewrite existing .json files
    """

    ret = 0

    t = '-t' in opts

    f = '-f' in opts

    try:
        org.wayround.aipsetup.pkginfo.get_missing_info_records_list(t, f)
    except:
        logging.exception("Error while searching for missing records")
        ret = 1
    else:
        ret = 0

    return ret

def repoman_find_outdated_pkg_info_records(opts, args):
    """
    Finds pkg info records which differs to FS .json files
    """
    ret = 0

    try:
        res = org.wayround.aipsetup.pkginfo.get_outdated_info_records_list(
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

def repoman_update_outdated_pkg_info_records(opts, args):
    """
    Loads pkg info records which differs to FS .json files
    """

    org.wayround.aipsetup.pkginfo.update_outdated_pkg_info_records()

    return 0

def repoman_delete_pkg_info_records(opts, args):
    """
    mask must be given or operation will fail

    MASK
    """
    mask = None

    ret = 0

    if len(args) > 0:
        mask = args[0]

    if mask != None:
        ret = org.wayround.aipsetup.pkginfo.delete_info_records(mask)
    else:
        logging.error("Mask is not given")
        ret = 1

    return ret

def repoman_backup_package_info_to_filesystem(opts, args):
    """
    Save package information from database to info directory.

    [-f] [MASK]

    Existing files are skipped, unless -f is set
    """
    mask = '*'

    if len(args) > 0:
        mask = args[0]

    force = '-f' in opts

    ret = org.wayround.aipsetup.pkginfo.save_info_records_to_fs(mask, force)

    return ret

def repoman_load_package_info_from_filesystem(opts, args):
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
                org.wayround.aipsetup.config.config['info'] +
                os.path.sep +
                '*'
                )
            )
    else:
        filenames = copy.copy(args)

    rewrite_all = '-a' in opts


    org.wayround.aipsetup.pkginfo.load_info_records_from_fs(
        filenames, rewrite_all
        )

    return ret

def repoman_list_pkg_info_records(opts, args):
    """
    List records containing in index

    [FILEMASK]

    Default MASK is *
    """
    mask = '*'

    if len(args) > 0:
        mask = args[0]

    org.wayround.aipsetup.pkginfo.get_info_records_list(mask)

    return 0

def repoman_print_pkg_info_record(opts, args):
    """
    Print package info record information
    """

    ret = 0

    name = None

    if len(args) > 0:
        name = args[0]

    if name != None:

        ret = org.wayround.aipsetup.pkginfo.print_info_record(name)

    else:
        logging.error("Name is not given")
        ret = 1

    return ret

def repoman_load_tags(opts, args):

    org.wayround.aipsetup.pkgtag.load_tags_from_fs()

    return 0

def repoman_save_tags(opts, args):

    org.wayround.aipsetup.pkgtag.save_tags_to_fs()

    return 0


def repoman_put_asps_to_index(opts, args):
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
        ret = org.wayround.aipsetup.pkgindex.put_asps_to_index(files, move=move)

    return ret

def info_list_files(opts, args, typ='info', mask='*.json'):
    """
    List XML files in pkg_info dir of UNICORN dir

    [FILEMASK]

    One argument is allowed - FILEMASK, which defaults to '\*.json'

    example:
    aipsetup info list '\*doc\*.json'
    """

    args_l = len(args)

    if args_l > 1:
        logging.error("Too many arguments")
    else:

        if args_l == 1:
            mask = args[0]

        lst = glob.glob(
            org.wayround.aipsetup.config.config[typ] + os.path.sep + mask
            )

        for i in range(len(lst)):
            lst[i] = os.path.basename(lst[i])[:-5]

        lst.sort()

        print(
            org.wayround.utils.text.return_columned_list(
                lst
                )
            )

    return 0

def info_edit_file(opts, args, typ='info'):
    """
    Edit selected info-file in editor designated in aipsetup.conf

    FILENAME

    One argument required - FILENAME
    """
    ret = 0
    if len(args) != 1:
        logging.error("file to edit not specified")
        ret = 1
    else:
        ret = org.wayround.utils.edit.edit_file(
            os.path.join(
                org.wayround.aipsetup.config.config[typ],
                args[0]
                ),
            org.wayround.aipsetup.config.config['editor']
            )
    return ret

def info_editor(opts, args):
    """
    Start special info-file editor
    """
    import org.wayround.aipsetup.infoeditor

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

            pkg_name = (
                org.wayround.aipsetup.pkginfo.get_package_name_by_tarball_filename(file_name)
                )

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
        org.wayround.aipsetup.infoeditor.main(file_name)

    return ret

def info_copy(opts, args):
    """
    Creates a copy of one info file into another

    OLDNAME NEWNAME
    """
    if len(args) != 2:
        logging.error("wrong argument count")
    else:

        org.wayround.utils.file.inderictory_copy_file(
            org.wayround.aipsetup.config.config['info'],
            args[0],
            args[1]
            )

    return 0


def info_mass_script(opts, args):
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


        for i in sources:

            pkg_name = (
                org.wayround.aipsetup.pkginfo.get_package_name_by_tarball_filename(i)
                )

            if not pkg_name:
                logging.error("Could not find package name of `{}'".format(i))
                ret = 4
            else:

                info_dir = org.wayround.aipsetup.config.config['info']

                p1 = info_dir + os.path.sep + pkg_name + '.json'

                info = read_from_file(p1)

                if not isinstance(info, dict):
                    logging.error("Wrong info {}".format(p1))
                    ret = 5
                else:

                    if force or info['buildscript'] == '':
                        info['buildscript'] = script_name

                        write_to_file(p1, info)

                        logging.info("Applied to {}".format(pkg_name))
                    else:
                        logging.warning(
                            "{} already have defined script".format(
                                pkg_name
                                )
                            )


        org.wayround.aipsetup.pkginfo.update_outdated_pkg_info_records()

    return ret

def name_parse_package(opts, args):
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

        p_re = package_name_parse(filename, mute=False)

        if p_re == None:
            ret = 2

    return ret



def name_parse_name(opts, args):
    """
    Parse name

    [-w] NAME

    if -w is set - change <name>.json info file nametype value to
    result
    """

    ret = 0

    if len(args) != 1:
        logging.error("File name required")
        ret = 1
    else:

        filename = args[0]

        packagename = (
            org.wayround.aipsetup.pkginfo.get_package_name_by_tarball_filename(
                filename,
                mute=False
                )
            )

        print("Package name is: {}".format(packagename))

    return ret


def name_parse_test(args, opts):
    """
    Test Name Parsing Facilities
    """
    parse_test()
    return 0

def building_site_init(config, opts, args):
    """
    Initiate new building site dir, copying spplyed tarballs to 00.TARBALLS

    [DIRNAME] [TARBALL [TARBALL [TARBALL ...]]]
    """

    import org.wayround.aipsetup.buildingsite

    init_dir = '.'

    if len(args) > 0:
        init_dir = args[0]

    files = None
    if len(args) > 1:
        files = args[1:]


    bs = org.wayround.aipsetup.buildingsite.BuildingSite(init_dir)
    ret = bs.init(files)

    return ret

def buildingsite_apply_info(opts, args):
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

    ret = apply_info(dirname, file)

    return ret
