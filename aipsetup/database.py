#!/usr/bin/python2.6

import os
import os.path
import sys
import fnmatch


import sqlalchemy
import sqlalchemy.orm

import pkginfo


def print_help():
    print """\
aipsetup database command

where command one of:

   scan_repo_for_pkg_and_cat

       scan repository and save it's categories and packages indexes
       to database

   find_repository_package_name_collisions_in_database

       scan index for equal package names

   find_missing_pkg_info_records [-t] [-f]

       search packages which have no corresponding info records

       if -t option is present - automatically creates non-existing
       corresponding .xml file templates in info dir

       -f forces rewrite existing .xml files. this option only action
        with -t option

   find_outdated_pkg_info_records

       finds pkg info records which differs to FS .xml files

   update_outdated_pkg_info_records

       loads pkg info records which differs to FS .xml files

   backup_package_info_to_filesystem [-f] [MASK]

       save package information from database to info directory.

       existing files are skipped, unless -f set

   load_package_info_from_filesystem [-a] [file names]

       load package information from named files

       by default only missing records are loaded

       if -a is set, all seleted record are loaded even if they
       already present in db.

   delete_pkg_info_records MASK

       if mask must be given or operation will fail

   list_pkg_info_records [MASK]

       default MASK is *

   print_pkg_info_record NAME

       print package info record information
"""

def router(opts, args, config):

    ret = 0

    if len(args) > 0:

        if args[0] == 'scan_repo_for_pkg_and_cat':
            # scan repository for packages and categories. result
            # replaces data in database
            r = PackageDatabase(config)
            r.scan_repo_for_pkg_and_cat()

        if args[0] == 'find_repository_package_name_collisions_in_database':
            # search database package table for collisions: no more
            # when one package with same name can exist!
            r = PackageDatabase(config)
            r.find_repository_package_name_collisions_in_database()

        if args[0] == 'find_missing_pkg_info_records':
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

        if args[0] == 'find_outdated_pkg_info_records':
            r = PackageDatabase(config)
            r.find_outdated_pkg_info_records()

        if args[0] == 'update_outdated_pkg_info_records':
            r = PackageDatabase(config)
            r.update_outdated_pkg_info_records()

        if args[0] == 'backup_package_info_to_filesystem':
            mask = '*'

            if len(args) > 1:
                mask = args[1]

            f = False
            for i in opts:
                if i[0] == '-f':
                    f = True
                    break

            r = PackageDatabase(config)
            r.backup_package_info_to_filesystem(mask, f)

        if args[0] == 'load_package_info_from_filesystem':
            a = False
            for i in opts:
                if i[0] == '-a':
                    a = True

            r = PackageDatabase(config)
            r.load_package_info_from_filesystem(args[1:], a)


        if args[0] == 'delete_pkg_info_records':

            mask = None

            if len(args) > 1:
                mask = args[1]

            if mask != None:

                r = PackageDatabase(config)
                r.delete_pkg_info_records(mask)
            else:
                print "-e- Mask is not given"

        if args[0] == 'list_pkg_info_records':

            mask = '*'

            if len(args) > 1:
                mask = args[1]


            r = PackageDatabase(config)
            r.list_pkg_info_records(mask)


        if args[0] == 'print_pkg_info_record':
            name = None

            if len(args) > 1:
                name = args[1]

            if name != None:

                r = PackageDatabase(config)
                r.print_pkg_info_record(name)
            else:
                print "-e- Name is not given"


        if args[0] == 'help':
            print_help()


    else:
        print "wrong aipsetup command. try `aipsetup database help'"
        ret = 1


    return ret


def is_package(path):
    return os.path.isdir(path) \
        and os.path.isfile(os.path.join(path, '.package'))



def join_pkg_path(pkg_path):
    ret = ''
    lst = []

    for i in pkg_path:
        lst.append(i[1])

    ret = '/'.join(lst)

    return ret


