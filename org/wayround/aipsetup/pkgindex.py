
"""
Facility for indexing and analyzing sources and packages repository
"""

import os.path
import sys
import glob
import logging
import re

import sqlalchemy
import sqlalchemy.ext

import org.wayround.utils.db
import org.wayround.utils.tag

import org.wayround.aipsetup.config
import org.wayround.aipsetup.name

import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkgtags


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


def get_is_repo_package_dir(path):

    return (os.path.isdir(path)
        and os.path.isfile(
            os.path.join(path, '.package')
            )
        )

def get_package_files(name, index_db):

    pid = get_package_id(name, index_db=index_db)
    package_path = get_package_path_string(pid, index_db=index_db)

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

    return needed_files

def get_package_source_files(name, info_db=None):

    if info_db == None:
        raise ValueError("info_db can't be None")

    needed_files = []

    pkg_info = org.wayround.aipsetup.pkginfo.get_package_info_record(
        name=name, info_db=info_db
        )


    try:
        tags_object = org.wayround.aipsetup.pkgindex.get_sources_connection()
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

def get_category_by_id(cid, index_db):

    ret = None

    q = index_db.sess.query(index_db.Category).filter_by(cid=cid).first()

    if q:
        ret = q.name

    return ret

def get_category_parent_by_id(cid, index_db):

    ret = None

    q = index_db.sess.query(index_db.Category).filter_by(cid=cid).first()

    if q:
        ret = q.parent_cid

    return ret

def get_category_by_path(path, index_db):

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
            cat_dir = get_category_idname_dict(level, index_db=index_db)
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

def get_package_id(name, index_db):

    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(name=name).first()
    if q != None:
        ret = q.pid

    return ret

def get_package_category(pid, index_db):
    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(pid=pid).first()
    if q != None:
        ret = q.cid

    return ret

def get_package_category_by_name(name, index_db):
    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(name=name).first()
    if q != None:
        ret = q.cid

    return ret


def get_package_by_id(pid, index_db):

    ret = None

    q = index_db.sess.query(index_db.Package).filter_by(pid=pid).first()
    if q != None:
        ret = q.name

    return ret


def get_package_name_list(cid=None, index_db=None):

    if index_db == None:
        raise ValueError("index_db can't be None")

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

def get_package_id_list(cid=None, index_db=None):

    if index_db == None:
        raise ValueError("index_db can't be None")

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

def get_package_idname_dict(cid=None, index_db=None):

    if index_db == None:
        raise ValueError("index_db can't be None")

    if cid == None:
        lst = index_db.sess.query(index_db.Package).all()
    else:
        lst = index_db.sess.query(index_db.Package).filter_by(cid=cid).all()

    dic = {}
    for i in lst:
        dic[int(i.pid)] = i.name

    del(lst)

    return dic

def get_category_name_list(parent_cid=0, index_db=None):

    if index_db == None:
        raise ValueError("index_db can't be None")


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

def get_category_id_list(parent_cid=0, index_db=None):

    if index_db == None:
        raise ValueError("index_db can't be None")

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

def get_category_idname_dict(parent_cid=0, index_db=None):

    if index_db == None:
        raise ValueError("index_db can't be None")

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


def get_package_path(pid, index_db):

    ret = []
    pkg = None

    if pid != None:
        pkg = index_db.sess.query(index_db.Package).filter_by(pid=pid).first()
    else:
        raise ValueError("Error getting package data from DB")



    if pkg != None :

        r = pkg.cid

        ret.insert(0, (pkg.pid, pkg.name))

        while r != 0:
            cat = index_db.sess.query(index_db.Category).filter_by(cid=r).first()
            ret.insert(0, (cat.cid, cat.name))
            r = cat.parent_cid

    return ret


def get_category_path(cid, index_db):

    ret = []
    categ = None

    if cid != None:
        categ = index_db.sess.query(index_db.Category).filter_by(cid=cid).first()
    else:
        raise ValueError("Error getting category data from DB")

    if categ != None :

        r = categ.parent_cid

        ret.insert(0, (categ.cid, categ.name))

        while r != 0:
            cat = index_db.sess.query(index_db.Category).filter_by(cid=r).first()
            ret.insert(0, (cat.cid, cat.name))
            r = cat.parent_cid

    return ret


def get_package_path_string(pid, index_db):
    r = get_package_path(pid, index_db)
    ret = join_pkg_path(r)
    return ret

def get_category_path_string(cid, index_db):
    r = get_category_path(cid, index_db)
    ret = join_pkg_path(r)
    return ret

def get_package_collisions_in_db(index_db):

    ret = 0

    lst = index_db.sess.query(
        index_db.Package
        ).order_by(
            index_db.Package.name
            ).all()

    lst2 = []

    logging.info("Scanning paths")
    for each in lst:
        org.wayround.utils.file.progress_write('       {}'.format(each.name))
        lst2.append(get_package_path(pid=each.pid, index_db=index_db))

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
        ret = 0
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
        ret = 1

    return ret

def create_category(name='name', parent_cid=0, index_db=None):

    if index_db == None:
        raise ValueError("index_db can't be None")

    new_cat = index_db.Category(name=name, parent_cid=parent_cid)

    index_db.sess.add(new_cat)

    new_cat_id = new_cat.cid

    return new_cat_id


def _scan_repo_for_pkg_and_cat(root_dir, cid, index_db):

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

        if get_is_repo_package_dir(full_path):

            pa = index_db.Package(name=each, cid=cid)
            index_db.sess.add(pa)
            if sys.stdout.isatty():
                pcount = index_db.sess.query(index_db.Package).count()
                line_to_write = (
                    "       {} packages found: {}".format(pcount, pa.name)
                    )
                org.wayround.utils.file.progress_write(line_to_write)

            del(pa)

        elif os.path.isdir(full_path):

            new_cat = index_db.Category(name=each, parent_cid=cid)

            index_db.sess.add(new_cat)
            # TODO: comment commit or not?
            index_db.sess.commit()

            new_cat_cid = new_cat.cid

            del(new_cat)

            _scan_repo_for_pkg_and_cat(
                full_path, new_cat_cid, index_db
                )
        else:
            logging.warning("garbage file found: {}".format(full_path))

    return 0

def scan_repo_for_pkg_and_cat(index_db):

    ret = 0

    logging.info("Deleting old data")
    index_db.sess.query(index_db.Category).delete()
    index_db.sess.query(index_db.Package).delete()

    logging.info("Committing")
    index_db.sess.commit()

    logging.info("Scanning repository...")
    _scan_repo_for_pkg_and_cat(
        org.wayround.aipsetup.config.config['repository'],
        0,
        index_db=index_db
        )

    org.wayround.utils.file.progress_write_finish()
    index_db.sess.commit()

    logging.info("Searching for errors")
    get_package_collisions_in_db(index_db=index_db)
    logging.info("Search operations finished")

    return ret

def create_required_dirs_at_package(path):

    ret = 0

    # TODO: maybe it's time to remove aipsetup2 from here
    for i in ['pack', 'aipsetup2']:
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
    src_db,
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

def index_sources(subdir_name, force_reindex=False, first_delete_found=False):

    index_sources_directory(
        os.path.realpath(os.path.abspath(org.wayround.aipsetup.config.config['source'])),
        os.path.realpath(os.path.abspath(subdir_name)),
        get_sources_connection(),
        # TODO: move this list to config
        ['.tar.gz', '.tar.bz2', '.zip',
         '.7z', '.tgz', '.tar.xz', '.tar.lzma',
         '.tbz2'],
        force_reindex=force_reindex,
        first_delete_found=first_delete_found
        )

    return 0

