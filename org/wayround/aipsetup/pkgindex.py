
"""
Facility for indexing and analyzing sources and packages repository
"""

import os.path
import sys
import glob
import fnmatch
import copy
import logging


import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative


import org.wayround.utils.text
import org.wayround.utils.fileindex

import org.wayround.aipsetup.info
import org.wayround.aipsetup.config
import org.wayround.aipsetup.name


def exported_commands():
    return {
        'scan_repo_for_pkg_and_cat': pkgindex_scan_repo_for_pkg_and_cat,
        'find_repository_package_name_collisions_in_database': \
            pkgindex_find_repository_package_name_collisions_in_database,
        'find_missing_pkg_info_records': pkgindex_find_missing_pkg_info_records,
        'find_outdated_pkg_info_records': pkgindex_find_outdated_pkg_info_records,
        'update_outdated_pkg_info_records': pkgindex_update_outdated_pkg_info_records,
        'delete_pkg_info_records': pkgindex_delete_pkg_info_records,
        'backup_package_info_to_filesystem': pkgindex_backup_package_info_to_filesystem,
        'load_package_info_from_filesystem': pkgindex_load_package_info_from_filesystem,
        'list_pkg_info_records': pkgindex_list_pkg_info_records,
        'print_pkg_info_record': pkgindex_print_pkg_info_record,
        'index_sources': pkgindex_index_unicorn,
        }

def commands_order():
    return [
        'scan_repo_for_pkg_and_cat',
        'find_repository_package_name_collisions_in_database',
        'find_missing_pkg_info_records',
        'find_outdated_pkg_info_records',
        'update_outdated_pkg_info_records',
        'delete_pkg_info_records',
        'backup_package_info_to_filesystem',
        'load_package_info_from_filesystem',
        'list_pkg_info_records',
        'print_pkg_info_record',
        'index_sources'
        ]

def pkgindex_scan_repo_for_pkg_and_cat(opts, args):
    """
    Scan repository and save it's categories and packages indexes
    to database
    """

    r = PackageDatabase()
    ret = r.scan_repo_for_pkg_and_cat()

    return ret

def pkgindex_find_repository_package_name_collisions_in_database(opts, args):
    """
    Scan index for equal package names
    """
    r = PackageDatabase()
    ret = r.find_repository_package_name_collisions_in_database()

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
    r = PackageDatabase()
    ret = r.find_outdated_pkg_info_records()

    return ret

def pkgindex_update_outdated_pkg_info_records(opts, args):
    """
    Loads pkg info records which differs to FS .xml files
    """
    r = PackageDatabase()
    ret = r.update_outdated_pkg_info_records()

    return ret

def pkgindex_delete_pkg_info_records(opts, args):
    """
    If mask must be given or operation will fail
    """
    mask = None

    ret = 0

    if len(args) > 0:
        mask = args[0]

    if mask != None:
        r = PackageDatabase()
        ret = r.delete_pkg_info_records(mask)
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

    f = '-f' in opts

    r = PackageDatabase()
    ret = r.backup_package_info_to_filesystem(mask, f)

    return ret

