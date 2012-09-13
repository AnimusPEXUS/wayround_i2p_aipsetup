
"""
Facility for indexing and analyzing sources and packages repository
"""

import os.path
import sys
import glob
import fnmatch
import copy
import logging
import re
import functools


import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative


import org.wayround.utils.text
import org.wayround.utils.fileindex
import org.wayround.utils.tag
import org.wayround.utils.log

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config
import org.wayround.aipsetup.name
import org.wayround.aipsetup.version


def exported_commands():
    return {
        'scan': pkgindex_scan_repo_for_pkg_and_cat,
        'find_collisions': \
            pkgindex_find_repository_package_name_collisions_in_database,
        'missing': pkgindex_find_missing_pkg_info_records,
        'outdated': pkgindex_find_outdated_pkg_info_records,
        'update': pkgindex_update_outdated_pkg_info_records,
        'delete': pkgindex_delete_pkg_info_records,
        'backup': pkgindex_backup_package_info_to_filesystem,
        'load': pkgindex_load_package_info_from_filesystem,
        'list': pkgindex_list_pkg_info_records,
        'print': pkgindex_print_pkg_info_record,
        'index_sources': pkgindex_index_sources,
        'edit_latests': pkgindex_latest_editor
        }

def commands_order():
    return [
        'scan',
        'find_collisions',
        'missing',
        'outdated',
        'update',
        'delete',
        'backup',
        'load',
        'list',
        'print',
        'index_sources',
        'edit_latests'
        ]

def pkgindex_scan_repo_for_pkg_and_cat(opts, args):
    """
    Scan repository and save it's categories and packages indexes
    to database
    """

    r = PackageDatabase()
    ret = r.scan_repo_for_pkg_and_cat()
    del r

    return ret

def pkgindex_find_repository_package_name_collisions_in_database(opts, args):
    """
    Scan index for equal package names
    """
    r = PackageDatabase()
    ret = r.find_repository_package_name_collisions_in_database()
    del r

    return ret

def pkgindex_find_missing_pkg_info_records(opts, args):
    """
    Search packages which have no corresponding info records

    [-t] [-f]

    -t creates non-existing .xml file templates in info dir

    -f forces rewrite existing .xml files
    """

    ret = 0

    t = '-t' in opts

    f = '-f' in opts

    try:
        r = PackageDatabase()
        ret = r.find_missing_pkg_info_records(t, f)
        del r
    except:
        logging.exception("Error while searching for missing records")
        ret = 1
    finally:
        ret = 0

    return ret

def pkgindex_find_outdated_pkg_info_records(opts, args):
    """
    Finds pkg info records which differs to FS .xml files
    """
    ret = 0
    try:
        r = PackageDatabase()
    except:
        ret = 1
        logging.error("Error connecting to DB")
    else:
        try:
            res = r.find_outdated_pkg_info_records()

        except:
            ret = 2
            raise

        else:
            if len(res) > 0:
                logging.warning("Total {} warnings".format(len(res)))
            else:
                logging.info("No warnings")

        finally:
            del r

    return ret

def pkgindex_update_outdated_pkg_info_records(opts, args):
    """
    Loads pkg info records which differs to FS .xml files
    """
    r = PackageDatabase()
    r.update_outdated_pkg_info_records()
    del r

    return 0

def pkgindex_delete_pkg_info_records(opts, args):
    """
    mask must be given or operation will fail

    MASK
    """
    mask = None

    ret = 0

    if len(args) > 0:
        mask = args[0]

    if mask != None:
        r = PackageDatabase()
        ret = r.delete_pkg_info_records(mask)
        del r
    else:
        logging.error("Mask is not given")
        ret = 1

    return ret

def pkgindex_backup_package_info_to_filesystem(opts, args):
    """
    Save package information from database to info directory.

    [-f] [MASK]

    Existing files are skipped, unless -f is set
    """
    mask = '*'

    if len(args) > 0:
        mask = args[0]

    force = '-f' in opts

    r = PackageDatabase()
    ret = r.backup_package_info_to_filesystem(mask, force)
    del r

    return ret

def pkgindex_load_package_info_from_filesystem(opts, args):
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

    r = PackageDatabase()
    r.load_package_info_from_filesystem(filenames, rewrite_all)
    del r

    return ret

def pkgindex_list_pkg_info_records(opts, args):
    """
    List records containing in index

    [FILEMASK]

    Default MASK is *
    """
    # TODO: clarification for help needed
    mask = '*'

    if len(args) > 0:
        mask = args[0]


    r = PackageDatabase()
    r.list_pkg_info_records(mask)
    del r

    return 0

def pkgindex_print_pkg_info_record(opts, args):
    """
    Print package info record information
    """

    ret = 0

    name = None

    if len(args) > 0:
        name = args[0]

    if name != None:

        r = PackageDatabase()
        ret = r.print_pkg_info_record(name)
        del r
    else:
        logging.error("Name is not given")
        ret = 1

    return ret


def pkgindex_index_sources(opts, args):
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
            ret = index_sources(
                os.path.realpath(subdir_name),
                force_reindex=force_reindex,
                first_delete_found=first_delete_found
                )

    return ret

def pkgindex_latest_editor(opts, args):

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
        latest_editor(name)

    return ret

def latest_editor(name):
    import org.wayround.aipsetup.latesteditor

    ret = org.wayround.aipsetup.latesteditor.main(name)

    return ret

def is_repo_package_dir(path):
    return os.path.isdir(path) \
        and os.path.isfile(
            os.path.join(path, '.package')
            )


def get_package_path(name):
    ret = None
    r = PackageDatabase()
    pid = r.get_package_id(name)
    if pid == None:
        logging.error("Can't get `{}' from database".format(name))
        ret = None
    else:
        ret = r.get_package_path_string(pid)
    del(r)
    return ret

