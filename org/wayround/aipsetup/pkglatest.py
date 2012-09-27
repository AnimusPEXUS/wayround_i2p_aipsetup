
import logging
import functools

import sqlalchemy
import sqlalchemy.ext


import org.wayround.utils.db

import org.wayround.aipsetup.config

import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkgindex


def latest_editor(name):
    import org.wayround.aipsetup.latesteditor

    ret = org.wayround.aipsetup.latesteditor.main(name)

    return ret


class PackageLatest(org.wayround.utils.db.BasicDB):
    """
    Main package index DB handling class
    """

    Base = sqlalchemy.ext.declarative.declarative_base()

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



def set_found_latest_src_to_record(
    name, force=False, mute=True, info_db=None, latest_db=None
    ):

    if info_db == None:
        raise ValueError("info_db can't be None")

    if latest_db == None:
        raise ValueError("latest_db can't be None")

    ret = False

    r = get_latest_src_from_src_db(name)
    if r != None:
        print(
            "Package's latest src is: `{}'".format(r),
            )
        if r != None:

            ret = set_latest_src_to_record(
                name, r, force, info_db=info_db, latest_db=latest_db
                )

        else:
            ret = False

    if not ret:
        print("Can't set")


    return ret

def set_found_latest_src_to_records(
    names, force=False, mute=True, info_db=None, latest_db=None
    ):

    if info_db == None:
        raise ValueError("info_db can't be None")

    if latest_db == None:
        raise ValueError("latest_db can't be None")


    if len(names) == 0:
        names = org.wayround.aipsetup.pkginfo.get_info_records_list(
            mute=True, info_db=info_db
            )

    for i in names:
        set_found_latest_src_to_record(
            i,
            force,
            mute,
            info_db=info_db,
            latest_db=latest_db
            )

    return

def set_found_latest_pkg_to_record(
    name, force=False, mute=True, info_db=None, latest_db=None
    ):

    if info_db == None:
        raise ValueError("info_db can't be None")

    if latest_db == None:
        raise ValueError("latest_db can't be None")

    ret = False

    r = get_latest_pkg_from_repo(name)
    if r != None:
        print(
            "Package's latest pkg is: `{}'".format(r)
            )
        if r != None:

            ret = set_latest_pkg_to_record(
                name, r, force, info_db=info_db, latest_db=latest_db
                )

        else:
            ret = False

    if not ret:
        print("Can't set")


    return ret

def set_found_latest_pkg_to_records(
    names, force=False, mute=True, info_db=None, latest_db=None
    ):

    if info_db == None:
        raise ValueError("info_db can't be None")

    if latest_db == None:
        raise ValueError("latest_db can't be None")

    if len(names) == 0:
        names = org.wayround.aipsetup.pkginfo.get_info_records_list(
            mute=True, info_db=info_db
            )

    for i in names:
        set_found_latest_pkg_to_record(
            i, force, mute, info_db=info_db, latest_db=latest_db
            )

    return


def set_latest_src_to_record(name, latest, force=False, info_db=None, latest_db=None):
    return _set_latest_to_record(name, latest, 'src', force, info_db=info_db, latest_db=latest_db)

def set_latest_pkg_to_record(
    name, latest, force=False, info_db=None, latest_db=None
    ):

    return _set_latest_to_record(
        name, latest, 'pkg', force, info_db=info_db, latest_db=latest_db
        )

def _set_latest_to_record(
    name, latest, typ, force=False, info_db=None, latest_db=None
    ):

    if info_db == None:
        raise ValueError("info_db can't be None")

    if latest_db == None:
        raise ValueError("latest_db can't be None")

    logging.debug("setting latest `{}' to `{}'".format(typ, latest))
    ret = None

    if not typ in ['src', 'pkg']:
        raise ValueError("`typ' can be only 'src' or 'pkg'")

    typ2 = ''
    if typ == 'src':
        typ2 = 'source'
    elif typ == 'pkg':
        typ2 = 'package'

    info = org.wayround.aipsetup.pkginfo.get_package_info_record(
        name, info_db=info_db
        )

    if info == None:
        logging.error("Not found Info record for `{}'".format(name))
    else:

        logging.debug("Searching for existing `Latest' record of `{}'".format(name))
        q = latest_db.sess.query(
            latest_db.Latest
            ).filter_by(
                name=name, typ=typ2
            ).first()

        if q == None:
            logging.debug("existing `Latest' record of `{}' not found".format(name))
            if info['auto_newest_' + typ] or force:
                logging.debug("creating `Latest' record of `{}'".format(name))
                a = latest_db.Latest()
                a.name = name
                a.file = latest
                a.typ = typ2
                latest_db.sess.add(a)
                ret = True
            else:
                ret = False
        else:
            logging.debug("existing `Latest' record of `{}' found".format(name))
            if info['auto_newest_' + typ] or force:
                logging.debug("updating `Latest' record of `{}'".format(name))
                q.file = latest
                latest_db.sess.commit()
                ret = True
            else:
                ret = False

    if ret == False:
        logging.error(
            "Not `auto_newest_{}' and not forced".format(typ)
            )

    return ret

def get_latest_src_from_record(name, latest_db=None, info_db=None, index_db=None):
    return _get_latest_from_record(
        name, 'src', info_db=info_db, latest_db=latest_db, index_db=index_db
        )

def get_latest_pkg_from_record(name, latest_db=None, info_db=None, index_db=None):
    return _get_latest_from_record(
        name, 'pkg', info_db=info_db, latest_db=latest_db, index_db=index_db
        )

def _get_latest_from_record(name, typ, latest_db=None, info_db=None, index_db=None):

    if info_db == None:
        raise ValueError("info_db can't be None")

    if latest_db == None:
        raise ValueError("latest_db can't be None")

    if index_db == None:
        raise ValueError("index_db can't be None")

    ret = None

    if not typ in ['src', 'pkg']:
        raise ValueError("`typ' can be only 'src' or 'pkg'")

    info = org.wayround.aipsetup.pkginfo.get_package_info_record(
        name,
        info_db=info_db
        )

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
                latest = get_latest_src_from_src_db(name, info_db=info_db)
            elif typ == 'pkg':
                latest = get_latest_pkg_from_repo(name, index_db=index_db)
            ret = latest
        else:

            latest_r = latest_db.sess.query(
                latest_db.Latest
                ).filter_by(
                    name=name, typ=typ2
                    ).first()

            if latest_r == None:
                ret = None
            else:
                latest = latest_r.file
                ret = latest

    return ret


def get_latest_src_from_src_db(name, info_db=None, files=None):

    if info_db == None:
        raise ValueError("info_db can't be None")

    ret = None

    if not files:
        files = org.wayround.aipsetup.pkgindex.get_package_source_files(
            name, info_db=info_db
            )

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

def get_latest_pkg_from_repo(name, index_db=None, files=None):

    if index_db == None:
        raise ValueError("index_db can't be None")

    ret = None

    if not files:
        files = org.wayround.aipsetup.pkgindex.get_package_files(
            name, index_db=index_db
            )

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
