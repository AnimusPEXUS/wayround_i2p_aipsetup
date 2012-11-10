
"""
Facility for indexing and analyzing sources and packages repository
"""

import copy
import functools
import glob
import logging
import os.path
import pprint
import re
import shutil
import sys

import sqlalchemy
import sqlalchemy.ext

import org.wayround.utils.db
import org.wayround.utils.tag
import org.wayround.utils.file

import org.wayround.aipsetup.config
import org.wayround.aipsetup.name

import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.dbconnections


class PackageIndex(org.wayround.utils.db.BasicDB):
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
            primary_key=True
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
            primary_key=True
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

    def __init__(self):

        org.wayround.utils.db.BasicDB.__init__(
            self,
            org.wayround.aipsetup.config.config['package_index_db_config'],
            echo=False
            )

        return

def get_sources_connection():
    ret = None
    try:
        tags = org.wayround.utils.tag.TagEngine(
            org.wayround.aipsetup.config.config['source_index'],
            commit_every=200
            )
    except:
        logging.exception(
            "Can't connect to source index DB `{}'".format(
                org.wayround.aipsetup.config.config['source_index']
                )
            )
        raise
    else:
        ret = tags

    return ret


def is_repo_package(path):

    return (os.path.isdir(path)
        and os.path.isfile(
            os.path.join(path, '.package')
            )
        )

def get_package_files(name):

    ret = 0

    pid = get_package_id(name)
    if pid == None:
        logging.error("Error getting package `{}' ID".format(name))
        ret = 1
    else:

        package_path = get_package_path_string(pid)

        if not isinstance(package_path, str):
            logging.error("Can't get path for package `{}'".format(pid))
            ret = 2
        else:

            package_dir = os.path.abspath(
                org.wayround.aipsetup.config.config['repository']
                + os.path.sep + package_path + os.path.sep + 'pack'
                )

            logging.debug("Looking for package files in `{}'".format(package_dir))
            files = glob.glob(os.path.join(package_dir, '*.asp'))

            needed_files = []
            for i in files:
                parsed = org.wayround.aipsetup.name.package_name_parse(i)
                if parsed and parsed['groups']['name'] == name:
                    needed_files.append(
                        '/' +
                        os.path.relpath(
                            i,
                            org.wayround.aipsetup.config.config['repository']
                            )
                        )

            ret = needed_files

    return ret


def get_package_source_files(name, filtered=True):

    ret = []

    pkg_info = org.wayround.aipsetup.pkginfo.get_package_info_record(
        name=name
        )

    try:
        tags_object = org.wayround.aipsetup.dbconnections.src_db()
    except:
        logging.exception("Can't connect to source file index")
    else:
        try:

            files = []
            files = tags_object.objects_by_tags([pkg_info['basename']])

            if filtered:
                files2 = []
                for i in files:
                    if i.startswith(pkg_info['src_path_prefix']):
                        files2.append(i)

                files = files2

                del files2

            if filtered:
                ftl_r = (
                    org.wayround.aipsetup.pkginfo.filter_tarball_list(
                        files,
                        pkg_info['filters']
                        )
                    )
                if isinstance(ftl_r, list):
                    files = ftl_r
                else:
                    logging.error(
                        "get_package_source_files: filter_tarball_list returned `{}'".format(files)
                        )

            files.sort()

            ret = files

            del(files)

        finally:
            # TODO: commit 0_o?
            tags_object.commit()

    return ret

def get_category_by_id(cid):

    ret = None

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    q = index_db.sess.query(index_db.Category).filter_by(cid=cid).first()

    if q:
        ret = q.name

    return ret

def get_category_parent_by_id(cid):

    ret = None

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    q = index_db.sess.query(index_db.Category).filter_by(cid=cid).first()

    if q:
        ret = q.parent_cid

    return ret

def get_category_by_path(path):

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
            cat_dir = get_category_idname_dict(level)
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

def get_package_id(name):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(name=name).first()
    if q != None:
        ret = q.pid

    return ret

