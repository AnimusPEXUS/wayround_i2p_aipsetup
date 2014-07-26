
"""
Facility for indexing and analyzing sources and packages repository
"""

import copy
import functools
import glob
import json
import logging
import os.path
import shutil

import sqlalchemy.ext.declarative

import org.wayround.aipsetup.package
import org.wayround.aipsetup.package_name_parser
import org.wayround.aipsetup.version
import org.wayround.utils.db
import org.wayround.utils.file
import org.wayround.utils.path
import org.wayround.utils.tag
import org.wayround.utils.tarball
import org.wayround.utils.terminal


class PackageRepo(org.wayround.utils.db.BasicDB):
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

    def __init__(self, config):

        org.wayround.utils.db.BasicDB.__init__(
            self,
            config,
            echo=False,
            create_all=True
            )

        return


class SourceRepo(org.wayround.utils.tag.TagEngine):
    pass


class SourcePathsRepo(org.wayround.utils.tag.TagEngine):
    pass


class PackageRepoCtl:

    def __init__(self, repository_dir, garbage_dir, db_connection):

        self._repository_dir = org.wayround.utils.path.abspath(repository_dir)
        self._garbage_dir = org.wayround.utils.path.abspath(garbage_dir)
        self._db_connection = db_connection

        return

    def get_repository_dir(self):
        return self._repository_dir

    def get_garbage_dir(self):
        return self._garbage_dir

    def get_db_connection(self):
        return self._db_connection

    def is_repo_package(self, path):

        """
        Check whatever path is [aipsetup package index] package
        """

        return (os.path.isdir(path)
            and os.path.isfile(
                os.path.join(path, '.package')
                )
            )

    def get_package_files(self, name):

        """
        Returns list of indexed package's asps
        """

        ret = 0

        pid = self.get_package_id(name)
        if pid == None:
            logging.error("Error getting package `{}' ID".format(name))
            ret = 1
        else:

            package_path = self.get_package_path_string(pid)

            if not isinstance(package_path, str):
                logging.error("Can't get path for package `{}'".format(pid))
                ret = 2
            else:

                package_dir = org.wayround.utils.path.abspath(
                    self._repository_dir
                    + os.path.sep + package_path + os.path.sep + 'pack'
                    )

                logging.debug(
                    "Looking for package files in `{}'".format(package_dir)
                    )

                files = glob.glob(os.path.join(package_dir, '*.asp'))

                needed_files = []

                for i in files:

                    parsed = org.wayround.aipsetup.package_name_parser.\
                        package_name_parse(i)

                    if parsed and parsed['groups']['name'] == name:
                        needed_files.append(
                            os.path.sep +
                            org.wayround.utils.path.relpath(
                                i,
                                self._repository_dir
                                )
                            )

                ret = needed_files

        return ret

    def get_category_by_id(self, cid):

        ret = None

        index_db = self._db_connection

        q = index_db.session.query(index_db.Category).filter_by(cid=cid).\
            first()

        if q:
            ret = q.name

        return ret

    def get_category_parent_by_id(self, cid):

        ret = None

        index_db = self._db_connection

        q = index_db.session.query(index_db.Category).filter_by(cid=cid).\
            first()

        if q:
            ret = q.parent_cid

        return ret

    def get_category_by_path(self, path):

        """
        In case of success, returns category id
        """

        if not isinstance(path, str):
            raise ValueError("`path' must be string")

        ret = 0
        if len(path) > 0:

            path_parsed = path.split('/')

            level = 0

            for i in path_parsed:

                cat_dir = self.get_category_idname_dict(level)

                found_cat = False
                for j in list(cat_dir.keys()):
                    if cat_dir[j] == i:
                        level = j
                        ret = j
                        found_cat = True
                        break

                if not found_cat:
                    ret = None
                    break

                if ret == None:
                    break

        return ret

    def get_package_id(self, name):

        index_db = self._db_connection

        ret = None

        q = index_db.session.query(index_db.Package).filter_by(name=name).\
            first()
        if q != None:
            ret = q.pid

        return ret

    def get_package_category(self, pid):

        index_db = self._db_connection

        ret = None

        q = index_db.session.query(index_db.Package).filter_by(pid=pid).first()
        if q != None:
            ret = q.cid

        return ret

    def get_package_category_by_name(self, name):

        index_db = self._db_connection

        ret = None

        q = index_db.session.query(index_db.Package).filter_by(name=name).\
            first()

        if q != None:
            ret = q.cid

        return ret

    def get_package_by_id(self, pid):

        index_db = self._db_connection

        ret = None

        q = index_db.session.query(index_db.Package).filter_by(pid=pid).first()
        if q != None:
            ret = q.name

        return ret

    def get_package_name_list(self, cid=None):

        index_db = self._db_connection

        if cid == None:
            lst = index_db.session.query(index_db.Package).all()
        else:
            lst = index_db.session.query(
                index_db.Package
                ).filter_by(cid=cid).all()

        lst_names = []
        for i in lst:
            lst_names.append(i.name)

        lst_names.sort()

        return lst_names

    def get_package_id_list(self, cid=None):

        index_db = self._db_connection

        lst = None
        if cid == None:
            lst = index_db.session.query(index_db.Package).all()
        else:
            lst = index_db.session.query(
                index_db.Package
                ).filter_by(cid=cid).all()

        ids = []
        for i in lst:
            ids.append(i.pid)

        return ids

    def get_package_idname_dict(self, cid=None):

        index_db = self._db_connection

        if cid == None:
            lst = index_db.session.query(index_db.Package).all()
        else:
            lst = index_db.session.query(
                index_db.Package
                ).filter_by(cid=cid).all()

        dic = {}
        for i in lst:
            dic[int(i.pid)] = i.name

        return dic

    def get_category_name_list(self, parent_cid=0):

        index_db = self._db_connection

        lst = index_db.session.query(
            index_db.Category
            ).filter_by(
                parent_cid=parent_cid
                ).order_by(
                    index_db.Category.name
                    ).all()

        lst_names = []
        for i in lst:
            lst_names.append(i.name)

        lst_names.sort()

        return lst_names

    def get_category_id_list(self, parent_cid=0):

        index_db = self._db_connection

        lst = index_db.session.query(
            index_db.Category
            ).filter_by(
                parent_cid=parent_cid
                ).order_by(
                    index_db.Category.name
                    ).all()

        ids = []
        for i in lst:
            ids.append(i.cid)

        return ids

    def get_category_idname_dict(self, parent_cid=0):

        """
        Return dict in which keys are ids and values are names
        """

        index_db = self._db_connection

        lst = None
        if parent_cid == None:
            lst = index_db.session.query(
                index_db.Category
                ).order_by(
                    index_db.Category.name
                    ).all()
        else:
            lst = index_db.session.query(
                index_db.Category
                ).filter_by(
                    parent_cid=parent_cid
                    ).order_by(
                        index_db.Category.name
                        ).all()

        dic = {}
        for i in lst:
            dic[int(i.cid)] = i.name

        return dic

    def get_package_path(self, pid_or_name):

        if not isinstance(pid_or_name, int):
            pid_or_name = str(pid_or_name)

        pid = None
        if isinstance(pid_or_name, str):
            pid = self.get_package_id(pid_or_name)
        else:
            pid = int(pid_or_name)

        ret = []
        pkg = None

        if pid == None:
            logging.error(
                "Error getting package `{}' data from DB".format(pid_or_name)
                )

            logging.warning("Maybe it's not indexed")
            ret = None

        else:
            index_db = self._db_connection
            pkg = index_db.session.query(
                index_db.Package
                ).filter_by(pid=pid).first()

            if pkg != None:

                r = pkg.cid

                ret.insert(0, (pkg.pid, pkg.name))

                while r != 0:
                    cat = index_db.session.query(
                        index_db.Category
                        ).filter_by(cid=r).first()

                    ret.insert(0, (cat.cid, cat.name))
                    r = cat.parent_cid

        return ret

    def get_category_path(self, cid):

        index_db = self._db_connection

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
            categ = index_db.session.query(
                index_db.Category
                ).filter_by(cid=cid).first()

            if categ != None:

                r = categ.parent_cid

                ret.insert(0, (categ.cid, categ.name))

                while r != 0:
                    cat = index_db.session.query(
                        index_db.Category
                        ).filter_by(cid=r).first()

                    ret.insert(0, (cat.cid, cat.name))
                    r = cat.parent_cid

        return ret

    def get_package_path_string(self, pid_or_name):

        ret = None

        r = self.get_package_path(pid_or_name)

        if not isinstance(r, list):
            ret = None
        else:
            ret = self._join_pkg_path(r)
        return ret

    def get_category_path_string(self, cid_or_name):

        ret = None

        r = self.get_category_path(cid_or_name)

        if not isinstance(r, list):
            ret = None
        else:
            ret = self._join_pkg_path(r)

        return ret

    # TODO: I don't like this function
    def _join_pkg_path(self, pkg_path):
        lst = []

        for i in pkg_path:
            lst.append(i[1])

        ret = '/'.join(lst)

        return ret

    def _srfpac_pkg_struct(self, pid, name, cid):
        return dict(pid=pid, name=name, cid=cid)

    def _srfpac_cat_struct(self, cid, name, parent_cid):
        return dict(cid=cid, name=name, parent_cid=parent_cid)

    def _srfpac_get_cat_by_cat_path(self, category_locations, cat_path):

        ret = None

        if cat_path in category_locations:
            ret = category_locations[cat_path]

        return ret

    def scan_repo_for_pkg_and_cat(self):
        ret = 0

        repo_dir = org.wayround.utils.path.abspath(
            self._repository_dir
            )

        category_locations = dict()
        package_locations = dict()

        last_cat_id = 0
        last_pkg_id = 0

        for os_walk_iter in os.walk(
            repo_dir
            ):

            if os_walk_iter[0] == repo_dir:
                category_locations[''] = self._srfpac_cat_struct(
                    cid=0,
                    name='',
                    parent_cid=None
                    )

            else:
                relpath = org.wayround.utils.path.relpath(
                    os_walk_iter[0],
                    repo_dir
                    )

                if self.is_repo_package(os_walk_iter[0]):

                    parent_cat = self._srfpac_get_cat_by_cat_path(
                        category_locations,
                        os.path.dirname(relpath)
                        )
                    parent_cat_id = parent_cat['cid']

                    package_locations[relpath] = self._srfpac_pkg_struct(
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

                    parent_cat = self._srfpac_get_cat_by_cat_path(
                        category_locations,
                        parent_cat_name
                        )

                    parent_cat_id = parent_cat['cid']

                    category_locations[relpath] = self._srfpac_cat_struct(
                        cid=last_cat_id,
                        name=os.path.basename(relpath),
                        parent_cid=parent_cat_id
                        )

                org.wayround.utils.terminal.progress_write(
                    "    scanning "
                    "(found: {} categories, {} packages): {}".format(
                        len(category_locations.keys()),
                        len(package_locations.keys()),
                        relpath
                        )
                    )

        org.wayround.utils.terminal.progress_write_finish()

        if ret == 0:
            ret = {'cats': category_locations, 'packs': package_locations}

        return ret

    def save_cats_and_packs_to_db(self, category_locations, package_locations):

        ret = 0

        category_locations_internal = copy.copy(category_locations)

        if '' in category_locations_internal:
            del category_locations_internal['']

        index_db = self._db_connection

        logging.info("Deleting old data from DB")
        index_db.session.query(index_db.Category).delete()
        index_db.session.query(index_db.Package).delete()

        index_db.session.commit()

        logging.info("Adding new data to DB")
        for i in category_locations_internal.keys():

            new_obj = index_db.Category()

            new_obj.cid = category_locations_internal[i]['cid']
            new_obj.name = category_locations_internal[i]['name']
            new_obj.parent_cid = category_locations_internal[i]['parent_cid']

            index_db.session.add(new_obj)

        for i in package_locations.keys():

            new_obj = index_db.Package()

            new_obj.pid = package_locations[i]['pid']
            new_obj.name = package_locations[i]['name']
            new_obj.cid = package_locations[i]['cid']

            index_db.session.add(new_obj)

        index_db.session.commit()
        logging.info("DB saved")

        return ret

    def create_required_dirs_at_package(self, path):

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

    def put_asps_to_index(self, files, move=False):

        """
        Put many asps to aipsetup package index

        Uses :func:`put_asp_to_index`
        """

        for i in files:
            if os.path.exists(i):
                self.put_asp_to_index(i, move=move)

        return 0

    def _put_asps_to_index(self, files, subdir, move=False):

        ret = 0

        repository_path = self._repository_dir

        for file in files:

            full_path = org.wayround.utils.path.abspath(
                repository_path + os.path.sep + subdir
                )

            if not os.path.exists(full_path):
                os.makedirs(full_path)

            if os.path.dirname(file) != full_path:

                action = 'Copying'
                if move:
                    action = 'Moving'

                logging.info(
                    "{} {}\n       to {}".format(
                        action,
                        os.path.basename(file), full_path
                        )
                    )

                sfile = full_path + os.path.sep + os.path.basename(file)
                if os.path.isfile(sfile):
                    os.unlink(sfile)
                if move:
                    shutil.move(file, full_path)
                else:
                    shutil.copy(file, full_path)

        return ret

    def put_asp_to_index(self, filename, move=False):

        """
        Moves file to aipsetup package index
        """

        ret = 0

        logging.info("Processing file `{}'".format(os.path.basename(filename)))

        if os.path.isdir(filename) or os.path.islink(filename):
            logging.error(
                "Wrong file type `{}'".format(filename)
                )
            ret = 10
        else:

            asp = org.wayround.aipsetup.package.ASPackage(filename)

            if asp.check_package(mute=True) == 0:
                parsed = org.wayround.aipsetup.package_name_parser.\
                    package_name_parse(
                        filename
                        )

                if not isinstance(parsed, dict):
                    logging.error(
                        "Can't parse file name {}".format(
                            os.path.basename(filename)
                            )
                        )
                    ret = 13
                else:
                    file = org.wayround.utils.path.abspath(filename)

                    files = [
                        file
                        ]

                    package_path = self.get_package_path_string(
                        parsed['groups']['name']
                        )

                    if not isinstance(package_path, str):
                        logging.error(
                            "Package path error `{}'".format(
                                parsed['groups']['name']
                                )
                            )
                        ret = 11
                    else:

                        path = package_path + os.path.sep + 'pack'

                        if not isinstance(path, str):
                            logging.error(
                                "Can't get package `{}' path string".format(
                                    parsed['groups']['name']
                                    )
                                )
                            ret = 12
                        else:
                            self._put_asps_to_index(files, path, move=move)

            else:

                logging.error(
                    "Action undefined for `{}'".format(
                        os.path.basename(filename)
                        )
                    )

        return ret

    def detect_package_collisions(
        self,
        category_locations, package_locations
        ):

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
                "Found {} duplicated package names. "
                "Package locations looks good!".format(
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

    def cleanup_repo_package_pack(self, name):

        g_path = org.wayround.utils.path.join(self._garbage_dir, name)

        if not os.path.exists(g_path):
            os.makedirs(g_path, exist_ok=True)

        path = org.wayround.utils.path.join(
            self._repository_dir,
            self.get_package_path_string(name), 'pack'
            )

        path = org.wayround.utils.path.abspath(path)

        self.create_required_dirs_at_package(org.wayround.utils.path.join(
            self._repository_dir,
            self.get_package_path_string(name)
            ))

        files = os.listdir(path)
        files.sort()

        for i in files:
            p1 = org.wayround.utils.path.join(path, i)

            if not os.path.isfile(p1) or os.path.islink(p1):
                logging.warning("Removing {}".format(p1))
                org.wayround.utils.file.remove_if_exists(p1)

        files = os.listdir(path)
        files.sort()

        for i in files:

            p1 = org.wayround.utils.path.join(path, i)

            if os.path.isfile(p1) and not os.path.islink(p1):

                if self.put_asp_to_index(p1) != 0:

                    logging.warning(
                        "Can't move file to index. moving to garbage"
                        )

                    shutil.move(p1, org.wayround.utils.path.join(g_path, i))

        files = os.listdir(path)
        files.sort()

        for i in files:

            p1 = path + os.path.sep + i

            if os.path.exists(p1):

                p2 = org.wayround.utils.path.join(g_path, i)

                pkg = org.wayround.aipsetup.package.ASPackage(p1)

                if pkg.check_package(True) != 0:
                    logging.warning(
                        "Wrong package, garbaging: `{}'\n\tas `{}'".format(
                            os.path.basename(p1),
                            p2
                            )
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

                logging.warning(
                    "Removing outdated package: {}".format(
                        os.path.basename(p1)
                        )
                    )
                try:
                    os.unlink(p1)
                except:
                    logging.exception("Error")

        return

    def cleanup_repo_package(self, name):

        g_path = org.wayround.utils.path.join(self._garbage_dir, name)

        if not os.path.exists(g_path):
            os.makedirs(g_path)

        path = org.wayround.utils.path.join(
            self._garbage_dir,
            self.get_package_path_string(name)
            )

        path = org.wayround.utils.path.abspath(path)

        self.create_required_dirs_at_package(path)

        files = os.listdir(path)

        for i in files:
            if not i in ['.package', 'pack']:

                p1 = org.wayround.utils.path.join(path, i)
                p2 = g_path
                logging.warning(
                    "moving `{}'\n\tto {}".format(
                        os.path.basename(p1),
                        p2
                        )
                    )

                try:
                    shutil.move(p1, p2)
                except:
                    logging.exception("Can't move file or dir")

    def cleanup_repo(self):

        garbage_dir = self._garbage_dir

        if not os.path.exists(garbage_dir):
            os.makedirs(garbage_dir)

        logging.info("Getting packages information from DB")

        pkgs = self.get_package_idname_dict(None)

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

            org.wayround.utils.terminal.progress_write(
                    "    {:6.2f}% (package {})".format(
                        perc,
                        pkgs[i]
                        )
                )

            self.cleanup_repo_package(pkgs[i])
            self.cleanup_repo_package_pack(pkgs[i])

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

        return

    def get_latest_pkg_from_repo(self, name, files=None):

        ret = None

        if not files:
            files = self.get_package_files(
                name
                )

        if not isinstance(files, list):
            files = []

        if len(files) == 0:
            ret = None
        else:

            ret = max(
                files,
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    )
                )

        return ret

    def build_category_tree(self, start_path=''):

        """
        Build category tree starting from ``start_path``

        Returns dict with category tree. where keys are paths and values are
        lists of packages
        """

        _id = self.get_category_by_path(start_path)

        all_ids = [_id]

        last_pos = 0
        last_len = len(all_ids)

        while True:

            for i in range(last_pos, last_len):
                all_ids += self.get_category_id_list(all_ids[i])

            _l = len(all_ids)

            if _l == last_len:
                break

            last_pos = last_len
            last_len = _l

        all_ids = set(all_ids)

        dic = {}

        for i in all_ids:
            cat_path = self.get_category_path_string(int(i))

            dic[cat_path] = self.get_package_name_list(int(i))

        return dic


class SourceRepoCtl:

    def __init__(self, sources_dir, database_connection):

        if not isinstance(database_connection, SourceRepo):
            raise ValueError(
                "database_connection must be of type "
                "org.wayround.aipsetup.repository.SourceRepo"
                )

        self.sources_dir = sources_dir
        self.database_connection = database_connection

    def index_sources(
        self,
        subdir_name,
        acceptable_src_file_extensions,
        force_reindex=False,
        first_delete_found=False,
        clean_only=False
        ):

        if not isinstance(acceptable_src_file_extensions, str):
            raise TypeError("`acceptable_src_file_extensions' must be str")

        ret = self._index_sources_directory(
            org.wayround.utils.path.realpath(self.sources_dir),
            org.wayround.utils.path.realpath(
                subdir_name
                ),
            acceptable_endings=acceptable_src_file_extensions.split(' '),
            force_reindex=force_reindex,
            first_delete_found=first_delete_found,
            clean_only=clean_only
            )

        return ret

    def _index_sources_directory(
        self,
        root_dir_name,
        sub_dir_name,
        acceptable_endings=None,
        force_reindex=False,
        first_delete_found=False,
        clean_only=False
        ):

        root_dir_name = org.wayround.utils.path.realpath(root_dir_name)

        sub_dir_name = org.wayround.utils.path.realpath(sub_dir_name)

        rel_path = org.wayround.utils.path.relpath(sub_dir_name, root_dir_name)
        rel_path = os.path.sep + rel_path + os.path.sep

        logging.debug("Root dir: {}".format(root_dir_name))
        logging.debug("Sub dir: {}".format(sub_dir_name))
        logging.debug("Rel dir: {}".format(rel_path))

        if rel_path == '/./':
            rel_path = ''

        added_count = 0

        if not clean_only:

            logging.info("Indexing {}...".format(root_dir_name))

            source_index = org.wayround.utils.file.files_recurcive_list(
                dirname=sub_dir_name,
                relative_to=root_dir_name,
                mute=False,
                acceptable_endings=acceptable_endings,
                sort=True,
                print_found=False,
                list_symlincs=False
                )

            source_index = org.wayround.utils.path.prepend_path(
                source_index,
                '/'
                )

            source_index = list(set(source_index))
            source_index.sort()

            found_count = len(source_index)

            logging.info("Found {} indexable objects".format(found_count))

            if first_delete_found:
                removed = 0
                logging.info("Removing found files from index")
                for i in source_index:
                    org.wayround.utils.terminal.progress_write(
                        "    removed {} of {}".format(removed, found_count)
                        )
                    self.database_connection.del_object_tags(i)
                    removed += 1

                self.database_connection.commit()

                org.wayround.utils.terminal.progress_write_finish()

            index = 0
            failed_count = 0
            skipped_count = 0
            logging.info("Loading DB to save new data")
            src_tag_objects = set(self.database_connection.get_objects())

            for i in source_index:
                index += 1

                if not force_reindex and i in src_tag_objects:

                    skipped_count += 1

                else:

                    parsed_src_filename = (
                        org.wayround.utils.tarball.\
                            parse_tarball_name(
                                i,
                                mute=True,
                                acceptable_source_name_extensions=(
                                    acceptable_endings
                                    )
                                )
                        )

                    if parsed_src_filename:
                        self.database_connection.set_tags(
                            i,
                            [parsed_src_filename['groups']['name']]
                            )
                        org.wayround.utils.terminal.progress_write(
                            "    added: {}\n".format(
                                os.path.basename(i)
                                )
                            )
                        added_count += 1
                    else:
                        org.wayround.utils.terminal.progress_write(
                            "    failed to parse: {}\n".format(
                                os.path.basename(i)
                                )
                            )
                        failed_count += 1

                org.wayround.utils.terminal.progress_write(
                    "    {} out of {} "
                    "({:.2f}%, added {}, failed {}, skipped {})".format(
                        index,
                        found_count,
                        (100.0 / (found_count / index)),
                        added_count,
                        failed_count,
                        skipped_count
                        )
                    )

            org.wayround.utils.terminal.progress_write_finish()

            del source_index

        self.database_connection.commit()
        logging.info("Searching non existing index items")
        src_tag_objects = self.database_connection.get_objects(order='object')
        deleted_count = 0
        found_scanned_count = 0
        skipped_count = 0
        src_tag_objects_l = len(src_tag_objects)
        i_i = 0
        to_deletion = []
        for i in src_tag_objects:

            logging.debug(
                "Checking possibility to skip {}".format(
                    os.path.sep + rel_path + os.path.sep
                    )
                )

            if i.startswith(rel_path):

                rp = org.wayround.utils.path.join(
                    root_dir_name, i
                    )

                if os.path.islink(rp) or not os.path.isfile(
                    org.wayround.utils.path.realpath(
                        rp
                        )
                    ):
                    to_deletion.append(i)
                    deleted_count += 1

                found_scanned_count += 1

            else:
                skipped_count += 1

            i_i += 1
            org.wayround.utils.terminal.progress_write(
                "    {:.2f}%, scanned {}, marked for "
                "deletion {}, skipped {}: {}".format(
                    100.0 / (float(src_tag_objects_l) / i_i),
                    found_scanned_count,
                    deleted_count,
                    skipped_count,
                    i
                    )
                )

        org.wayround.utils.terminal.progress_write_finish()

        self.database_connection.commit()

        self.database_connection.del_object_tags(to_deletion, False)

        self.database_connection.commit()

        logging.info(
            "Records: added {added}; deleted {deleted}".format(
                added=added_count,
                deleted=deleted_count
                )
            )
        logging.info(
            "DB Size: {} record(s)".format(self.database_connection.get_size())
            )

        return 0


class SourcePathsRepoCtl:

    def __init__(self, sources_paths_json_filename, database_connection):

        if not isinstance(database_connection, SourcePathsRepo):
            raise ValueError(
                "database_connection must be of type "
                "org.wayround.aipsetup.repository.SourcePathsRepo"
                )

        self.sources_paths_json_filename = sources_paths_json_filename
        self.database_connection = database_connection

    def load(self):

        f = open(self.sources_paths_json_filename)
        txt = f.read()
        f.close()

        data = json.loads(txt)

        self.database_connection.clear()

        for name in data.keys():

            for i in range(len(data[name]) - 1, -1, -1):
                if data[name][i] == '' or data[name][i].isspace():
                    del data[name][i]

            self.database_connection.set_tags(name, data[name])

        self.database_connection.commit()

        return

    def save(self):

        data = self.database_connection.get_objects_and_tags_dict()

        txt = json.dumps(
            data, sort_keys=True, indent=2
            )

        f = open(self.sources_paths_json_filename, 'w')
        f.write(txt)
        f.close()

        return