def create_required_dirs_at_package(path):

    ret = 0

    for i in ['pack', 'source', 'aipsetup2']:
        full_path = path + os.path.sep + i

        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
            except:
                logging.exception("Can't make dir `%(name)s'" % {
                    'name': full_path
                    })
                ret = 3
            else:
                ret = 0
        else:
            if os.path.islink(full_path):
                logging.error("`%(name)s' is link" % {
                    'name': full_path
                    })
                ret = 4
            elif os.path.isfile(full_path):
                logging.error("`%(name)s' is file" % {
                    'name': full_path
                    })
                ret = 5
            else:
                ret = 0

        if ret != 0:
            break

    return ret


def join_pkg_path(pkg_path):
    lst = []

    for i in pkg_path:
        lst.append(i[1])

    ret = '/'.join(lst)

    return ret

def index_sources(subdir_name, force_reindex=False, first_delete_found=False):

    index_directory(
        os.path.realpath(os.path.abspath(org.wayround.aipsetup.config.config['source'])),
        os.path.realpath(os.path.abspath(subdir_name)),
        org.wayround.aipsetup.config.config['source_index'],
        # TODO: move this list to config
        ['.tar.gz', '.tar.bz2', '.zip',
         '.7z', '.tgz', '.tar.xz', '.tar.lzma',
         '.tbz2'],
        force_reindex=force_reindex,
        first_delete_found=first_delete_found
        )

    return 0


def _scan_progress(added_tags, sub_dir_name, root_dir_name_len):
    org.wayround.utils.file.progress_write(
        "    scanning (found {}): {}".format(
            added_tags,
            sub_dir_name[root_dir_name_len + 1:]
            )
        )

    return

def _index_directory_to_list(
    list_buffer,
    root_dir_name,
    sub_dir_name,
    root_dir_name_len,
    acceptable_endings=None,
    added_tags=0
    ):

    sub_dir_name = os.path.abspath(sub_dir_name)

    added_tags = added_tags

    _scan_progress(added_tags, sub_dir_name, root_dir_name_len)

    files = os.listdir(sub_dir_name)
    files.sort()

    for each_file in files:

        if each_file in ['.', '..']:
            continue

        full_path = os.path.join(sub_dir_name, each_file)

        if os.path.islink(full_path):
            continue

        # not each_file[0] == '.' and 
        if os.path.isdir(full_path):

            res = _index_directory_to_list(
                list_buffer,
                root_dir_name,
                full_path,
                root_dir_name_len,
                acceptable_endings,
                added_tags=added_tags
                )
            added_tags = res['added_tags']

        # not each_file[0] == '.' and 
        elif os.path.isfile(full_path):

            if isinstance(acceptable_endings, list):

                match_found = False

                for i in acceptable_endings:
                    if each_file.endswith(i):
                        match_found = True
                        break

                if not match_found:
                    continue


            p = full_path[root_dir_name_len:]
            list_buffer.append(p)
            added_tags += 1

    _scan_progress(added_tags, sub_dir_name, root_dir_name_len)


    return {'added_tags': added_tags}


def index_directory(
    root_dir_name,
    sub_dir_name,
    db_connection,
    acceptable_endings=None,
    force_reindex=False,
    first_delete_found=False
    ):

    root_dir_name = os.path.realpath(os.path.abspath(root_dir_name))
    root_dir_name_len = len(root_dir_name)

    sub_dir_name = os.path.realpath(os.path.abspath(sub_dir_name))

    rel_path = os.path.relpath(sub_dir_name, root_dir_name)
    rel_path = os.path.sep + rel_path + os.path.sep

    logging.debug("Root dir: {}".format(root_dir_name))
    logging.debug("Sub dir: {}".format(sub_dir_name))
    logging.debug("Rel dir: {}".format(rel_path))

    if rel_path == '/./':
        rel_path = ''

    if rel_path == '//':
        rel_path = ''

    added_count = 0
    deleted_count = 0

    logging.info("Indexing {}...".format(root_dir_name))

    source_index = []

    _index_directory_to_list(
        source_index,
        root_dir_name,
        sub_dir_name,
        root_dir_name_len,
        acceptable_endings
        )

    org.wayround.utils.file.progress_write_finish()

    source_index = list(set(source_index))
    source_index.sort()

    found_count = len(source_index)

    logging.info("Found {} indexable objects".format(found_count))

    try:
        tags = org.wayround.utils.tag.TagEngine(db_connection, commit_every=200)
    except:
        logging.exception("Can't connect to source index DB `{}'".format(db_connection))
        raise
    else:

        try:
            if first_delete_found:
                removed = 0
                logging.info("Removing found files from index")
                for i in source_index:
                    org.wayround.utils.file.progress_write(
                        "    removed {} of {}".format(removed, found_count)
                        )
                    tags.del_object_tags(i)
                    removed += 1

                tags.commit()

                org.wayround.utils.file.progress_write_finish()

            logging.info("Saving to DB")
            index = -1
            failed_count = 0
            skipped_count = 0
            tag_objects = set(tags.get_objects())

            for i in source_index:
                index += 1

                if not force_reindex and i in tag_objects:

                    skipped_count += 1

                else:

                    parsed_src_filename = (
                        org.wayround.aipsetup.name.source_name_parse(
                            i,
                            mute=True
                            )
                        )

                    if parsed_src_filename:
                        tags.set_tags(i, [parsed_src_filename['groups']['name']])
                        added_count += 1
                    else:
                        org.wayround.utils.file.progress_write(
                            "    failed to parse: {}\n".format(os.path.basename(i))
                            )
                        failed_count += 1

                org.wayround.utils.file.progress_write(
                    "    processing {} out of {} (added {}, failed {}, skipped {})".format(
                        index,
                        found_count,
                        added_count,
                        failed_count,
                        skipped_count
                        )
                    )


            del source_index
