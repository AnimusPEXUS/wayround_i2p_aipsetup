
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

import wayround_org.aipsetup.package
import wayround_org.aipsetup.package_name_parser
import wayround_org.aipsetup.version
import wayround_org.utils.db
import wayround_org.utils.file
import wayround_org.utils.path
import wayround_org.utils.tag
import wayround_org.utils.tarball
import wayround_org.utils.terminal


class PackageRepo(wayround_org.utils.db.BasicDB):

    """
    Main package index DB handling class
    """

    def init_table_mappings(self, init_table_data):

        class Package(self.decl_base):

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

        self.Package = Package

        class Category(self.decl_base):

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

        self.Category = Category

        return

    def get_mapped_package_table(self):
        ret = None
        if self.Package.__tablename__ in self.decl_base.metadata.tables:
            ret = self.decl_base.metadata.tables[self.Package.__tablename__]
        return ret

    def get_mapped_category_table(self):
        ret = None
        if self.Category.__tablename__ in self.decl_base.metadata.tables:
            ret = self.decl_base.metadata.tables[self.Category.__tablename__]
        return ret

    def create_tables(self):
        self.get_mapped_package_table().create(checkfirst=True)
        self.get_mapped_category_table().create(checkfirst=True)
        return


class SourceRepo(wayround_org.utils.tag.TagEngine):
    pass