def get_package_category(pid):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(pid=pid).first()
    if q != None:
        ret = q.cid

    return ret

def get_package_category_by_name(name):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(name=name).first()
    if q != None:
        ret = q.cid

    return ret


def get_package_by_id(pid):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(pid=pid).first()
    if q != None:
        ret = q.name

    return ret


def get_package_name_list(cid=None):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    if cid == None:
        lst = index_db.sess.query(index_db.Package).all()
    else:
        lst = index_db.sess.query(index_db.Package).filter_by(cid=cid).all()

    lst_names = []
    for i in lst:
        lst_names.append(i.name)

    del(lst)

    lst_names.sort()

    return lst_names

def get_package_id_list(cid=None):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    lst = None
    if cid == None:
        lst = index_db.sess.query(index_db.Package).all()
    else:
        lst = index_db.sess.query(index_db.Package).filter_by(cid=cid).all()

    ids = []
    for i in lst:
        ids.append(i.pid)

    del(lst)

    return ids

def get_package_idname_dict(cid=None):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    if cid == None:
        lst = index_db.sess.query(index_db.Package).all()
    else:
        lst = index_db.sess.query(index_db.Package).filter_by(cid=cid).all()

    dic = {}
    for i in lst:
        dic[int(i.pid)] = i.name

    del(lst)

    return dic

def get_category_name_list(parent_cid=0):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    lst = index_db.sess.query(
        index_db.Category
        ).filter_by(
            parent_cid=parent_cid
            ).order_by(
                index_db.Category.name
                ).all()

    lst_names = []
    for i in lst:
        lst_names.append(i.name)

    del(lst)

    lst_names.sort()

    return lst_names

def get_category_id_list(parent_cid=0):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    lst = index_db.sess.query(
        index_db.Category
        ).filter_by(
            parent_cid=parent_cid
            ).order_by(
                index_db.Category.name
                ).all()

    ids = []
    for i in lst:
        ids.append(i.cid)

    del(lst)

    return ids

def get_category_idname_dict(parent_cid=0):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    lst = None
    if parent_cid == None:
        lst = index_db.sess.query(
            index_db.Category
            ).order_by(
                index_db.Category.name
                ).all()
    else:
        lst = index_db.sess.query(
            index_db.Category
            ).filter_by(
                parent_cid=parent_cid
                ).order_by(
                    index_db.Category.name
                    ).all()

    dic = {}
    for i in lst:
        dic[int(i.cid)] = i.name

    del(lst)

    return dic


def get_package_path(pid_or_name):

    if not isinstance(pid_or_name, int):
        pid_or_name = str(pid_or_name)

    pid = None
    if isinstance(pid_or_name, str):
        pid = get_package_id(pid_or_name)
    else:
        pid = int(pid_or_name)

    ret = []
    pkg = None

    if pid == None:
        logging.error("Error getting package `{}' data from DB".format(pid_or_name))
        logging.warning("Maybe it's not indexed")
        ret = None
    else:
        index_db = org.wayround.aipsetup.dbconnections.index_db()
        pkg = index_db.sess.query(index_db.Package).filter_by(pid=pid).first()

        if pkg != None :

            r = pkg.cid

            ret.insert(0, (pkg.pid, pkg.name))

            while r != 0:
                cat = index_db.sess.query(index_db.Category).filter_by(cid=r).first()
                ret.insert(0, (cat.cid, cat.name))
                r = cat.parent_cid

    return ret


def get_category_path(cid):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    ret = []
    categ = None

    if cid == None:
        logging.error(
            "Error getting category `{}' data from DB".format(
                cid
                )
            )
        ret = None
    else:
        categ = index_db.sess.query(index_db.Category).filter_by(cid=cid).first()

        if categ != None :

            r = categ.parent_cid

            ret.insert(0, (categ.cid, categ.name))

            while r != 0:
                cat = index_db.sess.query(index_db.Category).filter_by(cid=r).first()
                ret.insert(0, (cat.cid, cat.name))
                r = cat.parent_cid

    return ret