#            res = _index_directory(tags, root_dir_name, root_dir_name_len, acceptable_endings)
#            added_count = res['added_tags']

            tags.commit()
            org.wayround.utils.file.progress_write_finish()
            logging.info("Cleaning wrong DB entries")
            tag_objects = tags.get_objects()
            deleted_count = 0
            found_scanned_count = 0
            skipped_count = 0
            for i in tag_objects:

                logging.debug("Checking to skip {}".format(os.path.sep + rel_path + os.path.sep))

                if i.startswith(rel_path):
                    if not os.path.exists(
                        os.path.realpath(
                            os.path.abspath(
                                root_dir_name + os.path.sep + i
                                )
                            )
                        ):
                        tags.del_object_tags(i)
                        deleted_count += 1

                    found_scanned_count += 1

                else:
                    skipped_count += 1

                org.wayround.utils.file.progress_write(
                    "    searching (scanned {}, deleted {}, skipped {}): {}".format(
                        found_scanned_count,
                        deleted_count,
                        skipped_count,
                        i
                        )
                    )

            org.wayround.utils.file.progress_write_finish()

            tags.commit()

            logging.info(
                "Records: added {added}; deleted {deleted}".format(
                    added=added_count,
                    deleted=deleted_count
                    )
                )
            logging.info("DB Size: {} record(s)".format(tags.get_size()))
        finally:
            tags.close()

    return 0


def get_package_info(name, db_connected=None):

    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()

    ret = db.package_info_record_to_dict(name)

    if not db_connected:
        del db

    return ret

def pkg_file_list_to_dict(files, name):
    needed_files = {}
    for i in files:
        file_name = os.path.basename(i)
        file_name_parsed = org.wayround.aipsetup.name.package_name_parse(file_name)
        if file_name_parsed and file_name_parsed['groups']['name'] == name:
            needed_files[file_name] = file_name_parsed
    return needed_files


def get_package_files(name, db_connected=None):

    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()

    pid = db.get_package_id(name)
    package_path = db.get_package_path_string(pid)

    if not db_connected:
        del db

    package_dir = os.path.abspath(
        org.wayround.aipsetup.config.config['repository']
        + os.path.sep + package_path + os.path.sep + 'pack'
        )

    logging.debug("Looking for package files in `{}'".format(package_dir))
    files = glob.glob(os.path.join(package_dir, '*.asp'))

    needed_files = []
    for i in files:
        if org.wayround.aipsetup.name.package_name_parse(i) != None:
            needed_files.append(
                '/' +
                os.path.relpath(
                    i,
                    org.wayround.aipsetup.config.config['repository']
                    )
                )
#        file_name = os.path.basename(i)
#        file_name_parsed = org.wayround.aipsetup.name.package_name_parse(file_name)
#        if file_name_parsed and file_name_parsed['groups']['name'] == name:
#            needed_files[file_name] = file_name_parsed

    return needed_files

def get_package_source_files(name, db_connected=None):

    needed_files = []

    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()

    pkg_info = db.package_info_record_to_dict(name=name)

    if not db_connected:
        del db

    try:
        tags_object = org.wayround.utils.tag.TagEngine(
            org.wayround.aipsetup.config.config['source_index']
            )
    except:
        logging.exception("Can't connect to source file index")
    else:
        try:
            needed_files = []
            files = tags_object.objects_by_tags([pkg_info['basename']])
            for i in files:
                parsed_name = (
                    org.wayround.aipsetup.name.source_name_parse(i, mute=True)
                    )
                if parsed_name:
                    try:
                        re_m = re.match(
                            pkg_info['version_re'],
                            parsed_name['groups']['version']
                            )
                    except:
                        logging.exception(
                            "Error matching RE `{}' to `'".format(
                                pkg_info['version_re'],
                                parsed_name['groups']['version']
                                )
                            )
                    else:
                        if re_m:
                            needed_files.append(i)

            needed_files.sort()

        finally:
            tags_object.close()

    return needed_files

def latest_source(name, db_connected=None, files=None):

    ret = None

    if not files:
        files = get_package_source_files(name, db_connected)

    if len(files) == 0:
        ret = None
    else:
#        org.wayround.utils.list.list_sort(
#            files,
#            cmp=org.wayround.aipsetup.version.source_version_comparator
#            )
        ret = max(
            files,
            key=functools.cmp_to_key(
                org.wayround.aipsetup.version.source_version_comparator
                )
            )
#        ret = files[-1]

    return ret

def latest_package(name, db_connected=None, files=None):

    ret = None

    if not files:
        files = get_package_files(name, db_connected)

    if len(files) == 0:
        ret = None
    else:

        ret = max(
            files,
            key=functools.cmp_to_key(
                org.wayround.aipsetup.version.package_version_comparator
                )
            )
#        org.wayround.utils.list.list_sort(
#            files, cmp=org.wayround.aipsetup.version.package_version_comparator
#            )
#
#        ret = files[-1]

    return ret

def latest_src_to_package(name, force=False, mute=True, db_connected=None):

    ret = False

    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()

    r = latest_source(name)
    if r != None:
        org.wayround.utils.log.verbose_print(
            "Package's latest src is: `{}'".format(r),
            not mute
            )
        if r != None:

            ret = db.set_latest_source(name, r, force)

        else:
            ret = False

    if not ret:
        org.wayround.utils.log.verbose_print("Can't set")

    if not db_connected:
        del db

    return ret

