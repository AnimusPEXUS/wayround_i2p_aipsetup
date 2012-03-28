#!/usr/bin/python2.6

import os
import os.path
import sys

import sqlalchemy
import sqlalchemy.orm



def is_package(path):
    return os.path.isdir(path) and os.path.isfile(os.path.join(path, '.package'))



def join_pkg_path(pkg_path):
    ret = ''
    lst = []

    for i in pkg_path:
        lst.append(i[1])

    ret = '/'.join(lst)

    return ret


class PackageRepository:

    def __init__(self, repo_dir='.', debug=['db_echo']):

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
            'Package', self._db_metadata,
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
            'Category', self._db_metadata,
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

        sqlalchemy.orm.mapper(Package, self._table_Package)
        sqlalchemy.orm.mapper(Category, self._table_Category)

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



    def _scan_tree(self, sess, root_dir, cid):


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

                self._scan_tree(sess, full_path, new_cat.cid)
            else:
                print "-w- garbage file found: %(path)s" % {'path': full_path}

        return 0



    def scan_tree(self):
        sess = sqlalchemy.orm.Session(bind=self._db_engine)
        print "-i- deleting old data"
        sess.query(Category).delete()
        sess.query(Package).delete()
        print "-i- commiting"
        sess.commit()
        print "-i- scanning..."
        self._scan_tree(sess, self._repo_dir, 0)
        print "-i- closing."
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



    def find_package_name_collisions(self):
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