def get_package_path_string(pid_or_name):

    ret = None

    r = get_package_path(pid_or_name)

    if not isinstance(r, list):
        ret = None
    else:
        ret = join_pkg_path(r)
    return ret

def get_category_path_string(cid_or_name):

    ret = None

    r = get_category_path(cid_or_name)

    if not isinstance(r, list):
        ret = None
    else:
        ret = join_pkg_path(r)

    return ret


def create_category(name='name', parent_cid=0):

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    new_cat = index_db.Category(name=name, parent_cid=parent_cid)

    index_db.sess.add(new_cat)

    new_cat_id = new_cat.cid

    return new_cat_id


def _srfpac2_pkg_struct(pid, name, cid):
    return dict(pid=pid, name=name, cid=cid)

def _srfpac2_cat_struct(cid, name, parent_cid):
    return dict(cid=cid, name=name, parent_cid=parent_cid)

def _srfpac2_get_cat_by_cat_path(category_locations, cat_path):

    ret = None

    if cat_path in category_locations:
        ret = category_locations[cat_path]

    return ret

def scan_repo_for_pkg_and_cat():
    ret = 0

    repo_dir = os.path.abspath(
        org.wayround.aipsetup.config.config['repository']
        )

    category_locations = dict()
    package_locations = dict()

    last_cat_id = 0
    last_pkg_id = 0

    for root, dirs, files in os.walk(
        repo_dir
        ):


        if root == repo_dir:
            category_locations[''] = _srfpac2_cat_struct(
                cid=0,
                name='',
                parent_cid=None
                )

        else:
            relpath = os.path.relpath(root, repo_dir)

            if is_repo_package(root):

                parent_cat = _srfpac2_get_cat_by_cat_path(
                    category_locations,
                    os.path.dirname(relpath)
                    )
                parent_cat_id = parent_cat['cid']

                package_locations[relpath] = _srfpac2_pkg_struct(
                    pid=last_pkg_id,
                    name=os.path.basename(relpath),
                    cid=parent_cat_id
                    )
                last_pkg_id += 1

            else:

                already_listed_package = False
                for i in package_locations.keys():
                    if relpath.startswith(i):
                        already_listed_package = True
                        break

                if already_listed_package:
                    continue

                last_cat_id += 1

                parent_cat_name = os.path.dirname(relpath)

                parent_cat = _srfpac2_get_cat_by_cat_path(
                    category_locations,
                    parent_cat_name
                    )

                parent_cat_id = parent_cat['cid']

                category_locations[relpath] = _srfpac2_cat_struct(
                    cid=last_cat_id,
                    name=os.path.basename(relpath),
                    parent_cid=parent_cat_id
                    )

            org.wayround.utils.file.progress_write(
                "    scanning (found: {} categories, {} packages): {}".format(
                    len(category_locations.keys()),
                    len(package_locations.keys()),
                    relpath
                    )
                )

    org.wayround.utils.file.progress_write_finish()

#    print("Categories")
#    pprint.pprint(category_locations, indent=4)
#
#    print("Packages")
#    pprint.pprint(package_locations, indent=4)

    if ret == 0:
        ret = {'cats': category_locations, 'packs':package_locations}

    return ret

def detect_package_collisions(category_locations, package_locations):

    ret = 0

    lst_dup = {}
    pkg_paths = {}

    for each in package_locations.keys():

        l = package_locations[each]['name'].lower()

        if not l in pkg_paths:
            pkg_paths[l] = []

        pkg_paths[l].append(each)

    for each in package_locations.keys():

        l = package_locations[each]['name'].lower()

        if len(pkg_paths[l]) > 1:
            lst_dup[l] = pkg_paths[l]


    if len(lst_dup) == 0:
        logging.info(
            "Found {} duplicated package names. Package locations looks good!".format(
                len(lst_dup)
                )
            )
        ret = 0
    else:
        logging.warning(
            "Found {} duplicated package names\n        listing:".format(
                len(lst_dup)
                )
            )

        sorted_keys = list(lst_dup.keys())
        sorted_keys.sort()

        for each in sorted_keys:
            print("          {}:".format(each))

            lst_dup[each].sort()

            for each2 in lst_dup[each]:
                print("             {}".format(each2))
        ret = 1

    return ret