def latest_src_to_packages(names, force=False, mute=True, db_connected=None):

    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()

    if len(names) == 0:
        names = db.list_pkg_info_records(mute=True)

    for i in names:
        latest_src_to_package(
            i,
            force,
            mute,
            db_connected
            )

    if not db_connected:
        del db

    return

def latest_pkg_to_package(name, force=False, mute=True, db_connected=None):

    ret = False

    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()


    r = latest_package(name)
    if r != None:
        org.wayround.utils.log.verbose_print(
            "Package's latest pkg is: `{}'".format(r),
            not mute
            )
        if r != None:

            ret = db.set_latest_package(name, r, force)

        else:
            ret = False

    if not ret:
        org.wayround.utils.log.verbose_print("Can't set", not mute)

    if not db_connected:
        del db

    return ret

def latest_pkg_to_packages(names, force=False, mute=True, db_connected=None):

    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()

    if len(names) == 0:
        names = db.list_pkg_info_records(mute=True)

    for i in names:
        latest_pkg_to_package(i, force, mute, db_connected)

    if not db_connected:
        del db

    return

def find_package_info_by_basename_and_version(basename, version, db_connected=None):
    db = None
    if db_connected:
        db = db_connected
    else:
        db = PackageDatabase()

    ret = db.find_package_info_by_basename_and_version(basename, version)

    if not db_connected:
        del db

    return ret

def guess_package_homepage(pkg_name, tag_db_connected=None):

    db = None
    if tag_db_connected:
        db = tag_db_connected
    else:
        db = org.wayround.utils.tag.TagEngine(
            org.wayround.aipsetup.config.config['source_index']
            )

    files = db.objects_by_tags([pkg_name])
    possibilities = {}
    for i in files:
        domain = i[1:].split('/')[0]

        if not domain in possibilities:
            possibilities[domain] = 0

        possibilities[domain] += 1
    logging.debug('Possibilities for {} are: {}'.format(pkg_name, repr(possibilities)))

    if not tag_db_connected:
        del db

    return possibilities



class PackageDatabaseConfigError(Exception): pass