class PackageDatabase:

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

        self._db_metadata = \
            sqlalchemy.MetaData(bind=self._db_engine)

        self._table_Package = sqlalchemy.Table(
            'package', self._db_metadata,
            sqlalchemy.Column('pid',
                              sqlalchemy.Integer,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.String(256),
                              nullable=False,
                              default=''),
            sqlalchemy.Column('cid',
                              sqlalchemy.Integer,
                              nullable=False,
                              default=0)
            )



        self._table_Category = sqlalchemy.Table(
            'category', self._db_metadata,
            sqlalchemy.Column('cid',
                              sqlalchemy.Integer,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.String(256),
                              nullable=False,
                              default=''),
            sqlalchemy.Column('parent_cid',
                              sqlalchemy.Integer,
                              nullable=False,
                              default=0)
            )


        self._table_VersionPrefix = sqlalchemy.Table(
            'version_prefix', self._db_metadata,
            sqlalchemy.Column('name',
                              sqlalchemy.String(256),
                              nullable=False,
                              primary_key=True,
                              default=''),
            sqlalchemy.Column('prefix',
                              sqlalchemy.String(256),
                              nullable=False,
                              default='')
            )

        self._table_PackageInfo = sqlalchemy.Table(
            'package_info', self._db_metadata,
            sqlalchemy.Column('name',
                              sqlalchemy.String(256),
                              nullable=False,
                              primary_key=True,
                              default=''),
            sqlalchemy.Column('home_page',
                              sqlalchemy.String(256),
                              nullable=False,
                              default=''),
            sqlalchemy.Column('description',
                              sqlalchemy.Text,
                              nullable=False,
                              default=''),
            # 'standard', 'local' or other package name
            sqlalchemy.Column('pkg_name_type',
                              sqlalchemy.String(256),
                              nullable=False,
                              default=''),
            # if 'local' - then regexp is used
            sqlalchemy.Column('regexp',
                              sqlalchemy.String(256),
                              nullable=False,
                              default=''),
            sqlalchemy.Column('builder',
                              sqlalchemy.String(256),
                              nullable=False,
                              default='')
            )

        self._table_PackageSource = sqlalchemy.Table(
            'package_source', self._db_metadata,
            sqlalchemy.Column('id',
                              sqlalchemy.Integer,
                              nullable=False,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.String(256),
                              nullable=False),
            sqlalchemy.Column('url',
                              sqlalchemy.Text,
                              nullable=False,
                              default=''),
            )

        self._table_PackageMirror = sqlalchemy.Table(
            'package_mirror', self._db_metadata,
            sqlalchemy.Column('id',
                              sqlalchemy.Integer,
                              nullable=False,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.String(256),
                              nullable=False),
            sqlalchemy.Column('url',
                              sqlalchemy.Text,
                              nullable=False,
                              default=''),
            )

        self._table_PackageTag = sqlalchemy.Table(
            'package_tag', self._db_metadata,
            sqlalchemy.Column('id',
                              sqlalchemy.Integer,
                              nullable=False,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.String(256),
                              nullable=False),
            sqlalchemy.Column('tag',
                              sqlalchemy.String(256),
                              nullable=False),
            )


        sqlalchemy.orm.mapper(Package, self._table_Package)
        sqlalchemy.orm.mapper(Category, self._table_Category)
        sqlalchemy.orm.mapper(VersionPrefix, self._table_VersionPrefix)
        sqlalchemy.orm.mapper(PackageInfo, self._table_PackageInfo)
        sqlalchemy.orm.mapper(PackageSource, self._table_PackageSource)
        sqlalchemy.orm.mapper(PackageMirror, self._table_PackageMirror)
        sqlalchemy.orm.mapper(PackageTag, self._table_PackageTag)
        self._db_metadata.create_all()

    def create_category(self, name='name', parent_cid=0):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        new_cat = Category(name=name, parent_cid=parent_cid)

        sess.add(new_cat)
        sess.commit()


        new_cat_id = new_cat.cid

        sess.close()

        return new_cat_id

    def get_category_by_name(self, name='name'):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        lst = sess.query(Category).filter_by(name=name).all()

        sess.close()

        return lst

    def get_category_by_id(self, cid=0):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        lst = sess.query(Category).filter_by(cid=cid).all()

        sess.close()

        return lst

    def get_package_id(self, name):

        ret = None

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(Package).filter_by(name=name).first()
        if q != None:
            ret = q.pid

        sess.close()

        return ret


    def ls_packages(self, cid=None):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        if cid == None:
            lst = sess.query(Package).all()
        else:
            lst = sess.query(Package).filter_by(cid=cid).all()


        sess.close()

        return lst


    def ls_categories(self, parent_cid=0):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        lst = sess.query(Category).filter_by(parent_cid=parent_cid).all()

        sess.close()

        return lst

    def _scan_repo_for_pkg_and_cat(self, sess, root_dir, cid):


        files = os.listdir(root_dir)
        files.sort()

        isfiles = 0

        for each in files:
            full_path = os.path.join(root_dir, each)

            if not os.path.isdir(full_path):
                isfiles += 1

        if isfiles >= 3:
            print "-w- too many non-dirs : %(path)s" % {
                'path': root_dir}
            print "       skipping"
            sys.stdout.flush()
            return 1

        for each in files:
            full_path = os.path.join(root_dir, each)
            if is_package(full_path):
                sess.add(Package(name=each, cid=cid))
                sess.commit()
            elif os.path.isdir(full_path):
                new_cat = Category(name=each, parent_cid=cid)

                sess.add(new_cat)
                sess.commit()

                self._scan_repo_for_pkg_and_cat(
                    sess, full_path, new_cat.cid)
            else:
                print "-w- garbage file found: %(path)s" % {
                    'path': full_path}
                sys.stdout.flush()

        return 0

    def scan_repo_for_pkg_and_cat(self):
        sys.stdout.flush()
        sess = sqlalchemy.orm.Session(bind=self._db_engine)
        sys.stdout.flush()
        print "-i- deleting old data"
        sys.stdout.flush()
        sess.query(Category).delete()
        sess.query(Package).delete()
        sys.stdout.flush()
        print "-i- commiting"
        sys.stdout.flush()
        sess.commit()
        sys.stdout.flush()
        print "-i- scanning..."
        sys.stdout.flush()
        self._scan_repo_for_pkg_and_cat(
            sess, self._config['repository'], 0)
        sys.stdout.flush()
        print "-i- closing."
        sys.stdout.flush()
        sess.close()

    def get_package_tags(self, name):
        ret = []
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(PackageTag).filter_by(name = name).all()

        for i in q:
            ret.append(i.tag)

        sess.close()
        return ret

    def get_package_sources(self, name):
        ret = []
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(PackageSource).filter_by(name = name).all()

        for i in q:
            ret.append(i.url)

        sess.close()
        return ret

    def get_package_mirrors(self, name):
        ret = []
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(PackageMirror).filter_by(name = name).all()

        for i in q:
            ret.append(i.url)

        sess.close()
        return ret

    def set_package_tags(self, name, tags):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        sess.query(PackageTag).filter_by(name=name).delete()

        for i in tags:
            n = PackageTag(name, i)
            sess.add(n)

        sess.commit()
        sess.close()

    def set_package_sources(self, name, sources):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        sess.query(PackageSource).filter_by(name=name).delete()

        for i in sources:
            n = PackageSource(name, i)
            sess.add(n)

        sess.commit()
        sess.close()

    def set_package_mirrors(self, name, mirrors):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        sess.query(PackageMirror).filter_by(name=name).delete()

        for i in mirrors:
            n = PackageMirror(name, i)
            sess.add(n)

        sess.commit()
        sess.close()

    def get_package_path(self, pid):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        ret = []
        pkg = None

        if pid != None:
            pkg = sess.query(Package).filter_by(pid=pid).first()
        else:
            raise ValueError

        # print "pkg: "+repr(dir(pkg))

        if pkg != None :

            r = pkg.cid
            # print 'r: '+str(r)
            ret.insert(0,(pkg.pid, pkg.name))

            while r != 0:
                cat = sess.query(Category).filter_by(cid=r).first()
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

        lst = sess.query(Package).all()

        lst2 = []

        for each in lst:
            lst2.append(self.get_package_path(pid=each.pid))

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
            t='i'
            t2 = '. Package locations look good!'
        else:
            t='w'
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
                print

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
            q = sess.query(Package).all()
            for i in q:
                names_found.append(q.name)
        else:
            names_found = names

        for i in names_found:
            q = sess.query(PackageInfo).filter_by(name = i).first()

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

            q = sess.query(PackageInfo).filter_by(name = name).first()
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
                'regexp'       : q.regexp,
                'tags'         : tags,
                'sources'      : sources,
                'mirrors'      : mirrors,
                'builder'      : q.builder
                }

        if name != None:
            sess.close()

        return ret


    def package_info_dict_to_record(self, name, struct):

        # TODO: check_info_dict(struct)

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(PackageInfo).filter_by(name = name).first()

        creating_new = False
        if q == None:
            q = PackageInfo()
            creating_new = True

        q.name          = name
        q.description   = struct['description']
        q.home_page     = struct['homepage']
        q.pkg_name_type = struct['pkg_name_type']
        q.regexp        = struct['regexp']
        q.builder       = struct['builder']

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

        q = sess.query(PackageInfo).all()

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
                    if pkginfo.write_to_file(filename, r) != 0:
                        print "-e- can't write file %(name)s" % {
                            'name': filename
                            }

        sess.close()

    def load_package_info_from_filesystem(
        self, filenames=[], all_records=False):

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
            name = os.path.basename(i)
            name = name[:-4]

            missing = False
            if not all_records:
                sess = sqlalchemy.orm.Session(bind=self._db_engine)
                q = sess.query(PackageInfo).filter_by(name=name).first()
                if q == None:
                    missing = True
                sess.close()
                if not missing:
                    continue

            struct = pkginfo.read_from_file(i)
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

        q = sess.query(PackageInfo).all()

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

    def list_pkg_info_records(self, mask='*'):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(PackageInfo).order_by(PackageInfo.name).all()

        found = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                found += 1
                print i.name
                sys.stdout.flush()

        sess.close()
        print "-i- Total found %(n)d records" % {
            'n': found
            }
        return

    def find_missing_pkg_info_records(
        self, create_templates=False, force_rewrite=False):

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(Package).order_by(Package.name).all()

        pkgs_checked = 0
        pkgs_missing = 0
        pkgs_written = 0
        pkgs_exists  = 0
        pkgs_failed  = 0
        pkgs_forced  = 0

        missing = []

        for each in q:

            pkgs_checked += 1

            q2 = sess.query(PackageInfo).filter_by(name = each.name).first()

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

                    if pkginfo.write_to_file(
                        filename,
                        pkginfo.SAMPLE_PACKAGE_INFO_STRUCTURE) != 0:
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

        q = sess.query(PackageInfo).order_by(PackageInfo.name).all()

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

            d1 = pkginfo.read_from_file(filename)

            if not isinstance(d1, dict):
                print "-i- Error parsing file: %(name)s" % {
                    'name': filename
                    }
            else:
                d2 = self.package_info_record_to_dict(record=i)
                if not pkginfo.is_dicts_equal(d1, d2):
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

            print """
Name: %(name)s

File Name Type: %(pkg_name_type)s

Regular Expression: %(regexp)s

Builder: %(builder)s

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
                'name': name,
                'homepage': r['homepage'],
                'pkg_name_type': r['pkg_name_type'],
                'regexp': r['regexp'],
                'builder': r['builder'],
                'description': r['description'],
                'sources': '\n'.join(r['sources']),
                'mirrors': '\n'.join(r['mirrors']),
                'tags': ', '.join(r['tags']),
                'category': category
                }



class Package(object):

    def __init__(self, pid=None, name='', cid=None):
        if pid != None:
            self.pid = pid

        self.name = name
        self.cid = cid



class Category(object):

    def __init__(self, cid=None, name='', parent_cid=0):
        if cid != None:
            self.cid = cid

        self.name = name
        self.parent_cid = parent_cid



class VersionPrefix(object):

    def __init__(self, name='', prefix=''):

        self.name = name
        self.prefix = prefix



class PackageInfo(object):

    # def __init__(self, name, home_page, description,
    #              pkg_name_type, regexp):

    #     self.name=name
    #     self.home_page=home_page
    #     self.description=description
    #     self.pkg_name_type=pkg_name_type
    #     self.regexp=regexp

    def __init__(self):
        pass


class PackageSource(object):

    def __init__(self, name, url):

        self.name = name
        self.url = url



class PackageMirror(object):

    def __init__(self, name, url):

        self.name = name
        self.url = url



class PackageTag(object):

    def __init__(self, name, tag):

        self.name = name
        self.tag = tag
