# -*- coding: utf-8 -*-

"""
This is LUST durectory indexing tool

Helps to create index of repository and packages
info
"""

import os
import os.path
import sys
import fnmatch
import glob


import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative


import aipsetup.info
import aipsetup.utils.text


def print_help():
    print """\
aipsetup pkgindex command

Where command is one of:

   scan_repo_for_pkg_and_cat

       Scan repository and save it's categories and packages indexes
       to database

   find_repository_package_name_collisions_in_database

       Scan index for equal package names

   find_missing_pkg_info_records [-t] [-f]

       Search packages which have no corresponding info records

       -t creates non-existing .xml file templates in info dir

       -f forces rewrite existing .xml files

   load_package_info_from_filesystem [-a] [file names]

       Load missing package information from named files. If no files
       listed - assume all files in info dir

       -a force load all records, not only missing.

   find_outdated_pkg_info_records

       Finds pkg info records which differs to FS .xml files

   update_outdated_pkg_info_records

       Loads pkg info records which differs to FS .xml files

   backup_package_info_to_filesystem [-f] [MASK]

       Save package information from database to info directory.

       Existing files are skipped, unless -f is set

   delete_pkg_info_records MASK

       If mask must be given or operation will fail

   list_pkg_info_records [MASK]

       Default MASK is *

   print_pkg_info_record NAME

       Print package info record information
"""

def router(opts, args, config):

    ret = 0

    args_l = len(args)

    if args_l == 0:
        print "-e- No command given"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()

        elif args[0] == 'scan_repo_for_pkg_and_cat':
            # scan repository for packages and categories. result
            # replaces data in database
            r = PackageDatabase(config)
            r.scan_repo_for_pkg_and_cat()

        elif args[0] == 'find_repository_package_name_collisions_in_database':
            # search database package table for collisions: no more
            # when one package with same name can exist!
            r = PackageDatabase(config)
            r.find_repository_package_name_collisions_in_database()

        elif args[0] == 'find_missing_pkg_info_records':
            t = False
            for i in opts:
                if i[0] == '-t':
                    t = True
                    break

            f = False
            for i in opts:
                if i[0] == '-f':
                    f = True
                    break

            r = PackageDatabase(config)
            r.find_missing_pkg_info_records(t, f)

        elif args[0] == 'find_outdated_pkg_info_records':
            r = PackageDatabase(config)
            r.find_outdated_pkg_info_records()

        elif args[0] == 'update_outdated_pkg_info_records':
            r = PackageDatabase(config)
            r.update_outdated_pkg_info_records()

        elif args[0] == 'backup_package_info_to_filesystem':
            mask = '*'

            if args_l > 1:
                mask = aipsetup.utils.text.unicodify(args[1])

            f = False
            for i in opts:
                if i[0] == '-f':
                    f = True
                    break

            r = PackageDatabase(config)
            r.backup_package_info_to_filesystem(mask, f)

        elif args[0] == 'load_package_info_from_filesystem':

            file_list = aipsetup.utils.text.unicodify(args[1:])

            a = False
            for i in opts:
                if i[0] == '-a':
                    a = True

            if len(file_list) == 0:
                file_list = aipsetup.utils.text.unicodify(
                    glob.glob(os.path.join(config['info'], '*.xml'))
                    )

            r = PackageDatabase(config)
            r.load_package_info_from_filesystem(file_list, a)


        elif args[0] == 'delete_pkg_info_records':

            mask = None

            if args_l > 1:
                mask = aipsetup.utils.text.unicodify(args[1])

            if mask != None:

                r = PackageDatabase(config)
                r.delete_pkg_info_records(mask)
            else:
                print "-e- Mask is not given"

        elif args[0] == 'list_pkg_info_records':

            mask = '*'

            if args_l > 1:
                mask = aipsetup.utils.text.unicodify(args[1])


            r = PackageDatabase(config)
            r.list_pkg_info_records(mask)


        elif args[0] == 'print_pkg_info_record':
            name = None

            if args_l > 1:
                name = aipsetup.utils.text.unicodify(args[1])

            if name != None:

                r = PackageDatabase(config)
                r.print_pkg_info_record(name)
            else:
                print "-e- Name is not given"

        else:
            print "wrong aipsetup command. try `aipsetup pkgindex help'"
            ret = 1


    return ret