class PackageDatabase:
    """
    Main package index DB handling class
    """

    Base = sqlalchemy.ext.declarative.declarative_base()

    class Package(Base):
        """
        Package class

        There can be many packages with same name, but this
        is only for tucking down duplicates and eradicate
        them.
        """

        __tablename__ = 'package'

        pid = sqlalchemy.Column(
            sqlalchemy.Integer,
            primary_key=True,
            autoincrement=True
            )

        name = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        cid = sqlalchemy.Column(
            sqlalchemy.Integer,
            nullable=False,
            default=0
            )


    class Category(Base):
        """
        Class for package categories

        There can be categories with same names
        """

        __tablename__ = 'category'

        cid = sqlalchemy.Column(
            sqlalchemy.Integer,
            primary_key=True,
            autoincrement=True
            )

        name = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        parent_cid = sqlalchemy.Column(
            sqlalchemy.Integer,
            nullable=False,
            default=0
            )

    class PackageInfo(Base):
        """
        Class for holding package information
        """
        __tablename__ = 'package_info'

        name = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            primary_key=True,
            default=''
            )

        basename = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        version_re = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        home_page = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        description = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        buildinfo = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        installation_priority = sqlalchemy.Column(
            sqlalchemy.Integer,
            nullable=False,
            default=5
            )

        removable = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        reducible = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        auto_newest_src = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        auto_newest_pkg = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

    class PackageTag(Base):
        """
        Class for package's tags
        """

        __tablename__ = 'package_tag'

        id = sqlalchemy.Column(
            sqlalchemy.Integer,
            nullable=False,
            primary_key=True,
            autoincrement=True
            )

        name = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False
            )

        tag = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False
            )

    class Newest(Base):
        """
        Class for package's tags
        """

        __tablename__ = 'newest'

        id = sqlalchemy.Column(
            sqlalchemy.Integer,
            nullable=False,
            primary_key=True,
            autoincrement=True
            )

        name = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False
            )

        typ = sqlalchemy.Column(
            'type',
            sqlalchemy.UnicodeText,
            nullable=False
            )

        file = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=True,
            default=None,
            )



    def __init__(self):

        self._config = org.wayround.aipsetup.config.config

        if not os.path.isdir(self._config['repository']):
            raise PackageDatabaseConfigError(
                "No repository to service configured"
                )

        db_echo = False

        self._db_engine = \
            sqlalchemy.create_engine(
            self._config['package_index_db_config'],
            echo=db_echo
            )

        self.Base.metadata.bind = self._db_engine

        self.Base.metadata.create_all()

        self.sess = None
        self.start_session()

    def __del__(self):
        logging.debug("PKG Index DB cleaning")
        self.close_session()


    def start_session(self):
        if not self.sess:
            self.sess = sqlalchemy.orm.Session(bind=self._db_engine)

    def commit_session(self):
        if self.sess:
            self.sess.commit()

    def close_session(self):
        if self.sess:
            self.sess.commit()
            self.sess.close()
            self.sess = None


    def create_category(self, name='name', parent_cid=0):

        new_cat = self.Category(name=name, parent_cid=parent_cid)

        self.sess.add(new_cat)

        new_cat_id = new_cat.cid

        return new_cat_id

    def get_category_by_id(self, cid):

        ret = None

        q = self.sess.query(self.Category).filter_by(cid=cid).first()

        if q:
            ret = q.name

        return ret

    def get_category_parent_by_id(self, cid):

        ret = None

        q = self.sess.query(self.Category).filter_by(cid=cid).first()

        if q:
            ret = q.parent_cid

        return ret

    def get_category_by_path(self, path):

        if not isinstance(path, str):
            raise ValueError("`path' must be string")

        ret = 0
        if len(path) > 0:

            logging.debug("path: {}".format(repr(path)))
            path_parsed = path.split('/')

            logging.debug("path_parsed: {}".format(repr(path_parsed)))

            level = 0

            for i in path_parsed:

                logging.debug("Searching for: {}".format(i))
                cat_dir = self.ls_category_dict(level)
                logging.debug("cat_dir: {}".format(cat_dir))

                found_cat = False
                for j in cat_dir:
                    if cat_dir[j] == i:
                        level = j
                        ret = j
                        logging.debug("found `{}' cid == {}".format(i, j))
                        found_cat = True
                        break

                if not found_cat:
                    ret = None
                    logging.debug("not found `{}' cid".format(i))
                    break

                if ret == None:
                    break

        return ret

    def get_package_id(self, name):

        ret = None

        q = self.sess.query(self.Package).filter_by(name=name).first()
        if q != None:
            ret = q.pid

        return ret

    def get_package_category(self, pid):
        ret = None

        q = self.sess.query(self.Package).filter_by(pid=pid).first()
        if q != None:
            ret = q.cid

        return ret

    def get_package_category_by_name(self, name):
        ret = None

        q = self.sess.query(self.Package).filter_by(name=name).first()
        if q != None:
            ret = q.cid

        return ret


    def get_package_by_id(self, pid):

        ret = None

        q = self.sess.query(self.Package).filter_by(pid=pid).first()
        if q != None:
            ret = q.name

        return ret


    def ls_packages(self, cid=None):

        if cid == None:
            lst = self.sess.query(self.Package).all()
        else:
            lst = self.sess.query(self.Package).filter_by(cid=cid).all()

        lst_names = []
        for i in lst:
            lst_names.append(i.name)

        del(lst)

        lst_names.sort()

        return lst_names

    def ls_package_ids(self, cid=None):

        if cid == None:
            lst = self.sess.query(self.Package).all()
        else:
            lst = self.sess.query(self.Package).filter_by(cid=cid).all()

        ids = []
        for i in lst:
            ids.append(i.pid)

        del(lst)

        return ids

    def ls_package_dict(self, cid=None):

        if cid == None:
            lst = self.sess.query(self.Package).all()
        else:
            lst = self.sess.query(self.Package).filter_by(cid=cid).all()

        dic = {}
        for i in lst:
            dic[int(i.pid)] = i.name

        del(lst)

        return dic

    def ls_categories(self, parent_cid=0):

        lst = self.sess.query(self.Category).filter_by(parent_cid=parent_cid).order_by(self.Category.name).all()

        lst_names = []
        for i in lst:
            lst_names.append(i.name)

        del(lst)

        lst_names.sort()

        return lst_names

    def ls_category_ids(self, parent_cid=0):

        lst = self.sess.query(self.Category).filter_by(parent_cid=parent_cid).order_by(self.Category.name).all()

        ids = []
        for i in lst:
            ids.append(i.cid)

        del(lst)

        return ids

    def ls_category_dict(self, parent_cid=0):

        lst = self.sess.query(self.Category).filter_by(parent_cid=parent_cid).order_by(self.Category.name).all()

        dic = {}
        for i in lst:
            dic[int(i.cid)] = i.name

        del(lst)

        return dic


    def _scan_repo_for_pkg_and_cat(self, root_dir, cid):

        files = os.listdir(root_dir)

        files.sort()

        isfiles = 0

        for each in files:
            full_path = os.path.join(root_dir, each)

            if not os.path.isdir(full_path):
                isfiles += 1

        if isfiles >= 3:
            logging.warning("too many non-dirs : %(path)s" % {
                'path': root_dir
                })
            print("       skipping")

            return 1

        for each in files:
            if each in ['.', '..']:
                continue

            full_path = os.path.join(root_dir, each)

            if os.path.islink(full_path):
                continue

            if is_repo_package_dir(full_path):
                pa = self.Package(name=each, cid=cid)
                self.sess.add(pa)
                # TODO: May be comment this commit?
                # self.sess.commit()
                if sys.stdout.isatty():
                    pcount = self.sess.query(self.Package).count()
                    line_to_write = "       %(num)d packages found: %(name)s" % {
                        'num': pcount,
                        'name': pa.name
                        }
                    org.wayround.utils.file.progress_write(line_to_write)
                del(pa)
            elif os.path.isdir(full_path):
                new_cat = self.Category(name=each, parent_cid=cid)

                self.sess.add(new_cat)
                self.sess.commit()

                new_cat_cid = new_cat.cid
                del(new_cat)

                self._scan_repo_for_pkg_and_cat(
                    full_path, new_cat_cid
                    )
            else:
                logging.warning("garbage file found: %(path)s" % {
                    'path': full_path
                    })

        return 0

    def scan_repo_for_pkg_and_cat(self):

        ret = 0

        logging.info("Deleting old data")
        self.sess.query(self.Category).delete()
        self.sess.query(self.Package).delete()

        logging.info("Committing")
        self.sess.commit()

        logging.info("Scanning repository...")
        self._scan_repo_for_pkg_and_cat(
            self._config['repository'], 0)

        org.wayround.utils.file.progress_write_finish()
        self.sess.commit()

        logging.info("Searching for errors")
        self.find_repository_package_name_collisions_in_database()
        logging.info("Search operations finished")

        return ret

    def get_package_tags(self, name):
        ret = []

        q = self.sess.query(self.PackageTag).filter_by(name=name).all()

        for i in q:
            ret.append(i.tag)

        return ret

    def set_package_tags(self, name, tags):

        self.sess.query(self.PackageTag).filter_by(name=name).delete()

        for tag_name in tags:
            new_tag = self.PackageTag()
            new_tag.name = name
            new_tag.tag = tag_name
            self.sess.add(new_tag)

        return

    def get_package_path(self, pid):

        ret = []
        pkg = None

        if pid != None:
            pkg = self.sess.query(self.Package).filter_by(pid=pid).first()
        else:
            raise ValueError("Error getting package data from DB")

        # print "pkg: "+repr(dir(pkg))

        if pkg != None :

            r = pkg.cid
            # print 'r: '+str(r)
            ret.insert(0, (pkg.pid, pkg.name))

            while r != 0:
                cat = self.sess.query(self.Category).filter_by(cid=r).first()
                ret.insert(0, (cat.cid, cat.name))
                r = cat.parent_cid

            # This is _presumed_. NOT inserted
            # ret.insert(0,(0, '/'))


        #print '-gpp- :' + repr(ret)
        return ret


    def get_category_path(self, cid):

        ret = []
        categ = None

        if cid != None:
            categ = self.sess.query(self.Category).filter_by(cid=cid).first()
        else:
            raise ValueError("Error getting category data from DB")

        # print "categ: "+repr(dir(categ))

        if categ != None :

            r = categ.parent_cid
            # print 'r: '+str(r)
            ret.insert(0, (categ.cid, categ.name))

            while r != 0:
                cat = self.sess.query(self.Category).filter_by(cid=r).first()
                ret.insert(0, (cat.cid, cat.name))
                r = cat.parent_cid

            # This is _presumed_. NOT inserted
            # ret.insert(0,(0, '/'))

        #print '-gpp- :' + repr(ret)
        return ret


    def get_package_path_string(self, cid):
        r = self.get_package_path(cid)
        ret = join_pkg_path(r)
        return ret

    def get_category_path_string(self, cid):
        r = self.get_category_path(cid)
        ret = join_pkg_path(r)
        return ret

    def find_repository_package_name_collisions_in_database(self):

        lst = self.sess.query(self.Package).order_by(self.Package.name).all()

        lst2 = []

        logging.info("Scanning paths")
        for each in lst:
            org.wayround.utils.file.progress_write('       ' + each.name)
            lst2.append(self.get_package_path(pid=each.pid))
        org.wayround.utils.file.progress_write_finish()

        logging.info("Processing %(n)s packages..." % {'n': len(lst)})
        sys.stdout.flush()

        del(lst)

        lst_dup = {}
        pkg_paths = {}

        for each in lst2:

            l = each[-1][1].lower()

            if not l in pkg_paths:
                pkg_paths[l] = []

            pkg_paths[l].append(join_pkg_path(each))

        for each in list(pkg_paths.keys()):
            if len(pkg_paths[each]) > 1:
                lst_dup[each] = pkg_paths[each]


        if len(lst_dup) == 0:
            logging.info("Found %(c)s duplicated package names. Package locations look good!" % {
                'c' : len(lst_dup)
                })
        else:
            logging.warning("Found %(c)s duplicated package names" % {
                'c' : len(lst_dup)
                })

            print("       listing:")

            sorted_keys = list(lst_dup.keys())
            sorted_keys.sort()

            for each in sorted_keys:
                print("          %(key)s:" % {
                    'key': each
                    })

                lst_dup[each].sort()

                for each2 in lst_dup[each]:
                    print("             %(path)s" % {
                        'path': each2
                        })

        return 0

    def check_package_information(self, names=None):
        """
        names can be a list of names to check. if names is None -
        check all.
        """

        found = []

        not_found = []

        names_found = []

        if names == None:
            q = self.sess.query(self.Package).all()
            for i in q:
                names_found.append(i.name)
        else:
            names_found = names

        for i in names_found:
            q = self.sess.query(self.PackageInfo).filter_by(name=i).first()

            if q == None:
                not_found.append(q)
            else:
                found.append(q)

        return (found, not_found)

    def package_info_record_to_dict(self, name=None, record=None):
        """
        This method can accept package name or complete record
        instance.

        If name is given, record is not used and method does db query
        itself.

        If name is not given, record is used as if it were this method's
        query result.
        """

        ret = None

        if name != None:
            q = self.sess.query(self.PackageInfo).filter_by(name=name).first()
        else:
            q = record

        if q == None:
            ret = None
        else:

            ret = dict()

            tags = self.get_package_tags(q.name)

            keys = set(org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys())
            keys.remove('tags')

            for i in keys:
                ret[i] = eval('q.{}'.format(i))

            ret['tags'] = tags
            ret['name'] = q.name

        return ret


    def package_info_dict_to_record(self, name, struct):

        # TODO: check_info_dict(struct)

        q = self.sess.query(self.PackageInfo).filter_by(name=name).first()

        creating_new = False
        if q == None:
            q = self.PackageInfo()
            creating_new = True