class PackageRepoCtl:

    def __init__(self, repository_dir, garbage_dir, db_connection):

        self._repository_dir = wayround_org.utils.path.abspath(repository_dir)
        self._garbage_dir = wayround_org.utils.path.abspath(garbage_dir)
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
                wayround_org.utils.path.join(path, '.package')
                )
                )

    def get_package_hosts(self, name):

        ret = 0

        pid = self.get_package_id(name)
        if pid is None:
            logging.error("Error getting package `{}' ID".format(name))
            ret = 1
        else:

            package_path = self.get_package_path_string(pid)

            if not isinstance(package_path, str):
                logging.error("Can't get path for package `{}'".format(pid))
                ret = 2
            else:

                package_dir = wayround_org.utils.path.abspath(
                    wayround_org.utils.path.join(
                        self._repository_dir,
                        package_path,
                        'pack'
                        )
                    )

                if not os.path.isdir(package_dir):
                    # NOTE: not an error condition: absent dir means no files
                    ret = []

                else:

                    ret = []

                    files = os.listdir(package_dir)
                    files.sort()

                    for i in files:
                        if os.path.isdir(wayround_org.utils.path.join(package_dir, i)):
                            ret.append(i)

        return ret

    def get_package_host_archs(self, name, host):

        ret = 0

        pid = self.get_package_id(name)
        if pid is None:
            logging.error("Error getting package `{}' ID".format(name))
            ret = 1
        else:

            package_path = self.get_package_path_string(pid)

            if not isinstance(package_path, str):
                logging.error("Can't get path for package `{}'".format(pid))
                ret = 2
            else:

                package_dir = wayround_org.utils.path.abspath(
                    wayround_org.utils.path.join(
                        self._repository_dir,
                        package_path,
                        'pack',
                        host
                        )
                    )

                if not os.path.isdir(package_dir):
                    # NOTE: not an error condition: absent dir means no files
                    ret = []

                else:

                    ret = []

                    files = os.listdir(package_dir)
                    files.sort()

                    for i in files:
                        if os.path.isdir(wayround_org.utils.path.join(package_dir, i)):
                            ret.append(i)

        return ret

    def get_package_files(self, name, host, arch):
        """
        Returns list of indexed package's asps
        """

        ret = 0

        pid = self.get_package_id(name)
        if pid is None:
            logging.error("Error getting package `{}' ID".format(name))
            ret = 1
        else:

            package_path = self.get_package_path_string(pid)

            if not isinstance(package_path, str):
                logging.error("Can't get path for package `{}'".format(pid))
                ret = 2
            else:

                package_dir = wayround_org.utils.path.abspath(
                    wayround_org.utils.path.join(
                        self._repository_dir,
                        package_path,
                        'pack',
                        host,
                        arch
                        )
                    )

                if not os.path.isdir(package_dir):
                    # NOTE: not an error condition: absent dir means no files
                    ret = []

                else:
                    logging.debug(
                        "Looking for package files in `{}'".format(package_dir)
                        )

                    files = glob.glob(wayround_org.utils.path.join(package_dir, '*.asp'))

                    needed_files = []

                    for i in files:

                        if not os.path.isfile(i):
                            continue

                        parsed = wayround_org.aipsetup.package_name_parser.\
                            package_name_parse(i)

                        if (parsed
                                and parsed['groups']['name'] == name
                                and parsed['groups']['host'] == host
                                and parsed['groups']['arch'] == arch
                            ):
                            needed_files.append(
                                os.path.sep +
                                wayround_org.utils.path.relpath(
                                    i,
                                    self._repository_dir
                                    )
                                )

                    ret = needed_files

        return ret

    def get_category_by_id(self, cid):

        ret = None

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        q = session.query(index_db.Category).filter_by(cid=cid).first()

        if q:
            ret = q.name

        session.close()

        return ret

    def get_category_parent_by_id(self, cid):

        ret = None

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        q = session.query(index_db.Category).filter_by(cid=cid).first()

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

                if ret is None:
                    break

        return ret

    def get_package_id(self, name):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        ret = None

        q = session.query(index_db.Package).filter_by(name=name).all()

        len_q = len(q)

        if len_q > 1:
            logging.error(
                "More than one package with name `{}' found".format(name)
                )

            ret = None
        elif len_q == 0:
            logging.error(
                "Not found any packages with name `{}'".format(name)
                )
            ret = None
        else:
            ret = q[0].pid

        session.close()

        return ret

    def get_package_category(self, pid):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        ret = None

        q = session.query(index_db.Package).filter_by(pid=pid).first()

        if q is not None:
            ret = q.cid

        session.close()

        return ret

    def get_package_category_by_name(self, name):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        ret = None

        q = session.query(index_db.Package).filter_by(name=name).first()

        if q is not None:
            ret = q.cid

        session.close()

        return ret

    def get_package_by_id(self, pid):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        ret = None

        q = session.query(index_db.Package).filter_by(pid=pid).first()

        if q is not None:
            ret = q.name

        session.close()

        return ret

    def get_package_name_list(self, cid=None):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        if cid is None:
            lst = session.query(index_db.Package).all()
        else:
            lst = session.query(index_db.Package).filter_by(cid=cid).all()

        lst_names = []
        for i in lst:
            lst_names.append(i.name)

        lst_names.sort()

        session.close()

        return lst_names

    def get_package_id_list(self, cid=None):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        lst = None
        if cid is None:
            lst = session.query(index_db.Package).all()
        else:
            lst = session.query(index_db.Package).filter_by(cid=cid).all()

        ids = []
        for i in lst:
            ids.append(i.pid)

        session.close()

        return ids

    def get_package_idname_dict(self, cid=None):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        if cid is None:
            lst = session.query(index_db.Package).all()
        else:
            lst = session.query(index_db.Package).filter_by(cid=cid).all()

        dic = {}
        for i in lst:
            dic[int(i.pid)] = i.name

        session.close()

        return dic

    def package_reposition(self, pkg_name, new_subpath):

        ret = 0

        pps = self.get_package_path_string(pkg_name)

        if pps is not None:

            cur_pkg_path = os.path.abspath(
                wayround_org.utils.path.join(
                    self._repository_dir,
                    pps
                    )
                )

            new_pkg_path = os.path.abspath(
                wayround_org.utils.path.join(
                    self._repository_dir,
                    new_subpath
                    )
                )
        else:
            logging.error(
                "Invalid package name to move: {}".format(pkg_name)
                )
            ret = 3

        if ret == 0:
            if not wayround_org.utils.path.is_subpath_real(
                    new_pkg_path,
                    self._repository_dir
                    ):
                logging.error("Supplied subpath not under repository")
                ret = 1

        if ret == 0:
            if cur_pkg_path == wayround_org.utils.path.join(new_pkg_path, pkg_name):
                logging.error(
                    "Supplyed same subpath as currently is"
                    )
                ret = 2

        if ret == 0:

            npps = new_pkg_path.split('/')
            for i in range(len(npps)):

                npjap = wayround_org.utils.path.join(
                    '/', npps[:i + 1], '.package'
                    )

                if os.path.isfile(npjap):
                    logging.error(
                        "Discovered what there is a package under ne path:\n"
                        "{}\n"
                        "One package can not be placed under another package"
                        "".format(
                            npjap
                            )
                        )
                    ret = 5

        if ret == 0:
            try:
                os.makedirs(new_pkg_path, exist_ok=True)
            except:
                logging.exception("Some error")
                ret = 6

        if ret == 0:
            try:
                os.rename(
                    cur_pkg_path,
                    wayround_org.utils.path.join(new_pkg_path, pkg_name)
                    )
            except:
                logging.exception(
                    "Can't rename\n    `{}'\n    to\n    {}".format(
                        cur_pkg_path,
                        wayround_org.utils.path.join(new_pkg_path, pkg_name)
                        )
                    )
                ret = 7

        return ret

    def get_category_name_list(self, parent_cid=0):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        lst = session.query(index_db.Category.name)\
            .filter_by(parent_cid=parent_cid)\
            .order_by(index_db.Category.name)\
            .all()

        lst_names = []
        for i in lst:
            lst_names.append(i[0])

        session.close()

        return lst_names

    def get_category_id_list(self, parent_cid=0):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        lst = session.query(index_db.Category.cid)\
            .filter_by(parent_cid=parent_cid)\
            .order_by(index_db.Category.name).all()

        ids = []
        for i in lst:
            ids.append(i[0])

        session.close()

        return ids

    def get_category_idname_dict(self, parent_cid=0):
        """
        Return dict in which keys are ids and values are names
        """

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        lst = None
        if parent_cid is None:
            lst = session.query(index_db.Category)\
                .order_by(index_db.Category.name)\
                .all()
        else:
            lst = session.query(index_db.Category)\
                .filter_by(parent_cid=parent_cid)\
                .order_by(index_db.Category.name)\
                .all()

        dic = {}
        for i in lst:
            dic[int(i.cid)] = i.name

        session.close()

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

        if pid is None:
            logging.error(
                "Error getting package `{}' data from DB".format(pid_or_name)
                )

            logging.warning("Maybe it's not indexed")
            ret = None

        else:
            index_db = self._db_connection
            session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

            pkg = session.query(index_db.Package)\
                .filter_by(pid=pid)\
                .first()

            if pkg is not None:

                r = pkg.cid

                ret.insert(0, (pkg.pid, pkg.name))

                while r != 0:
                    cat = session.query(index_db.Category)\
                        .filter_by(cid=r)\
                        .first()

                    ret.insert(0, (cat.cid, cat.name))
                    r = cat.parent_cid

            session.close()

        return ret

    def get_category_path(self, cid):

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        ret = []
        categ = None

        if cid is None:
            logging.error(
                "Error getting category `{}' data from DB".format(
                    cid
                    )
                )
            ret = None
        else:
            categ = session.query(index_db.Category)\
                .filter_by(cid=cid)\
                .first()

            if categ is not None:

                r = categ.parent_cid

                ret.insert(0, (categ.cid, categ.name))

                while r != 0:
                    cat = session.query(index_db.Category)\
                        .filter_by(cid=r)\
                        .first()

                    ret.insert(0, (cat.cid, cat.name))
                    r = cat.parent_cid

        session.close()

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

    # TODO: I don't like this method
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

        repo_dir = wayround_org.utils.path.abspath(
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
                relpath = wayround_org.utils.path.relpath(
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

                wayround_org.utils.terminal.progress_write(
                    "    scanning "
                    "(found: {} categories, {} packages): {}".format(
                        len(category_locations.keys()),
                        len(package_locations.keys()),
                        relpath
                        )
                    )

        wayround_org.utils.terminal.progress_write_finish()

        if ret == 0:
            ret = {'cats': category_locations, 'packs': package_locations}

        return ret

    def save_cats_and_packs_to_db(self, category_locations, package_locations):

        ret = 0

        category_locations_internal = copy.copy(category_locations)

        if '' in category_locations_internal:
            del category_locations_internal['']

        index_db = self._db_connection
        session = sqlalchemy.orm.Session(index_db.decl_base.metadata.bind)

        logging.info("Deleting old data from DB")
        session.query(index_db.Category).delete()
        session.query(index_db.Package).delete()

        session.commit()

        logging.info("Adding new data to DB")
        for i in category_locations_internal.keys():

            new_obj = index_db.Category()

            new_obj.cid = category_locations_internal[i]['cid']
            new_obj.name = category_locations_internal[i]['name']
            new_obj.parent_cid = category_locations_internal[i]['parent_cid']

            session.add(new_obj)

        for i in package_locations.keys():

            new_obj = index_db.Package()

            new_obj.pid = package_locations[i]['pid']
            new_obj.name = package_locations[i]['name']
            new_obj.cid = package_locations[i]['cid']

            session.add(new_obj)

        session.commit()

        session.close()

        logging.info("DB saved")

        return ret

    def create_required_dirs_at_package(self, path):

        ret = 0

        for i in ['pack']:
            full_path = wayround_org.utils.path.join(path, i)

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

        for file1 in files:

            full_path = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(repository_path, subdir)
                )

            os.makedirs(full_path, exist_ok=True)

            if os.path.dirname(file1) != full_path:

                action = 'Copying'
                if move:
                    action = 'Moving'

                logging.info(
                    "{} {}\n       to {}".format(
                        action,
                        os.path.basename(file1), full_path
                        )
                    )

                sfile = full_path + os.path.sep + os.path.basename(file1)
                if os.path.isfile(sfile):
                    os.unlink(sfile)
                if move:
                    shutil.move(file1, full_path)
                else:
                    shutil.copy(file1, full_path)

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

            asp = wayround_org.aipsetup.package.ASPackage(filename)

            if asp.check_package(mute=True) == 0:
                parsed = wayround_org.aipsetup.package_name_parser.\
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
                    file1 = wayround_org.utils.path.abspath(filename)

                    files = [
                        file1
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

                        path = wayround_org.utils.path.join(
                            package_path,
                            'pack',
                            parsed['groups']['host'],
                            parsed['groups']['arch']
                            )

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

    def cleanup_repo_package_pack_host_arch(self, g_path, name, host, arch):

        path = wayround_org.utils.path.join(
            self._repository_dir,
            self.get_package_path_string(name),
            'pack',
            host,
            arch
            )

        self._ccc1(path, g_path)

        files = os.listdir(path)
        files.sort()

        for i in files:

            p1 = wayround_org.utils.path.join(path, i)

            if os.path.exists(p1):

                p2 = wayround_org.utils.path.join(g_path, i)

                pkg = wayround_org.aipsetup.package.ASPackage(p1)

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
                        logging.exception("Can't put to garbage")

        files = os.listdir(path)
        files.sort(
            key=functools.cmp_to_key(
                wayround_org.aipsetup.version.package_version_comparator
                ),
            reverse=True
            )

        if len(files) > 5:
            for i in files[5:]:
                p1 = wayround_org.utils.path.join(path, i)

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

    def cleanup_repo_package_pack_host(self, g_path, name, host):

        path = wayround_org.utils.path.join(
            self._repository_dir,
            self.get_package_path_string(name),
            'pack',
            host
            )

        self._ccc1(path, g_path)

        files = os.listdir(path)
        files.sort()

        for arch in files:
            if os.path.isdir(wayround_org.utils.path.join(path, arch)):
                self.cleanup_repo_package_pack_host_arch(
                    g_path,
                    name,
                    host,
                    arch
                    )

        return

    def _ccc1(self, path, g_path):

        files = os.listdir(path)
        files.sort()

        for i in files:
            p1 = wayround_org.utils.path.join(path, i)

            if os.path.islink(p1):
                logging.warning("Removing {}".format(p1))
                wayround_org.utils.file.remove_if_exists(p1)

        files = os.listdir(path)
        files.sort()

        for i in files:

            p1 = wayround_org.utils.path.join(path, i)

            if os.path.isfile(p1):

                if self.put_asp_to_index(p1, move=True) != 0:

                    logging.warning(
                        "Can't move file `{}' to index."
                        " moving to garbage".format(p1)
                        )

                    shutil.move(p1, wayround_org.utils.path.join(g_path, i))

            '''
            if os.path.isdir(p1) and remove_dirs:

                logging.warning(
                    "Can't move file to index. moving to garbage"
                    )

                shutil.move(p1, wayround_org.utils.path.join(g_path, i))
            '''

        return

    def cleanup_repo_package_pack(self, name):

        g_path = wayround_org.utils.path.join(self._garbage_dir, name)

        if not os.path.exists(g_path):
            os.makedirs(g_path, exist_ok=True)

        path = wayround_org.utils.path.join(
            self._repository_dir,
            self.get_package_path_string(name),
            'pack'
            )

        self.create_required_dirs_at_package(path)

        path = wayround_org.utils.path.abspath(path)

        self._ccc1(path, g_path)

        files = os.listdir(path)
        files.sort()

        for host in files:
            if os.path.isdir(wayround_org.utils.path.join(path, host)):
                self.cleanup_repo_package_pack_host(g_path, name, host)

        return

    def cleanup_repo_package(self, name):

        g_path = wayround_org.utils.path.join(self._garbage_dir, name)

        if not os.path.exists(g_path):
            os.makedirs(g_path)

        path = wayround_org.utils.path.join(
            self._garbage_dir,
            self.get_package_path_string(name)
            )

        path = wayround_org.utils.path.abspath(path)

        self.create_required_dirs_at_package(path)

        files = os.listdir(path)

        for i in files:
            if not i in ['.package', 'pack']:

                p1 = wayround_org.utils.path.join(path, i)
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

        return

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

            wayround_org.utils.terminal.progress_write(
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
                    if wayround_org.utils.file.isdirempty(p1):
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
                    wayround_org.aipsetup.version.package_version_comparator
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
                "wayround_org.aipsetup.repository.SourceRepo"
                )

        self.sources_dir = sources_dir
        self.src_db = database_connection

        return

    def index_sources(
            self,
            subdir_name,
            acceptable_src_file_extensions,
            force_reindex=False,
            first_delete_found=False,
            clean_only=False
            ):

        src_dir = wayround_org.utils.path.abspath(self.sources_dir)
        sub_src_dir = wayround_org.utils.path.abspath(subdir_name)

        ret = 0

        if (
                not (sub_src_dir + '/').startswith(src_dir + '/')
                or not os.path.isdir(
                    wayround_org.utils.path.abspath(subdir_name)
                    )):
            logging.error("Not a subdir of pkg_source: {}".format(subdir_name))
            ret = 1

        if ret == 0:

            ret = self._index_sources_directory(
                src_dir,
                sub_src_dir,
                acceptable_endings=acceptable_src_file_extensions,
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
        ''

        '''
        root_dir_name = wayround_org.utils.path.realpath(root_dir_name)
        sub_dir_name = wayround_org.utils.path.realpath(sub_dir_name)
        '''

        root_dir_name = wayround_org.utils.path.abspath(root_dir_name)
        sub_dir_name = wayround_org.utils.path.abspath(sub_dir_name)

        rel_path = wayround_org.utils.path.relpath(sub_dir_name, root_dir_name)
        rel_path = os.path.sep + rel_path + os.path.sep

        logging.debug("Root dir: {}".format(root_dir_name))
        logging.debug("Sub dir: {}".format(sub_dir_name))
        logging.debug("Rel dir: {}".format(rel_path))

        if rel_path == '/./':
            rel_path = ''

        added_count = 0

        if not clean_only:

            logging.info("Indexing {}...".format(root_dir_name))

            source_index = wayround_org.utils.file.files_recurcive_list(
                dirname=sub_dir_name,
                relative_to=root_dir_name,
                mute=False,
                acceptable_endings=acceptable_endings,
                sort=True,
                print_found=False,
                list_symlincs=False
                )

            source_index = wayround_org.utils.path.prepend_path(
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
                    wayround_org.utils.terminal.progress_write(
                        "    removed {} of {}".format(removed, found_count)
                        )
                    self.src_db.del_object_tags(i)
                    removed += 1

                self.src_db.commit()

                wayround_org.utils.terminal.progress_write_finish()

            index = 0
            failed_count = 0
            skipped_count = 0
            logging.info("Loading DB to save new data")
            src_tag_objects = set(self.src_db.get_objects())

            additions_memory = []

            for i in source_index:
                index += 1

                if not force_reindex and i in src_tag_objects:

                    skipped_count += 1

                else:

                    parsed_src_filename = (
                        wayround_org.utils.tarball.
                        parse_tarball_name(
                            i,
                            mute=True,
                            acceptable_source_name_extensions=(
                                acceptable_endings
                                )
                            )
                        )

                    if parsed_src_filename:
                        additions_memory.append(
                            (i, [parsed_src_filename['groups']['name']])
                            )
                        wayround_org.utils.terminal.progress_write(
                            "    adding: {}\n".format(
                                os.path.basename(i)
                                )
                            )
                        added_count += 1
                    else:
                        wayround_org.utils.terminal.progress_write(
                            "    failed to parse: {}\n".format(
                                os.path.basename(i)
                                )
                            )
                        failed_count += 1

                wayround_org.utils.terminal.progress_write(
                    "    {} out of {} "
                    "({:.2f}%, adding {}, failed {}, skipped {})".format(
                        index,
                        found_count,
                        (100.0 / (found_count / index)),
                        added_count,
                        failed_count,
                        skipped_count
                        )
                    )

            wayround_org.utils.terminal.progress_write_finish()

            del source_index

        logging.info("Committing additions..")
        self.src_db.set_many_objects_tags(
            additions_memory
            )

        del additions_memory

        logging.info("Searching non existing index items")

        src_tag_objects = self.src_db.get_objects()

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

                rp = wayround_org.utils.path.join(
                    root_dir_name, i
                    )

                if os.path.islink(rp) or not os.path.isfile(
                        wayround_org.utils.path.abspath(
                            rp
                            )
                        ):
                    '''
                    wayround_org.utils.path.realpath(
                        rp
                        )
                    ):
                    '''
                    to_deletion.append(i)
                    deleted_count += 1

                found_scanned_count += 1

            else:
                skipped_count += 1

            i_i += 1
            wayround_org.utils.terminal.progress_write(
                "    {:.2f}%, scanned {}, marked for "
                "deletion {}, skipped {}: {}".format(
                    100.0 / (float(src_tag_objects_l) / i_i),
                    found_scanned_count,
                    deleted_count,
                    skipped_count,
                    i
                    )
                )

        wayround_org.utils.terminal.progress_write_finish()

        self.src_db.del_object_tags(to_deletion, False)

        logging.info(
            "Records: added {added}; deleted {deleted}".format(
                added=added_count,
                deleted=deleted_count
                )
            )
        logging.info(
            "Source Data Base Size: {} record(s)".format(
                self.src_db.get_size())
            )

        return 0
