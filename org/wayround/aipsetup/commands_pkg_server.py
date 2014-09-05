
import collections
import copy
import glob
import logging
import os.path

import org.wayround.aipsetup.controllers
import org.wayround.aipsetup.info
import org.wayround.utils.path
import org.wayround.utils.tarball


def commands():
    return collections.OrderedDict([
        ('pkg-server', collections.OrderedDict([
            ('start', pkg_server_start),
            ])),
        ('pkg-server-info', collections.OrderedDict([
            ('save', info_backup_package_info_to_filesystem),
            ('load', info_load_package_info_from_filesystem),
            ('missing', info_find_missing_pkg_info_records),
            ('outdated', info_find_outdated_pkg_info_records),
            ('update', info_update_outdated_pkg_info_records),
            ('delete', info_delete_pkg_info_records),
            ('editor', info_editor),
            ('mass-apply', info_mass_script_apply)
            ])),
        ('pkg-server-repo', collections.OrderedDict([
            ('index', pkg_repo_index_and_update),
            ('put', pkg_repo_put_file),
            ('put-bundle', pkg_repo_put_bundle),
            ('clean', pkg_repo_cleanup)
            ]))
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

    load_info_tags(command_name, {}, [], adds)

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

    save_info_tags(command_name, {}, [], adds)

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
                    config['pkg_server']['info_json_dir'],
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

    load_info_tags(command_name, {}, [], adds)

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


def info_mass_script_apply(command_name, opts, args, adds):
    """
    Mass buildscript applience

    scriptname [-i=subpath] [-f] [tarballs list]

    -f    force (by default new script name will not be applied to
          records with existing ones)

    -i=subpath
          create package section in repository under pointed subpath
    """

    config = adds['config']

    ret = 0

    sources = []

    force = '-f' in opts

    subpath = None
    if '-i' in opts:
        subpath = opts['-i']

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

        known_names = set()
        exts = \
            config['pkg_server']['acceptable_src_file_extensions'].split(' ')

        sources.sort()

        # TODO: rework next
        for i in sources:

            cont = True
            for j in exts:
                if i.endswith(j):
                    cont = False
                    break

            if cont:
                continue

            pkg_name = info_ctl.get_package_name_by_tarball_filename(i)
            parsed_name = org.wayround.utils.tarball.\
                parse_tarball_name(i, mute=True)

            if not parsed_name:
                logging.error("Error parsing tarball name `{}'".format(i))

            parsed_name = parsed_name['groups']['name']
            if parsed_name.isspace() or len(parsed_name) == 0:
                logging.error("Empty package names are not allowed")
                continue

            if parsed_name in known_names:
                continue

            known_names.add(parsed_name)

            if len(pkg_name) != 1:
                name = pkg_name[0]
                logging.error(
                    "Could not determine package name for base `{}'".format(i)
                    )
                if not subpath:
                    ret = 4
                else:
                    logging.info(
                        "Adding `{}' to repository".format(parsed_name)
                        )
                    total_pkg_path = org.wayround.utils.path.join(
                        config['pkg_server']['repository_dir'],
                        subpath,
                        parsed_name
                        )
                    try:
                        os.makedirs(total_pkg_path)
                    except:
                        pass

                    f = open(
                        org.wayround.utils.path.join(
                            total_pkg_path, '.package'
                            ),
                        'w'
                        )
                    f.write('')
                    f.close()

                    try:
                        os.makedirs(
                            org.wayround.utils.path.join(
                                total_pkg_path, 'pack'
                                )
                            )
                    except:
                        pass

            else:

                info_dir = config['pkg_server']['info_json_dir']

                p1 = org.wayround.utils.path.join(
                    info_dir,
                    name + '.json'
                    )

                info = org.wayround.aipsetup.info.read_info_file(p1)

                if not isinstance(info, dict):
                    logging.error("Wrong info {}".format(p1))
                    ret = 5
                else:

                    if force or info['buildscript'] == '':
                        info['buildscript'] = script_name

                        org.wayround.aipsetup.info.write_info_file(p1, info)

                        logging.info("Applied to {}".format(name))
                    else:
                        logging.warning(
                            "{} already have defined script".format(
                                name
                                )
                            )

        pkg_repo_index_and_update(command_name, opts, args, adds)

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
    Copy package to package server index repository

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


def pkg_repo_put_bundle(command_name, opts, args, adds):
    """
    Set bundle to package server
    """

    config = adds['config']

    ret = 0

    files = []
    if len(args) > 0:
        files = args[:]

    if len(files) == 0:
        logging.error("Filenames required")
        ret = 2
    else:

        bundles_ctl = \
            org.wayround.aipsetup.controllers.bundles_ctl_by_config(config)

        for i in args:

            bn = os.path.basename(i)

            f = open(i)
            t = f.read()
            f.close()

            bundles_ctl.set(bn, t)

    return ret