def save_cats_and_packs_to_db(category_locations, package_locations):

    ret = 0

    category_locations_internal = copy.copy(category_locations)

    del category_locations_internal['']

    index_db = org.wayround.aipsetup.dbconnections.index_db()

    logging.info("Deleting old data from DB")
    index_db.sess.query(index_db.Category).delete()
    index_db.sess.query(index_db.Package).delete()

    index_db.sess.commit()

    logging.info("Adding new data to DB")
    for i in category_locations_internal.keys():

        new_obj = index_db.Category()

        new_obj.cid = category_locations_internal[i]['cid']
        new_obj.name = category_locations_internal[i]['name']
        new_obj.parent_cid = category_locations_internal[i]['parent_cid']

        index_db.sess.add(new_obj)

    for i in package_locations.keys():

        new_obj = index_db.Package()

        new_obj.pid = package_locations[i]['pid']
        new_obj.name = package_locations[i]['name']
        new_obj.cid = package_locations[i]['cid']

        index_db.sess.add(new_obj)

    index_db.sess.commit()
    logging.info("DB saved")

    return ret

def create_required_dirs_at_package(path):

    ret = 0

    for i in ['pack']:
        full_path = path + os.path.sep + i

        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
            except:
                logging.exception("Can't make dir `{}'".format(full_path))
                ret = 3
            else:
                ret = 0
        else:
            if os.path.islink(full_path):
                logging.error("`{}' is link".format(full_path))
                ret = 4
            elif os.path.isfile(full_path):
                logging.error("`{}' is file".format(full_path))
                ret = 5
            else:
                ret = 0

        if ret != 0:
            break

    return ret

# TODO: deprecation required for this function
def join_pkg_path(pkg_path):
    lst = []

    for i in pkg_path:
        lst.append(i[1])

    ret = '/'.join(lst)

    return ret


def _index_progress(added_tags, sub_dir_name, root_dir_name_len):
    org.wayround.utils.file.progress_write(
        "    scanning (found {}): {}".format(
            added_tags,
            sub_dir_name[root_dir_name_len + 1:]
            )
        )

    return