def is_repo_package_dir(path):
    return os.path.isdir(path) \
        and os.path.isfile(
            os.path.join(path, '.package')
            )


def get_package_path(config, name):
    ret = None
    r = PackageDatabase(config)
    pid = r.get_package_id(name)
    if pid == None:
        print "-e- Can't get `%(package)s' from database" % {
            'package': name
            }
        ret = None
    else:
        ret = r.get_package_path_string(pid)
    del(r)
    return ret

def create_required_dirs_at_package(path):

    ret = 0

    for i in ['pack', 'source']:
        full_path = path + '/' + i

        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
            except:
                print "-e- Can't make dir `%(name)s'" % {
                    'name': full_path
                    }
                ret = 3
            else:
                ret = 0
        else:
            if os.path.islink(full_path):
                print "-e- `%(name)s' is link" % {
                    'name': full_path
                    }
                ret = 4
            elif os.path.isfile(full_path):
                print "-e- `%(name)s' is file" % {
                    'name': full_path
                    }
                ret = 5
            else:
                ret = 0

        if ret != 0:
            break

    return ret


def join_pkg_path(pkg_path):
    ret = ''
    lst = []

    for i in pkg_path:
        lst.append(i[1])

    ret = '/'.join(lst)

    return ret


class PackageDatabase:
    """
    Main package index DB handling class
    """

    Base = sqlalchemy.ext.declarative.declarative_base()

    class Package(Base):
        """
        Package class

        There can be many packages with same name, but this
        is only for tucking down duplicates and radicate
        them.
        """

        __tablename__ = 'package'

        pid = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True,
                                autoincrement=True)

        name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                 nullable=False,
                                 default=u'')

        cid = sqlalchemy.Column(sqlalchemy.Integer,
                                nullable=False,
                                default=0)


    class Category(Base):
        """
        Class for package categories

        There can be categories with same names
        """

        __tablename__ = 'category'

        cid = sqlalchemy.Column(sqlalchemy.Integer,
                                primary_key=True,
                                autoincrement=True)

        name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                 nullable=False,
                                 default=u'')

        parent_cid = sqlalchemy.Column(sqlalchemy.Integer,
                                       nullable=False,
                                       default=0)

    class PackageInfo(Base):
        """
        Class for holding package information
        """
        __tablename__ = 'package_info'

        name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                 nullable=False,
                                 primary_key=True,
                                 default=u'')

        home_page = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                      nullable=False,
                                      default=u'')

        description = sqlalchemy.Column(sqlalchemy.UnicodeText,
                                        nullable=False,
                                        default=u'')

        pkg_name_type = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                          nullable=False,
                                          default=u'')

        buildinfo = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                      nullable=False,
                                      default=u'')


    class PackageSource(Base):
        """
        Class for package's sources URLs
        """

        __tablename__ = 'package_source'

        id = sqlalchemy.Column(sqlalchemy.Integer,
                               nullable=False,
                               primary_key=True,
                               autoincrement=True)

        name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                 nullable=False)

        url = sqlalchemy.Column(sqlalchemy.UnicodeText,
                                nullable=False,
                                default=u'')



    class PackageMirror(Base):
        """
        Class for package's mirror URLs
        """

        __tablename__ = 'package_mirror'

        id = sqlalchemy.Column(sqlalchemy.Integer,
                               nullable=False,
                               primary_key=True,
                               autoincrement=True)

        name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                 nullable=False)

        url = sqlalchemy.Column(sqlalchemy.Text,
                                nullable=False,
                                default=u'')


    class PackageTag(Base):
        """
        Class for package's tags
        """

        __tablename__ = 'package_tag'

        id = sqlalchemy.Column(sqlalchemy.Integer,
                               nullable=False,
                               primary_key=True,
                               autoincrement=True)

        name = sqlalchemy.Column('name',
                                 sqlalchemy.Unicode(256),
                                 nullable=False)

        tag = sqlalchemy.Column('tag',
                                sqlalchemy.Unicode(256),
                                nullable=False)


    def __init__(self, config):

        self._config = config

        if not os.path.isdir(self._config['repository']):
            raise Exception

        db_echo = False

        self._db_engine = \
            sqlalchemy.create_engine(
            self._config['sqlalchemy_engine_string'],
            echo=db_echo
            )

        self.Base.metadata.bind = self._db_engine

        self.Base.metadata.create_all()

    #def __del__(self):
        #del(self._db_engine)


    def create_category(self, name='name', parent_cid=0):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        new_cat = self.Category(name=name, parent_cid=parent_cid)

        sess.add(new_cat)
        sess.commit()

        new_cat_id = new_cat.cid

        sess.close()

        return new_cat_id

    def get_category_by_name(self, name='name'):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        lst = sess.query(self.Category).filter_by(name=name).all()

        sess.close()

        return lst

    def get_category_by_id(self, cid=0):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        lst = sess.query(self.Category).filter_by(cid=cid).all()

        sess.close()

        return lst

    def get_package_id(self, name):

        ret = None

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.Package).filter_by(name=name).first()
        if q != None:
            ret = q.pid

        sess.close()

        return ret


    def ls_packages(self, cid=None):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        if cid == None:
            lst = sess.query(self.Package).all()
        else:
            lst = sess.query(self.Package).filter_by(cid=cid).all()

        sess.close()

        return lst


    def ls_categories(self, parent_cid=0):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        lst = sess.query(self.Category).filter_by(parent_cid=parent_cid).all()

        sess.close()

        return lst

    def _scan_repo_for_pkg_and_cat(self, sess, root_dir, cid):

        ld = os.listdir(root_dir)

        files = aipsetup.utils.text.unicodify(ld)

        files.sort()

        isfiles = 0

        for each in files:
            full_path = os.path.join(root_dir, each)

            if not os.path.isdir(full_path):
                isfiles += 1

        if isfiles >= 3:
            print "-w- too many non-dirs : %(path)s" % {
                'path': root_dir
                }
            print "       skipping"

            return 1

        for each in files:
            if each in ['.', '..']:
                continue

            full_path = os.path.join(root_dir, each)

            if os.path.islink(full_path):
                continue

            if is_repo_package_dir(full_path):
                sess.add(self.Package(name=each, cid=cid))
                sess.commit()
            elif os.path.isdir(full_path):
                new_cat = self.Category(name=each, parent_cid=cid)

                sess.add(new_cat)
                sess.commit()

                self._scan_repo_for_pkg_and_cat(
                    sess, full_path, new_cat.cid)
            else:
                print "-w- garbage file found: %(path)s" % {
                    'path': full_path
                    }

        return 0

    def scan_repo_for_pkg_and_cat(self):

        ret = 0

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        print "-i- deleting old data"
        sess.query(self.Category).delete()
        sess.query(self.Package).delete()

        print "-i- commiting"
        sess.commit()

        print "-i- scanning..."
        self._scan_repo_for_pkg_and_cat(
            sess, self._config['repository'], 0)

        count_p = sess.query(self.Package).count()

        print "-i- %(n)d packages found" % {'n': count_p}

        print "-i- closing."
        sess.close()

        return ret

    def get_package_tags(self, name):
        ret = []
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.PackageTag).filter_by(name = name).all()

        for i in q:
            ret.append(i.tag)

        sess.close()
        return ret

    def get_package_sources(self, name):
        ret = []
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.PackageSource).filter_by(name = name).all()

        for i in q:
            ret.append(i.url)

        sess.close()
        return ret

    def get_package_mirrors(self, name):
        ret = []
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.PackageMirror).filter_by(name = name).all()

        for i in q:
            ret.append(i.url)

        sess.close()
        return ret

    def set_package_tags(self, name, tags):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        sess.query(self.PackageTag).filter_by(name=name).delete()

        for i in tags:
            n = self.PackageTag(name, i)
            sess.add(n)

        sess.commit()
        sess.close()

    def set_package_sources(self, name, sources):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        sess.query(self.PackageSource).filter_by(name=name).delete()

        for i in sources:
            n = self.PackageSource(name, i)
            sess.add(n)

        sess.commit()
        sess.close()

    def set_package_mirrors(self, name, mirrors):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        sess.query(self.PackageMirror).filter_by(name=name).delete()

        for i in mirrors:
            n = self.PackageMirror(name, i)
            sess.add(n)

        sess.commit()
        sess.close()

    def get_package_path(self, pid):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        ret = []
        pkg = None

        if pid != None:
            pkg = sess.query(self.Package).filter_by(pid=pid).first()
        else:
            raise ValueError

        # print "pkg: "+repr(dir(pkg))

        if pkg != None :

            r = pkg.cid
            # print 'r: '+str(r)
            ret.insert(0,(pkg.pid, pkg.name))

            while r != 0:
                cat = sess.query(self.Category).filter_by(cid=r).first()
                ret.insert(0,(cat.cid, cat.name))
                r = cat.parent_cid

            # This is _presumed_. NOT inserted
            # ret.insert(0,(0, '/'))

        sess.close()

        # print '-gpp- :' + repr(ret)
        return ret

    def get_package_path_string(self, pid):
        r = self.get_package_path(pid)

        ret = join_pkg_path(r)

        return ret

    def find_repository_package_name_collisions_in_database(self):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        lst = sess.query(self.Package).all()

        lst2 = []

        for each in lst:
            lst2.append(self.get_package_path(pid=each.pid))

        print "-i- Processing %(n)s packages" % {'n': len(lst)}
        sys.stdout.flush()
        sess.close()

        del(lst)

        lst_dup = {}
        pkg_paths = {}

        for each in lst2:
            # print repr(each)

            l = each[-1][1].lower()

            if not l in pkg_paths:
                pkg_paths[l] = []

            pkg_paths[l].append(join_pkg_path(each))


        for each in pkg_paths.keys():
            if len(pkg_paths[each]) > 1:
                lst_dup[each] = pkg_paths[each]


        t = len(lst_dup)
        if len(lst_dup) == 0:
            t = 'i'
            t2 = '. Package locations look good!'
        else:
            t = 'w'
            t2 = ''

        print "-%(t)s- found %(c)s duplicated package names%(t2)s" % {
            'c' : len(lst_dup),
            't' : t,
            't2': t2
            }

        if len(lst_dup) > 0:
            print "       listing:"

            sorted_keys = lst_dup.keys()
            sorted_keys.sort()

            for each in sorted_keys:
                print "          %(key)s:" % {
                    'key': each
                    }

                lst_dup[each].sort()

                for each2 in lst_dup[each]:
                    print "             %(path)s" % {
                        'path': each2
                        }

        return 0

    def check_package_information(self, names=None):
        """
        names can be a list of names to check. if names is None -
        check all.
        """

        found = []

        not_found = []

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        names_found = []

        if names == None:
            q = sess.query(self.Package).all()
            for i in q:
                names_found.append(i.name)
        else:
            names_found = names

        for i in names_found:
            q = sess.query(self.PackageInfo).filter_by(name = i).first()

            if q == None:
                not_found.append(q)
            else:
                found.append(q)

        sess.close()

        return (found, not_found)

    def package_info_record_to_dict(self, name=None, record=None):
        """
        This method can accept package name or complited record
        instance.

        If name is given, record is not used and method does db query
        itself.

        If name is not given, record is used as if it wer this method
        query result.
        """

        ret = None

        if name != None:
            sess = sqlalchemy.orm.Session(bind=self._db_engine)

            q = sess.query(self.PackageInfo).filter_by(name = name).first()
        else:
            q = record

        if q == None:
            ret = None
        else:

            tags = self.get_package_tags(q.name)
            sources = self.get_package_sources(q.name)
            mirrors = self.get_package_mirrors(q.name)

            ret = {
                'homepage'     : q.home_page,
                'description'  : q.description,
                'pkg_name_type': q.pkg_name_type,
                'tags'         : tags,
                'sources'      : sources,
                'mirrors'      : mirrors,
                'buildinfo'    : q.buildinfo
                }

        if name != None:
            sess.close()

        return ret


    def package_info_dict_to_record(self, name, struct):

        # TODO: check_info_dict(struct)

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(Pself.ackageInfo).filter_by(name = name).first()

        creating_new = False
        if q == None:
            q = self.PackageInfo()
            creating_new = True

        q.name          = name
        q.description   = struct['description']
        q.home_page     = struct['homepage']
        q.pkg_name_type = struct['pkg_name_type']
        q.buildinfo     = struct['buildinfo']

        # category set only through pkg_repository
        # q.category    = category

        if creating_new:
            sess.add(q)


        sess.commit()
        sess.close()

        self.set_package_tags(name, struct['tags'])
        self.set_package_sources(name, struct['sources'])
        self.set_package_mirrors(name, struct['mirrors'])

    def backup_package_info_to_filesystem(
        self, mask='*', force_rewrite=False):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.PackageInfo).all()

        for i in q:
            if fnmatch.fnmatch(i.name, mask):
                filename = os.path.join(
                    self._config['info'], '%(name)s.xml' % {
                        'name': i.name
                        })
                if not force_rewrite and os.path.exists(filename):
                    print "-w- File exists - skipping: %(name)s" % {
                        'name': filename
                        }
                    continue
                if force_rewrite and os.path.exists(filename):
                    print "-i- File exists - rewriting: %(name)s" % {
                        'name': filename
                        }
                if not os.path.exists(filename):
                    print "-i- Writing: %(name)s" % {
                        'name': filename
                        }

                r = self.package_info_record_to_dict(record=i)
                if isinstance(r, dict):
                    if aipsetup.info.write_to_file(filename, r) != 0:
                        print "-e- can't write file %(name)s" % {
                            'name': filename
                            }

        sess.close()

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

        for i in files:
            name = aipsetup.utils.text.unicodify(
                os.path.basename(i)
                )

            name = name[:-4]

            missing = False
            if not all_records:
                sess = sqlalchemy.orm.Session(bind=self._db_engine)

                q = sess.query(self.PackageInfo).filter_by(name=name).first()

                if q == None:
                    missing = True

                sess.close()

                if not missing:
                    continue

            struct = aipsetup.info.read_from_file(i)
            if isinstance(struct, dict):
                print "-i- loading record: %(name)s" % {'name': name}
                self.package_info_dict_to_record(name, struct)
                loaded += 1
            else:
                print "-e- can't get info from file %(name)s" % {
                    'name': i
                    }


        print "-i- Total loaded %(n)d records" % {'n': loaded}
        return

    def delete_pkg_info_records(self, mask='*'):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.PackageInfo).all()

        deleted = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                sess.delete(i)
                deleted += 1
                print "-i- deleted pkg info: %(name)s" % {
                    'name': i.name
                    }
                sys.stdout.flush()

        sess.commit()
        sess.close()
        print "-i- Total deleted %(n)d records" % {
            'n': deleted
            }
        return

    def list_pkg_info_records(self, mask='*', mute=False):
        lst = []
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.PackageInfo).order_by(self.PackageInfo.name).all()

        found = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                found += 1
                lst.append(i.name)

        sess.close()
        if not mute:
            aipsetup.utils.text.columned_list_print(lst)
            print "-i- Total found %(n)d records" % {
                'n': found
                }
        return lst

    def find_missing_pkg_info_records(
        self, create_templates=False, force_rewrite=False):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.Package).order_by(self.Package.name).all()

        pkgs_checked = 0
        pkgs_missing = 0
        pkgs_written = 0
        pkgs_exists  = 0
        pkgs_failed  = 0
        pkgs_forced  = 0

        missing = []

        for each in q:

            pkgs_checked += 1

            q2 = sess.query(self.PackageInfo).filter_by(name = each.name).first()

            if q2 == None:

                pkgs_missing += 1
                missing.append(each.name)

                print "-w- missing package info record: %(name)s" % {
                    'name': each.name
                    }

                if create_templates:

                    filename = os.path.join(
                        self._config['info'],
                        '%(name)s.xml' % {'name': each.name}
                        )

                    if os.path.exists(filename):
                        if not force_rewrite:
                            print "-i- xml info file already exists"
                            pkgs_exists += 1
                            continue
                        else:
                            pkgs_forced += 1

                    if force_rewrite:
                        print "-i- forced template rewriting"

                    if aipsetup.info.write_to_file(
                        filename,
                        aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE) != 0:
                        pkgs_failed += 1
                        print "-e- failed writing template to %(name)s" % {
                            'name': filename
                            }
                    else:
                        pkgs_written += 1

        sess.close()

        print """\
-i- Total records checked     : %(n1)d
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
}

        missing.sort()
        return missing

    def find_outdated_pkg_info_records(self, mute=False):

        ret = []

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(self.PackageInfo).order_by(self.PackageInfo.name).all()

        for i in q:

            filename = os.path.join(
                self._config['info'],
                '%(name)s.xml' % {'name': i.name}
                )

            if not os.path.exists(filename):
                ret.append(i.name)
                if not mute:
                    print "-w- file missing: %(name)s" % {
                        'name': filename
                        }
                continue

            d1 = aipsetup.info.read_from_file(filename)

            if not isinstance(d1, dict):
                print "-i- Error parsing file: %(name)s" % {
                    'name': filename
                    }
            else:
                d2 = self.package_info_record_to_dict(record=i)
                if not aipsetup.info.is_dicts_equal(d1, d2):
                    ret.append(i.name)
                    if not mute:
                        print "-w- xml init file differs for: %(name)s" % {
                            'name': i.name
                            }

        sess.close()

        if not mute:
            print "-i- Total %(n)d warnings" % {'n': len(ret)}

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
        r = self.package_info_record_to_dict(name = name)
        if r == None:
            print "-e- Not found named info record"
        else:

            pid = self.get_package_id(name)
            if pid != None:
                category = self.get_package_path_string(pid)
            else:
                category = "< Package not indexed! >"

            regexp = '< Wrong regexp type name >'
            if r['pkg_name_type'] in aipsetup.name.NAME_REGEXPS:
                regexp = aipsetup.name.NAME_REGEXPS[r['pkg_name_type']]

            print """
Name: %(name)s

File Name Type: %(pkg_name_type)s

Regular Expression: %(regexp)s

Buildinfo: %(buildinfo)s

== Description ==

%(description)s

Home Page: %(homepage)s

== Sources ==

%(sources)s

== Mirrors ==

%(mirrors)s

----

Category: %(category)s

Tags: %(tags)s

""" % {
        'name'         : name,
        'homepage'     : r['homepage'],
        'pkg_name_type': r['pkg_name_type'],
        'regexp'       : regexp,
        'description'  : r['description'],
        'sources'      : '\n'.join(r['sources']),
        'mirrors'      : '\n'.join(r['mirrors']),
        'tags'         : ', '.join(r['tags']),
        'category'     : category,
        'buildinfo'    : r['buildinfo']
        }

