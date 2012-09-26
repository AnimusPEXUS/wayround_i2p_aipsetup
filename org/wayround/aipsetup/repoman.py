"""
Repository manipulations CLI module
"""

import copy
import glob
import logging
import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkglatest
import org.wayround.aipsetup.pkgtags
import os.path



def exported_commands():
    return {
        'scan': repoman_scan_repo_for_pkg_and_cat,
        'collisions':repoman_find_repository_package_name_collisions_in_database,
        'index_src': repoman_index_sources,
        'latests': repoman_latest_editor,
        'missing': repoman_find_missing_pkg_info_records,
        'outdated': repoman_find_outdated_pkg_info_records,
        'update': repoman_update_outdated_pkg_info_records,
        'delete': repoman_delete_pkg_info_records,
        'backup': repoman_backup_package_info_to_filesystem,
        'load': repoman_load_package_info_from_filesystem,
        'list': repoman_list_pkg_info_records,
        'print': repoman_print_pkg_info_record
        }

def commands_order():
    return [
        'scan',
        'collisions',
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
        ]

def cli_name():
    return 'repo'

def repoman_scan_repo_for_pkg_and_cat(opts, args):
    """
    Scan repository and save it's categories and packages indexes
    to database
    """

    index_db = org.wayround.aipsetup.pkgindex.PackageIndex()
    ret = org.wayround.aipsetup.pkgindex.scan_repo_for_pkg_and_cat(index_db)
    del index_db

    return ret

def repoman_find_repository_package_name_collisions_in_database(opts, args):
    """
    Scan index for equal package names
    """

    index_db = org.wayround.aipsetup.pkgindex.PackageIndex()
    ret = org.wayround.aipsetup.pkgindex.get_package_collisions_in_db(
        index_db=index_db
        )
    del index_db

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
    subdir_name = os.path.realpath(
        os.path.abspath(
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
            subdir_name = os.path.realpath(os.path.abspath(subdir_name))

        if (
            not (os.path.realpath(os.path.abspath(subdir_name)) + '/').startswith(
            os.path.realpath(os.path.abspath(org.wayround.aipsetup.config.config['source'])) + '/'
            )
            or not os.path.isdir(os.path.abspath(subdir_name))):
            logging.error("Not a subdir of pkg_source")
            logging.debug(
"""\
passed: {}
config: {}
exists: {}
""".format(
                    os.path.realpath(os.path.abspath(subdir_name)),
                    os.path.realpath(os.path.abspath(org.wayround.aipsetup.config.config['source'])),
                    os.path.isdir(subdir_name)
                    )
                )
            ret = 2

        else:
            ret = org.wayround.aipsetup.pkgindex.index_sources(
                os.path.realpath(subdir_name),
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

    -t creates non-existing .xml file templates in info dir

    -f forces rewrite existing .xml files
    """

    ret = 0

    t = '-t' in opts

    f = '-f' in opts

    info_db = org.wayround.aipsetup.pkginfo.PackageInfo()
    index_db = org.wayround.aipsetup.pkgindex.PackageIndex()

    try:
        org.wayround.aipsetup.pkginfo.get_missing_info_records_list(
            t,
            f,
            info_db=info_db,
            index_db=index_db
            )
    except:
        logging.exception("Error while searching for missing records")
        ret = 1
    else:
        ret = 0
    finally:
        del info_db
        del index_db

    return ret

def repoman_find_outdated_pkg_info_records(opts, args):
    """
    Finds pkg info records which differs to FS .xml files
    """
    ret = 0

    info_db = org.wayround.aipsetup.pkginfo.PackageInfo()

    try:
        res = org.wayround.aipsetup.pkginfo.get_outdated_info_records_list(
            info_db=info_db
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

    finally:
        del info_db

    return ret

def repoman_update_outdated_pkg_info_records(opts, args):
    """
    Loads pkg info records which differs to FS .xml files
    """

    info_db = org.wayround.aipsetup.pkginfo.PackageInfo()
    org.wayround.aipsetup.pkginfo.update_outdated_pkg_info_records(info_db)
    del info_db

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
        info_db = org.wayround.aipsetup.pkginfo.PackageInfo()
        ret = org.wayround.aipsetup.pkginfo.delete_info_records(
            mask,
            info_db=info_db
            )
        del info_db
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

    info_db = org.wayround.aipsetup.pkginfo.PackageInfo()
    ret = org.wayround.aipsetup.pkginfo.save_info_records_to_fs(
        mask,
        force,
        info_db=info_db
        )
    del info_db

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
        filenames = glob.glob(org.wayround.aipsetup.config.config['info'] + os.path.sep + '*')
    else:
        filenames = copy.copy(args)

    rewrite_all = '-a' in opts

    info_db = org.wayround.aipsetup.pkginfo.PackageInfo()
    org.wayround.aipsetup.pkginfo.load_info_records_from_fs(
        filenames, rewrite_all, info_db=info_db
        )
    del info_db

    return ret

def repoman_list_pkg_info_records(opts, args):
    """
    List records containing in index

    [FILEMASK]

    Default MASK is *
    """
    # TODO: clarification for help needed
    mask = '*'

    if len(args) > 0:
        mask = args[0]


    info_db = org.wayround.aipsetup.pkginfo.PackageInfo()
    org.wayround.aipsetup.pkginfo.get_info_records_list(mask, info_db=info_db)
    del info_db

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

        info_db = org.wayround.aipsetup.pkginfo.PackageInfo()
        index_db = org.wayround.aipsetup.pkgindex.PackageIndex()
        latest_db = org.wayround.aipsetup.pkglatest.PackageLatest()

        ret = org.wayround.aipsetup.pkginfo.print_info_record(
            name,
            info_db=info_db,
            index_db=index_db,
            latest_db=latest_db
            )
        del info_db, latest_db, index_db
    else:
        logging.error("Name is not given")
        ret = 1

    return ret

