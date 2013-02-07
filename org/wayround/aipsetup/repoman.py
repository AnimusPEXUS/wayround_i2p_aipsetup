
"""
Repository manipulations CLI module
"""

import copy
import glob
import logging
import os.path

import org.wayround.utils.path


import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkglatest
import org.wayround.aipsetup.pkgtag
import org.wayround.aipsetup.clean



def exported_commands():
    return {
        'scan'          : repoman_scan_creating_templates,
        'scan_only'     : repoman_scan_repo_for_pkg_and_cat,
        'index_src'     : repoman_index_sources,
        'latests'       : repoman_latest_editor,
        'missing'       : repoman_find_missing_pkg_info_records,
        'outdated'      : repoman_find_outdated_pkg_info_records,
        'update'        : repoman_update_outdated_pkg_info_records,
        'delete'        : repoman_delete_pkg_info_records,
        'backup'        : repoman_backup_package_info_to_filesystem,
        'load'          : repoman_load_package_info_from_filesystem,
        'list'          : repoman_list_pkg_info_records,
        'print'         : repoman_print_pkg_info_record,
        'loadt'         : repoman_load_tags,
        'savet'         : repoman_save_tags,
        'index'         : repoman_put_asps_to_index
        }

def commands_order():
    return [
        'scan',
        'scan_only',
        'index_src',
        'missing',
        'outdated',
        'update',
        'delete',
        'backup',
        'load',
        'list',
        'print',
        'latests',
        'loadt',
        'savet',
        'index'
        ]

def cli_name():
    return 'repo'

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
