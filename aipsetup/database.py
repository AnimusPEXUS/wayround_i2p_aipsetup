#!/usr/bin/python2.6

import os
import os.path
import sys

import sqlalchemy
import sqlalchemy.orm

def router(opts, args, config):

    ret = 0

    if len(args) > 0:

        if args[0] == 'scan_repo_for_pkg_and_cat':
            # scan repository for packages and categories. result
            # replaces data in database
            r = PackageDatabase(
                repo_dir='/home/agu/_sda3/_UHT/pkg_publish',
                debug=[])
            r.scan_repo_for_pkg_and_cat()

        if args[0] == 'find_repository_package_name_collisions_in_database':
            # search database package table for collisions: no more
            # when one package with same name can exist!
            r = PackageDatabase(
                repo_dir='/home/agu/_sda3/_UHT/pkg_publish',
                debug=[])
            r.find_repository_package_name_collisions_in_database()

        if args[0] == 'compare_database_and_filesystem_package_info':
            # check every db.Package has db.PackageInfo .
            # check db.PackageInfo.* == fs.PackageInfo .
            pass

    else:
        print "wrong aipsetup command. try `aipsetup database help'"
        ret = 1


    return ret

def is_package(path):
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, '.package'))



def join_pkg_path(pkg_path):
    ret = ''
    lst = []

    for i in pkg_path:
        lst.append(i[1])

    ret = '/'.join(lst)

    return ret


class PackageDatabase:

    def __init__(self,
                 repo_dir='.',
                 db_engine_string='',
                 debug=['db_echo']):

        self._repo_dir = repo_dir

        db_file = os.path.join(repo_dir, 'index.sqlite')

        if not os.path.isdir(repo_dir):
            raise ValueError

        if os.path.exists(db_file) and not os.path.isfile(db_file):
            raise Exception

        db_echo = 'db_echo' in debug

        self._db_engine = sqlalchemy.create_engine('sqlite:///%(path)s' % {'path': db_file}, echo=db_echo)

        self._db_metadata = sqlalchemy.MetaData(bind=self._db_engine)

        self._table_Package = sqlalchemy.Table(
            'package', self._db_metadata,
            sqlalchemy.Column('pid',
                              sqlalchemy.Integer,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              default=u''),
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
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              default=u''),
            sqlalchemy.Column('parent_cid',
                              sqlalchemy.Integer,
                              nullable=False,
                              default=0)
            )


        self._table_VersionPrefix = sqlalchemy.Table(
            'version_prefix', self._db_metadata,
            sqlalchemy.Column('name',
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              primary_key=True
                              default=u''),
            sqlalchemy.Column('prefix',
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              default=u'')
            )

        self._table_PackageInfo = sqlalchemy.Table(
            'package_info', self._db_metadata,
            sqlalchemy.Column('name',
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              primary_key=True
                              default=u''),
            sqlalchemy.Column('home_page',
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              default=u''),
            sqlalchemy.Column('description',
                              sqlalchemy.UnicodeText,
                              nullable=False,
                              default=u''),
            # 'standard', 'local' or other package name
            sqlalchemy.Column('pkg_name_type',
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              default=u''),
            # if 'local' - then regexp is used
            sqlalchemy.Column('regexp',
                              sqlalchemy.Unicode(256),
                              nullable=False,
                              default=u'')
            )

        self._table_PackageSource = sqlalchemy.Table(
            'package_source', self._db_metadata,
            sqlalchemy.Column('id',
                              sqlalchemy.Integer,
                              nullable=False,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.Unicode(256),
                              nullable=False),
            sqlalchemy.Column('url',
                              sqlalchemy.UnicodeText,
                              nullable=False
                              default=u''),
            )

        self._table_PackageMirror = sqlalchemy.Table(
            'package_mirror', self._db_metadata,
            sqlalchemy.Column('id',
                              sqlalchemy.Integer,
                              nullable=False,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.Unicode(256),
                              nullable=False),
            sqlalchemy.Column('url',
                              sqlalchemy.UnicodeText,
                              nullable=False
                              default=u''),
            )

        self._table_PackageTag = sqlalchemy.Table(
            'package_tag', self._db_metadata,
            sqlalchemy.Column('id',
                              sqlalchemy.Integer,
                              nullable=False,
                              primary_key=True,
                              autoincrement=True),
            sqlalchemy.Column('name',
                              sqlalchemy.Unicode(256),
                              nullable=False),
            sqlalchemy.Column('tag',
                              sqlalchemy.Unicode(256),
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

                self._scan_repo_for_pkg_and_cat(sess, full_path, new_cat.cid)
            else:
                print "-w- garbage file found: %(path)s" % {'path': full_path}

        return 0

    def scan_repo_for_pkg_and_cat(self):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)
        print "-i- deleting old data"
        sess.query(Category).delete()
        sess.query(Package).delete()
        print "-i- commiting"
        sess.commit()
        print "-i- scanning..."
        self._scan_repo_for_pkg_and_cat(sess, self._repo_dir, 0)
        print "-i- closing."
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

        for i in tags:
            n = PackageTag(name, i)
            sess.add(n)

        sess.close()

    def set_package_sources(self, name, sources):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        for i in sources:
            n = PackageSource(name, i)
            sess.add(n)

        sess.close()

    def set_package_mirrors(self, name, mirrors):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        for i in mirrors:
            n = PackageMirror(name, i)
            sess.add(n)

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
        else:
            t='w'

        print "-%(t)s- found %(c)s duplicated package names" % {
            'c': len(lst_dup),
            't': t
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

    def package_info_record_to_dict(self, name):

        ret = None

        sess = sqlalchemy.orm.Session(bind=self._db_engine)

        q = sess.query(PackageInfo).filter_by(name = name).first()

        if q == None:
            ret = None
        else:

            category = ''
            tags = get_package_tags(name)
            sources = get_package_sources(name)
            mirrors = get_package_mirrors(name)

            ret = {
                'homepage'     : q.home_page,
                'description'  : q.description,
                'pkg_name_type': q.pkg_name_type,
                'regexp'       : q.regexp,
                'category'     : category,
                'tags'         : tags,
                'sources'      : sources,
                'mirrors'      : mirrors
                }

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
        q.description   = struct['description'],
        q.home_page     = struct['homepage'],
        q.pkg_name_type = struct['pkg_name_type'],
        q.regexp        = struct['regexp'],

        # category set only through pkg_repository
        # q.category     = category,

        if creating_new:
            sess.add(q)

        sess.close()

        self.set_package_tags(name, struct['tags'])
        self.set_package_sources(name, struct['sources'])
        self.set_package_mirrors(name, struct['mirrors'])


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