def _index_sources_directory_to_list(
    list_buffer,
    root_dir_name,
    sub_dir_name,
    root_dir_name_len,
    acceptable_endings=None,
    added_tags=0
    ):

    sub_dir_name = os.path.abspath(sub_dir_name)

    added_tags = added_tags

    _index_progress(added_tags, sub_dir_name, root_dir_name_len)

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

            res = _index_sources_directory_to_list(
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

    _index_progress(added_tags, sub_dir_name, root_dir_name_len)


    return {'added_tags': added_tags}


def index_sources_directory(
    root_dir_name,
    sub_dir_name,
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

    _index_sources_directory_to_list(
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
        tags = get_sources_connection()
    except:
        logging.exception("Can't connect to source index DB")
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

            index = 0
            failed_count = 0
            skipped_count = 0
            logging.info("Loading DB to save new data")
            src_tag_objects = set(tags.get_objects())

            for i in source_index:
                index += 1

                if not force_reindex and i in src_tag_objects:

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
            src_tag_objects = tags.get_objects()
            deleted_count = 0
            found_scanned_count = 0
            skipped_count = 0
            for i in src_tag_objects:

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

def index_sources(subdir_name, force_reindex=False, first_delete_found=False):

    index_sources_directory(
        os.path.realpath(os.path.abspath(org.wayround.aipsetup.config.config['source'])),
        os.path.realpath(os.path.abspath(subdir_name)),
        org.wayround.aipsetup.config.config['acceptable_src_file_extensions'],
        force_reindex=force_reindex,
        first_delete_found=first_delete_found
        )

    return 0

def cleanup_repo_package_pack(name):

    g_path = org.wayround.aipsetup.config.config['garbage'] + os.path.sep + name

    if not os.path.exists(g_path):
        os.makedirs(g_path, exist_ok=True)

    path = (
        org.wayround.aipsetup.config.config['repository'] + os.path.sep +
        org.wayround.aipsetup.pkgindex.get_package_path_string(name) +
        os.path.sep + 'pack'
        )

    while r'//' in path:
        path.replace(r'//', '/')

    path = os.path.abspath(path)

    files = os.listdir(path)
    files.sort()

    for i in files:
        p1 = path + os.path.sep + i

        if os.path.exists(p1):

            org.wayround.aipsetup.package.put_file_to_index(
                path + os.path.sep + i
                )

    files = os.listdir(path)
    files.sort()

    for i in files:

        p1 = path + os.path.sep + i

        if os.path.exists(p1):

            p2 = g_path + os.path.sep + i

            if org.wayround.aipsetup.package.check_package(
                p1, True
                ) != 0:
                logging.warning(
                    "Wrong package, garbaging: `{}'\n\tas `{}'".format(p1, p2)
                    )
                try:
                    shutil.move(p1, p2)
                except:
                    logging.exception("Can't garbage")

    files = os.listdir(path)
    files.sort(
        key=functools.cmp_to_key(
            org.wayround.aipsetup.version.package_version_comparator
            ),

        reverse=True
        )

    if len(files) > 5:
        for i in files[5:]:
            p1 = path + os.path.sep + i

            logging.warning("Removing outdated package: {}".format(p1))
            try:
                os.unlink(p1)
            except:
                logging.exception("Error")


def cleanup_repo_package(name):

    g_path = org.wayround.aipsetup.config.config['garbage'] + os.path.sep + name

    if not os.path.exists(g_path):
        os.makedirs(g_path)

    path = (
        org.wayround.aipsetup.config.config['repository'] + os.path.sep +
        org.wayround.aipsetup.pkgindex.get_package_path_string(name)
        )

    while r'//' in path:
        path.replace(r'//', '/')

    path = os.path.abspath(path)

    create_required_dirs_at_package(path)

    files = os.listdir(path)

    for i in files:
        if not i in ['.package', 'pack']:

            p1 = path + os.path.sep + i
            p2 = g_path
            logging.warning(
                "moving `{}'\n\tto {}".format(
                    p1,
                    p2
                    )
                )
            try:
                shutil.move(p1, p2)
            except:
                logging.exception("Can't move file or dir")


def cleanup_repo():

    garbage_dir = org.wayround.aipsetup.config.config['garbage']

    if not os.path.exists(garbage_dir):
        os.makedirs(garbage_dir)

    logging.info("Getting packages information from DB")

    pkgs = get_package_idname_dict(None)

    logging.info("Scanning repository for garbage in packages")

    lst = list(pkgs.keys())
    lst.sort()
    lst_l = len(lst)
    lst_i = -1

    for i in lst:

        lst_i += 1
        perc = 0

        if lst_i == 0:
            perc = 0.0
        else:
            perc = 100.0 / (float(lst_l) / lst_i)

        org.wayround.utils.file.progress_write(
                "    {:6.2f}% (package {})".format(
                    perc,
                    pkgs[i]
                    )
            )

        cleanup_repo_package(pkgs[i])
        cleanup_repo_package_pack(pkgs[i])

    g_files = os.listdir(garbage_dir)

    for i in g_files:
        p1 = garbage_dir + os.path.sep + i
        if not os.path.islink(p1):
            if os.path.isdir(p1):
                if org.wayround.utils.file.isdirempty(p1):
                    try:
                        os.rmdir(p1)
                    except:
                        logging.exception("Error")

#        pkgs[i] = org.wayround.aipsetup.pkgindex.get_package_path_string(
#            i, index_db=index_db
#            )
