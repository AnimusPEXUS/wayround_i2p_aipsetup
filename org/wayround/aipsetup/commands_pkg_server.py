
import collections
import copy
import glob
import logging
import os.path
import pprint

import org.wayround.aipsetup.controllers
import org.wayround.aipsetup.info
import org.wayround.aipsetup.package_name_parser
import org.wayround.utils.path


def commands():
    return collections.OrderedDict([
        ('pkg_server', {
            'start': pkg_server_start,
            }),

        ('info', {
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
            }),

        ('repo', {
            'index': pkg_repo_index_and_update,
            'put': pkg_repo_put_file,
            'clean': pkg_repo_cleanup,
            'list': pkg_repo_list_categories
            }),

        ])


def pkg_server_start(command_name, opts, args, adds):

    import org.wayround.aipsetup.server_pkg

    return org.wayround.aipsetup.server_pkg.server_start_host(
        command_name, opts, args, adds
        )


def pkg_repo_cleanup(command_name, opts, args, adds):

    """
    Removes old packages from package repository
    """

    config = adds['config']

    # TODO: more descriptive help text required

    pkg_repo_ctl = org.wayround.aipsetup.controllers.\
        pkg_repo_ctl_by_config(config)

    pkg_repo_ctl.cleanup_repo()

    return 0


def info_find_missing_pkg_info_records(command_name, opts, args, adds):

    """
    Search packages which have no corresponding info records

    [-t] [-f]

    -t creates non-existing .json file templates in info dir

    -f forces rewrite existing .json files
    """

    config = adds['config']

    ret = 0

    t = '-t' in opts

    f = '-f' in opts

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    pkg_index_ctl = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

    try:
        info_ctl.get_missing_info_records_list(pkg_index_ctl, t, f)
    except:
        logging.exception("Error while searching for missing records")
        ret = 1
    else:
        ret = 0

    return ret


def info_find_outdated_pkg_info_records(command_name, opts, args, adds):

    """
    Finds pkg info records which differs to FS .json files
    """

    config = adds['config']

    ret = 0

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

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


def info_update_outdated_pkg_info_records(command_name, opts, args, adds):

    """
    Loads pkg info records which differs to FS .json files
    """

    config = adds['config']

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    info_ctl.update_outdated_pkg_info_records()

    # TODO: ret is need to be made

    return 0


def info_delete_pkg_info_records(command_name, opts, args, adds):

    """
    mask must be given or operation will fail

    MASK
    """

    config = adds['config']

    ret = 0

    mask = None

    if len(args) > 0:
        mask = args[0]

    if mask != None:

        info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

        info_ctl.delete_info_records(mask)

    else:
        logging.error("Mask is not given")
        ret = 1

    return ret


def info_backup_package_info_to_filesystem(command_name, opts, args, adds):

    """
    Save package information from database to info directory.

    [-f] [MASK]

    Existing files are skipped, unless -f is set
    """

    config = adds['config']

    mask = '*'

    if len(args) > 0:
        mask = args[0]

    force = '-f' in opts

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    ret = info_ctl.save_info_records_to_fs(mask, force)

    return ret


def info_load_package_info_from_filesystem(command_name, opts, args, adds):

    """
    Load missing package information from named files

    [-a] [file names]

    If no files listed - assume all files in info dir.

    -a force load all records, not only missing.
    """

    config = adds['config']

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

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    info_ctl.load_info_records_from_fs(
        filenames, rewrite_all
        )

    return ret


def info_list_pkg_info_records(command_name, opts, args, adds):

    """
    List records containing in index

    [FILEMASK]

    Default MASK is *
    """

    config = adds['config']

    mask = '*'

    if len(args) > 0:
        mask = args[0]

    info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

    info_ctl.get_info_records_list(mask)

    return 0


def info_print_pkg_record(command_name, opts, args, adds):

    """
    Print package info record information
    """

    config = adds['config']

    ret = 0

    name = None

    if len(args) > 0:
        name = args[0]

    if name != None:

        info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

        pkg_repo_ctl = \
            org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

        tag_ctl = org.wayround.aipsetup.controllers.tag_ctl_by_config(config)

        info_ctl.print_info_record(
            name, pkg_repo_ctl, tag_ctl
            )

    else:
        logging.error("Name is not given")
        ret = 1

    return ret


def info_editor(command_name, opts, args, adds):

    """
    Start special info-file editor
    """

    config = adds['config']

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

            info_ctl = \
                org.wayround.aipsetup.controllers.info_ctl_by_config(config)

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


def info_parse_tarball(command_name, opts, args, adds):

    config = adds['config']

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

            info_ctl = \
                org.wayround.aipsetup.controllers.info_ctl_by_config(config)

            pkg_name = (
                info_ctl.get_package_name_by_tarball_filename(tarball)
                )

            print("Package name: {}".format(pkg_name))

    return ret


def info_mass_script_apply(command_name, opts, args, adds):

    """
    Mass buildscript applience

    scriptname [-f] [tarballs list]

    -f    force (by default new script name will not be applied to
          records with existing ones)
    """

    config = adds['config']

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

        info_ctl = org.wayround.aipsetup.controllers.info_ctl_by_config(config)

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


def info_parse_pkg_name(command_name, opts, args, adds):

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


def load_info_tags(command_name, opts, args, adds):

    config = adds['config']

    tag_ctl = org.wayround.aipsetup.controllers.tag_ctl_by_config(config)

    tag_ctl.load_tags_from_fs()

    return 0


def save_info_tags(command_name, opts, args, adds):

    config = adds['config']

    tag_ctl = org.wayround.aipsetup.controllers.tag_ctl_by_config(config)

    tag_ctl.save_tags_to_fs()

    return 0


def pkg_repo_index(command_name, opts, args, adds):

    """
    Scan repository and save it's categories and packages indexes
    to database
    """

    config = adds['config']

    ret = 0

    pkgindex = \
        org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

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


def pkg_repo_index_and_update(command_name, opts, args, adds):

    """
    Perform scan and templates creation
    """

    ret = 0

    if pkg_repo_index(
        command_name, opts={}, args=[], adds=adds
        ) != 0:

        ret = 1

    else:

        if info_find_missing_pkg_info_records(
            command_name, opts={'-t': None}, args=[], adds=adds
            ) != 0:

            ret = 2

        else:

            if info_load_package_info_from_filesystem(
                command_name, opts={}, args=[], adds=adds
                ) != 0:

                ret = 3

    return ret


def pkg_repo_put_file(command_name, opts, args, adds):

    """
    Copy package to index repository

    -m      move, not copy
    """

    config = adds['config']

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

        index = \
            org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

        ret = index.put_asps_to_index(files, move=move)

    return ret


def pkg_repo_list_categories(command_name, opts, args, adds):

    config = adds['config']

    ret = 0

    if org.wayround.utils.getopt.check_options(
            opts,
            opts_list=[]
            ) != 0:
        ret = 1

    if ret == 0:

        pkg_repo_ctl = \
            org.wayround.aipsetup.controllers.pkg_repo_ctl_by_config(config)

        tree = pkg_repo_ctl.build_category_tree('')

        keys = list(tree.keys())
        keys.sort()

        for i in keys:

            print("{} ::".format(i))

            tree[i].sort()

            for j in tree[i]:
                print("    {}".format(j))

            print()

    return 0
