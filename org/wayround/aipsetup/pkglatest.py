
import logging

import sqlalchemy

import org.wayround.utils.db

import org.wayround.aipsetup.config

import org.wayround.aipsetup.pkginfo as pkginfo
import org.wayround.aipsetup.pkgindex as pkgindex



class PackageLatest(org.wayround.utils.db.BasicDB):
    """
    Main package index DB handling class
    """

    class Latest(Base):
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

        org.wayround.utils.db.BasicDB.__init__(
            self,
            org.wayround.aipsetup.config.config['package_latest_db_config'],
            echo=False
            )

        return


def set_latest_source(name, latest, force=False):
    return set_latest(name, latest, 'src', force)

def set_latest_package(name, latest, force=False):
    return set_latest(name, latest, 'pkg', force)

def set_latest(name, latest, typ, force=False):

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
        logging.error("Not found Info record for `{}'".format(name))
    else:

        logging.debug("Searching for existing `Latest' record of `{}'".format(name))
        q = self.sess.query(
            self.Newest
            ).filter_by(
                name=name, typ=typ2
            ).first()

        if q == None:
            logging.debug("existing `Latest' record of `{}' not found".format(name))
            if info['auto_newest_' + typ] or force:
                logging.debug("creating `Latest' record of `{}'".format(name))
                a = self.Newest()
                a.name = name
                a.file = latest
                a.typ = typ2
                self.sess.add(a)
                ret = True
            else:
                ret = False
        else:
            logging.debug("existing `Latest' record of `{}' found".format(name))
            if info['auto_newest_' + typ] or force:
                logging.debug("updating `Latest' record of `{}'".format(name))
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

def get_latest_source(name):
    return self.get_latest(name, 'src')

def get_latest_package(name):
    return self.get_latest(name, 'pkg')

def get_latest(name, typ):

    ret = None

    if not typ in ['src', 'pkg']:
        raise ValueError("`typ' can be only 'src' or 'pkg'")

    info = self.package_info_record_to_dict(name)

    if info == None:
        logging.error("Not found Info record for `{}'".format(name))
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

def get_list_of_non_automatic_package_info():

    q = self.sess.query(
        self.Info
        ).filter(
            self.Info.auto_newest_pkg == False
            or self.Info.auto_newest_src == False
            ).all()

    lst = []
    for i in q:
        lst.append(self.package_info_record_to_dict(i.name, i))

    return lst

def latest_source(name, info_db=None, files=None):

    ret = None

    if not files:
        files = get_package_source_files(name, info_db=info_db)

    if len(files) == 0:
        ret = None
    else:
        ret = max(
            files,
            key=functools.cmp_to_key(
                org.wayround.aipsetup.version.source_version_comparator
                )
            )

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
        db = PackageIndex()

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
        db = PackageIndex()

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
        db = PackageIndex()


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
        db = PackageIndex()

    if len(names) == 0:
        names = db.list_pkg_info_records(mute=True)

    for i in names:
        latest_pkg_to_package(i, force, mute, db_connected)

    if not db_connected:
        del db

    return