def pkgindex_load_package_info_from_filesystem(opts, args):
    """
    Load missing package information from named files

    [-a] [file names]

    If no files listed - assume all files in info dir

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
    ret = r.list_pkg_info_records(mask)

    return ret

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
    else:
        logging.error("Name is not given")
        ret = 1

    return ret


def pkgindex_index_unicorn(opts, args):
    """
    Create sources and repositories indexes
    """
    index_unicorn()


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
        full_path = path + '/' + i

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

def index_unicorn():
    index_directory(org.wayround.aipsetup.config.config['source'],
                    org.wayround.aipsetup.config.config['source_index'],
                    # TODO: move this list to config
                    ['.tar.gz', '.tar.bz2', '.zip',
                     '.7z', '.tgz', '.tar.xz', '.tar.lzma',
                     '.tbz2'])

    # I came to conclusion, what whe don't need package indexing
    # because package repository can be too big.
    # Better to use pkgindex database and search on user action
    #
    #    index_directory(org.wayround.aipsetup.config.config['repository'],
    #                    org.wayround.aipsetup.config.config['repository_index'],
    #                    ['.asp'])




def _index_directory(f, root_dir, root_dirl, acceptable_endings=None):

    files = os.listdir(root_dir)
    files.sort()

    org.wayround.utils.file.progress_write("Scanning: {}".format(root_dir))

    for each in files:
        if each in ['.', '..']:
            continue

        full_path = os.path.join(root_dir, each)

        if os.path.islink(full_path):
            continue

        if not each[0] == '.' and os.path.isdir(full_path):
            _index_directory(f, full_path, root_dirl, acceptable_endings)

        elif not each[0] == '.' and os.path.isfile(full_path):

            if isinstance(acceptable_endings, list):

                match_found = False

                for i in acceptable_endings:
                    if each.endswith(i):
                        match_found = True
                        break

                if not match_found:
                    continue


            p = full_path[root_dirl:]
            f.add('%(name)s' % {
                    'name': p
                    })



def index_directory(
    dir_name,
    db_connection,
    acceptable_endings=None
    ):

    dir_name = os.path.abspath(dir_name)
    dir_namel = len(dir_name)

    logging.info("indexing %(dir)s..." % {'dir': dir_name})

    try:
        f = org.wayround.utils.fileindex.FileIndexer(db_connection)
    except:
        logging.exception("Can't open db `{}'".format(db_connection))
        raise
    else:

        try:
            _index_directory(f, dir_name, dir_namel, acceptable_endings)

            f.delete_missing(dir_name)

            f.commit()

            logging.info(
                "Records: added {added}; remained {skipped}; deleted {deleted}".format(
                    added=f.added_count,
                    skipped=f.exists_count,
                    deleted=f.deleted_count,
                    )
                )
            logging.info("DB Size: {}".format(f.get_size()))
        finally:
            f.close()

    return 0


def get_package_info(name):

    db = PackageDatabase()
    ret = db.package_info_record_to_dict(name)

    return ret

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
            sqlalchemy.Unicode(256),
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
            sqlalchemy.Unicode(256),
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
            sqlalchemy.Unicode(256),
            nullable=False,
            primary_key=True,
            default=''
            )

        home_page = sqlalchemy.Column(
            sqlalchemy.Unicode(256),
            nullable=False,
            default=''
            )

        description = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        pkg_name_type = sqlalchemy.Column(
            sqlalchemy.Unicode(256),
            nullable=False,
            default=''
            )

        buildinfo = sqlalchemy.Column(
            sqlalchemy.Unicode(256),
            nullable=False,
            default=''
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
            'name',
            sqlalchemy.Unicode(256),
            nullable=False
            )

        tag = sqlalchemy.Column(
            'tag',
            sqlalchemy.Unicode(256),
            nullable=False
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

    # TODO: Do I need this?
    #def __del__(self):
        #del(self._db_engine)

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

    def get_category_by_name(self, name='name'):

        lst = self.sess.query(self.Category).filter_by(name=name).all()

        return lst

    def get_category_by_id(self, cid=0):

        lst = self.sess.query(self.Category).filter_by(cid=cid).all()

        return lst

    def get_package_id(self, name):

        ret = None

        q = self.sess.query(self.Package).filter_by(name=name).first()
        if q != None:
            ret = q.pid

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

        print("")
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

        for i in tags:
            n = self.PackageTag()
            n.name = name
            n.tag = i
            self.sess.add(n)

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
        print("")

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

            tags = self.get_package_tags(q.name)

            ret = {
                'homepage'     : q.home_page,
                'description'  : q.description,
                'pkg_name_type': q.pkg_name_type,
                'tags'         : tags,
                'buildinfo'    : q.buildinfo
                }

        return ret


    def package_info_dict_to_record(self, name, struct):

        # TODO: check_info_dict(struct)

        q = self.sess.query(self.PackageInfo).filter_by(name=name).first()

        creating_new = False
        if q == None:
            q = self.PackageInfo()
            creating_new = True

        q.name = name
        q.description = struct['description']
        q.home_page = struct['homepage']
        q.pkg_name_type = struct['pkg_name_type']
        q.buildinfo = struct['buildinfo']

        # category set only through pkg_repository
        # q.category    = category

        if creating_new:
            self.sess.add(q)


        self.set_package_tags(name, struct['tags'])
        self.commit_session()

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
        self, filenames=[], all_records=False
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
        logging.info("searching missing records")
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

            if not all_records:
                q = self.sess.query(self.PackageInfo).filter_by(
                    name=name
                    ).first()
                if q == None:
                    missing.append(i)
            else:
                missing.append(i)

        print("")

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
        print("")

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
        self, create_templates=False, force_rewrite=False):

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

    def find_outdated_pkg_info_records(self, mute=False):

        ret = []

        q = self.sess.query(self.PackageInfo).order_by(self.PackageInfo.name).all()

        for i in q:

            filename = os.path.join(
                self._config['info'],
                '%(name)s.xml' % {'name': i.name}
                )

            if not os.path.exists(filename):
                ret.append(i.name)
                if not mute:
                    logging.warning("file missing: %(name)s" % {
                        'name': filename
                        })
                continue

            d1 = org.wayround.aipsetup.info.read_from_file(filename)

            if not isinstance(d1, dict):
                logging.info("Error parsing file: %(name)s" % {
                    'name': filename
                    })
            else:
                d2 = self.package_info_record_to_dict(record=i)
                if not org.wayround.aipsetup.info.is_info_dicts_equal(d1, d2):
                    ret.append(i.name)
                    if not mute:
                        logging.warning("xml init file differs for: %(name)s" % {
                            'name': i.name
                            })

        if not mute:
            logging.info("Total %(n)d warnings" % {'n': len(ret)})

        return ret

    def update_outdated_pkg_info_records(self):
        # find_missing_pkg_info_records

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
            all_records=True
            )


        return


    def print_pkg_info_record(self, name):
        r = self.package_info_record_to_dict(name=name)
        if r == None:
            logging.error("Not found named info record")
        else:

            pid = self.get_package_id(name)
            if pid != None:
                category = self.get_package_path_string(pid)
            else:
                category = "< Package not indexed! >"

            regexp = '< Wrong regexp type name >'
            if r['pkg_name_type'] in org.wayround.aipsetup.name.NAME_REGEXPS:
                regexp = org.wayround.aipsetup.name.NAME_REGEXPS[r['pkg_name_type']]

            print("""\
+---[{name}]---------------------------------+
 file name type: {pkg_name_type}
filename regexp: {regexp}
      buildinfo: {buildinfo}
       homepage: {homepage}
       category: {category}
           tags: {tags}
+---[{name}]---------------------------------+

{description}

+---[{name}]---------------------------------+
""".format_map(
        {
        'name'         : name,
        'homepage'     : r['homepage'],
        'pkg_name_type': r['pkg_name_type'],
        'regexp'       : regexp,
        'description'  : r['description'],
        'tags'         : ', '.join(r['tags']),
        'category'     : category,
        'buildinfo'    : r['buildinfo']
        }
        )
    )