#        keys = set(org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys())
#
#        for i in ['tags', 'name']:
#            if i in keys:
#                keys.remove(i)

        q.name = name
        q.description = str(struct["description"])
        q.home_page = str(struct["home_page"])
        q.buildinfo = str(struct["buildinfo"])
        q.basename = str(struct["basename"])
        q.version_re = str(struct["version_re"])
        q.installation_priority = int(struct["installation_priority"])
        q.removable = bool(struct["removable"])
        q.reducible = bool(struct["reducible"])
        q.auto_newest_src = bool(struct["auto_newest_src"])
        q.auto_newest_pkg = bool(struct["auto_newest_pkg"])

#        for i in keys:
#            exec('q.{key} = struct["{key}"]'.format(key=i))


        if creating_new:
            self.sess.add(q)


        self.set_package_tags(name, struct['tags'])
        #self.commit_session()

        return

    def backup_package_info_to_filesystem(
        self, mask='*', force_rewrite=False):

        q = self.sess.query(self.PackageInfo).all()

        for i in q:
            if fnmatch.fnmatch(i.name, mask):
                filename = os.path.join(
                    self._config['info'], '%(name)s.xml' % {
                        'name': i.name
                        })
                if not force_rewrite and os.path.exists(filename):
                    logging.warning("File exists - skipping: %(name)s" % {
                        'name': filename
                        })
                    continue
                if force_rewrite and os.path.exists(filename):
                    logging.info("File exists - rewriting: %(name)s" % {
                        'name': filename
                        })
                if not os.path.exists(filename):
                    logging.info("Writing: %(name)s" % {
                        'name': filename
                        })

                r = self.package_info_record_to_dict(record=i)
                if isinstance(r, dict):
                    if org.wayround.aipsetup.info.write_to_file(filename, r) != 0:
                        logging.error("can't write file %(name)s" % {
                            'name': filename
                            })

        return

    def load_package_info_from_filesystem(
        self, filenames=[], rewrite_existing=False
        ):

        """
        If names list is given - load only named and don't delete
        existing
        """

        files = []
        loaded = 0

        for i in filenames:
            if i.endswith('.xml'):
                files.append(i)

        files.sort()

        missing = []
        logging.info("Searching missing records")
        files_l = len(files)
        num = 0
        for i in files:

            if num == 0:
                perc = 0
            else:
                perc = 100 / (float(files_l) / num)
            org.wayround.utils.file.progress_write('    %(percent)d%%' % {
                'percent': perc
                })
            num += 1

            name = os.path.basename(i)[:-4]

            if not rewrite_existing:
                q = self.sess.query(self.PackageInfo).filter_by(
                    name=name
                    ).first()
                if q == None:
                    missing.append(i)
            else:
                missing.append(i)

        org.wayround.utils.file.progress_write_finish()

        org.wayround.utils.file.progress_write("-i- Loading missing records")

        for i in missing:
            struct = org.wayround.aipsetup.info.read_from_file(i)
            name = os.path.basename(i)[:-4]
            if isinstance(struct, dict):
                org.wayround.utils.file.progress_write(
                    "    loading record: %(name)s" % {
                        'name': name
                        }
                    )

                self.package_info_dict_to_record(
                    name, struct
                    )
                loaded += 1
            else:
                logging.error("can't get info from file %(name)s" % {
                    'name': i
                    })
        self.commit_session()
        org.wayround.utils.file.progress_write_finish()

        logging.info("Totally loaded %(n)d records" % {'n': loaded})
        return

    def delete_pkg_info_records(self, mask='*'):

        q = self.sess.query(self.PackageInfo).all()

        deleted = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                self.sess.delete(i)
                deleted += 1
                logging.info("deleted pkg info: %(name)s" % {
                    'name': i.name
                    })
                sys.stdout.flush()

        logging.info("Totally deleted %(n)d records" % {
            'n': deleted
            })
        return

    def list_pkg_info_records(self, mask='*', mute=False):
        lst = []

        q = self.sess.query(self.PackageInfo).order_by(self.PackageInfo.name).all()

        found = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                found += 1
                lst.append(i.name)

        if not mute:
            org.wayround.utils.text.columned_list_print(lst)
            logging.info("Total found %(n)d records" % {
                'n': found
                })
        return lst

    def find_missing_pkg_info_records(
        self, create_templates=False, force_rewrite=False
        ):

        q = self.sess.query(self.Package).order_by(self.Package.name).all()

        pkgs_checked = 0
        pkgs_missing = 0
        pkgs_written = 0
        pkgs_exists = 0
        pkgs_failed = 0
        pkgs_forced = 0

        missing = []

        for each in q:

            pkgs_checked += 1

            q2 = self.sess.query(self.PackageInfo).filter_by(name=each.name).first()

            if q2 == None:

                pkgs_missing += 1
                missing.append(each.name)

                logging.warning("missing package DB info record: %(name)s" % {
                    'name': each.name
                    })

                if create_templates:

                    filename = os.path.join(
                        self._config['info'],
                        '%(name)s.xml' % {'name': each.name}
                        )

                    if os.path.exists(filename):
                        if not force_rewrite:
                            logging.info("XML info file already exists")
                            pkgs_exists += 1
                            continue
                        else:
                            pkgs_forced += 1

                    if force_rewrite:
                        logging.info("Forced template rewriting: {}".format(filename))

                    if org.wayround.aipsetup.info.write_to_file(
                        filename,
                        org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE) != 0:
                        pkgs_failed += 1
                        logging.error("failed writing template to `%(name)s'" % {
                            'name': filename
                            })
                    else:
                        pkgs_written += 1

        logging.info("""\
Total records checked     : %(n1)d
    Missing records           : %(n2)d
    Missing but present on FS : %(n3)d
    Written                   : %(n4)d
    Write failed              : %(n5)d
    Write forced              : %(n6)d
""" % {
            'n1': pkgs_checked,
            'n2': pkgs_missing,
            'n3': pkgs_exists,
            'n4': pkgs_written,
            'n5': pkgs_failed,
            'n6': pkgs_forced
})

        missing.sort()
        return missing

    def find_outdated_pkg_info_records(self, mute=True):

        ret = []

        query_result = (
            self.sess.query(self.PackageInfo).order_by(self.PackageInfo.name).all()
            )

        for i in query_result:

            filename = os.path.join(
                self._config['info'],
                '{}.xml'.format(i.name)
                )

            if not os.path.exists(filename):
                if not mute:
                    logging.warning("File missing: {}".format(filename))
                ret.append(i.name)
                continue

            d1 = org.wayround.aipsetup.info.read_from_file(filename)

            if not isinstance(d1, dict):
                if not mute:
                    logging.error("Error parsing file: {}".format(filename))
                ret.append(i.name)
                continue

            d2 = self.package_info_record_to_dict(record=i)
            if not org.wayround.aipsetup.info.is_info_dicts_equal(d1, d2):
                if not mute:
                    logging.warning("xml init file differs to `%(name)s' record" % {
                        'name': i.name
                        })
                ret.append(i.name)

        return ret

    def update_outdated_pkg_info_records(self):

        opir = self.find_outdated_pkg_info_records(mute=True)

        opir2 = []

        for i in opir:
            opir2.append(
                os.path.join(
                    self._config['info'],
                    '%(name)s.xml' % {'name': i}
                    )
                )

        self.load_package_info_from_filesystem(
            filenames=opir2,
            rewrite_existing=True
            )

        return


    def print_pkg_info_record(self, name):
        r = self.package_info_record_to_dict(name=name)
        if r == None:
            logging.error("Not found named info record")
        else:

            cid = self.get_package_category_by_name(name)
            if cid != None:
                category = self.get_category_path_string(cid)
            else:
                category = "< Package not indexed! >"

            # TODO: add all fields
            print("""\
+---[{name}]---------------------------------------+
              basename: {basename}
        version regexp: {version_re}
             buildinfo: {buildinfo}
              homepage: {home_page}
              category: {category}
                  tags: {tags}
 installation priority: {installation_priority}
             removable: {removable}
             reducible: {reducible}
       auto newest src: {auto_newest_src}
       auto newest pkg: {auto_newest_pkg}
            newest src: {newest_src}
            newest pkg: {newest_pkg}
+---[{name}]---------------------------------------+
{description}
+---[{name}]---------------------------------------+
""".format_map(
        {
        'tags'                  : ', '.join(r['tags']),
        'category'              : category,
        'name'                  : name,
        'description'           : r['description'],
        'home_page'             : r['home_page'],
        'buildinfo'             : r['buildinfo'],
        'basename'              : r['basename'],
        'version_re'            : r['version_re'],
        'installation_priority' : r['installation_priority'],
        'removable'             : r['removable'],
        'reducible'             : r['reducible'],
        'auto_newest_src'       : r['auto_newest_src'],
        'auto_newest_pkg'       : r['auto_newest_pkg'],
        'newest_src'            : self.get_latest_source(name),
        'newest_pkg'            : self.get_latest_package(name),
        }
        )
    )

    def find_package_info_by_basename_and_version(self, basename, version):

        ret = {}

        q = self.sess.query(self.PackageInfo).filter_by(basename=basename).all()

        for i in q:
            if re.match(i.version_re, version):
                ret[i.name] = self.package_info_record_to_dict(i.name, i)
                break

        return ret

    def set_latest_source(self, name, latest, force=False):
        return self.set_latest(name, latest, 'src', force)

    def set_latest_package(self, name, latest, force=False):
        return self.set_latest(name, latest, 'pkg', force)

    def set_latest(self, name, latest, typ, force=False):

        logging.debug("setting latest `{}' to `{}'".format(typ, latest))
        ret = None

        if not typ in ['src', 'pkg']:
            raise ValueError("`typ' can be only 'src' or 'pkg'")

        typ2 = ''
        if typ == 'src':
            typ2 = 'source'
        elif typ == 'pkg':
            typ2 = 'package'

        info = self.package_info_record_to_dict(name)

        if info == None:
            logging.error("Not found PackageInfo record for `{}'".format(name))
        else:

            logging.debug("Searching for existing `Newest' record of `{}'".format(name))
            q = self.sess.query(
                self.Newest
                ).filter_by(
                    name=name, typ=typ2
                ).first()

            if q == None:
                logging.debug("existing `Newest' record of `{}' not found".format(name))
                if info['auto_newest_' + typ] or force:
                    logging.debug("creating `Newest' record of `{}'".format(name))
                    a = self.Newest()
                    a.name = name
                    a.file = latest
                    a.typ = typ2
                    self.sess.add(a)
                    ret = True
                else:
                    ret = False
            else:
                logging.debug("existing `Newest' record of `{}' found".format(name))
                if info['auto_newest_' + typ] or force:
                    logging.debug("updating `Newest' record of `{}'".format(name))
                    q.file = latest
                    self.sess.commit()
                    ret = True
                else:
                    ret = False

        if ret == False:
            logging.error(
                "Not `auto_newest_{}' and not forced".format(typ)
                )

        return ret

    def get_latest_source(self, name):
        return self.get_latest(name, 'src')

    def get_latest_package(self, name):
        return self.get_latest(name, 'pkg')

    def get_latest(self, name, typ):

        ret = None

        if not typ in ['src', 'pkg']:
            raise ValueError("`typ' can be only 'src' or 'pkg'")

        info = self.package_info_record_to_dict(name)

        if info == None:
            logging.error("Not found PackageInfo record for `{}'".format(name))
        else:
            typ2 = ''
            if typ == 'src':
                typ2 = 'source'
            elif typ == 'pkg':
                typ2 = 'package'

            if info['auto_newest_' + typ]:
                latest = ''
                if typ == 'src':
                    latest = latest_source(name, self)
                elif typ == 'pkg':
                    latest = latest_package(name, self)
                ret = latest
            else:

                latest_r = self.sess.query(
                    self.Newest
                    ).filter_by(
                        name=name, typ=typ2
                        ).first()

                if latest_r == None:
                    ret = None
                else:
                    latest = latest_r.file
                    ret = latest

        return ret

    def get_list_of_non_automatic_package_info(self):

        q = self.sess.query(
            self.PackageInfo
            ).filter(
                self.PackageInfo.auto_newest_pkg == False
                or self.PackageInfo.auto_newest_src == False
                ).all()

        lst = []
        for i in q:
            lst.append(self.package_info_record_to_dict(i.name, i))

        return lst
