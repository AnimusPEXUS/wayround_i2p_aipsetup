
import os.path
import logging
import fnmatch
import sys
import re

import sqlalchemy

import org.wayround.utils.file
import org.wayround.utils.db

import org.wayround.aipsetup.config
import org.wayround.aipsetup.info

import org.wayround.aipsetup.pkgindex as pkgindex
import org.wayround.aipsetup.pkglatest as pkglatest

class PackageInfo(org.wayround.utils.db.BasicDB):
    """
    Main package index DB handling class
    """

    class Info(Base):
        """
        Class for holding package information
        """
        __tablename__ = 'package_info'

        name = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            primary_key=True,
            default=''
            )

        basename = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        version_re = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        home_page = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        description = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        buildscript = sqlalchemy.Column(
            sqlalchemy.UnicodeText,
            nullable=False,
            default=''
            )

        installation_priority = sqlalchemy.Column(
            sqlalchemy.Integer,
            nullable=False,
            default=5
            )

        removable = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        reducible = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        auto_newest_src = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

        auto_newest_pkg = sqlalchemy.Column(
            sqlalchemy.Boolean,
            nullable=False,
            default=True
            )

    def __init__(self):

        org.wayround.utils.db.BasicDB.__init__(
            self,
            org.wayround.aipsetup.config.config['package_info_db_config'],
            echo=False
            )

        return



def check_package_information(names, info_db, index_db):
    """
    names can be a list of names to check. if names is None -
    check all.
    """

    found = []

    not_found = []

    names_found = []

    if names == None:
        q = index_db.sess.query(index_db.Package).all()
        for i in q:
            names_found.append(i.name)
    else:
        names_found = names

    for i in names_found:
        q = info_db.sess.query(info_db.PackageInfo).filter_by(name=i).first()

        if q == None:
            not_found.append(q)
        else:
            found.append(q)

    return (found, not_found)


def package_info_record_to_dict(name=None, record=None, info_db=None):
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
        q = info_db.sess.query(info_db.PackageInfo).filter_by(name=name).first()
    else:
        q = record

    if q == None:
        ret = None
    else:

        ret = dict()

        keys = set(org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys())
        keys.remove('tags')

        for i in keys:
            ret[i] = eval('q.{}'.format(i))

        ret['name'] = q.name


    return ret


def package_info_dict_to_record(name, struct, info_db):

    # TODO: check_info_dict(struct)

    q = info_db.sess.query(info_db.PackageInfo).filter_by(name=name).first()

    creating_new = False
    if q == None:
        q = info_db.PackageInfo()
        creating_new = True

#        keys = set(org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys())
#
#        for i in ['tags', 'name']:
#            if i in keys:
#                keys.remove(i)

    q.name = name
    q.description = str(struct["description"])
    q.home_page = str(struct["home_page"])
    q.buildscript = str(struct["buildscript"])
    q.basename = str(struct["basename"])
    q.version_re = str(struct["version_re"])
    q.installation_priority = int(struct["installation_priority"])
    q.removable = bool(struct["removable"])
    q.reducible = bool(struct["reducible"])
    q.auto_newest_src = bool(struct["auto_newest_src"])
    q.auto_newest_pkg = bool(struct["auto_newest_pkg"])

#        for i in keys:
#            exec('q.{key} = struct["{key}"]'.format(key=i))


    if creating_new:
        info_db.sess.add(q)

    return

def backup_package_info_to_filesystem(
    mask='*', force_rewrite=False, info_db=None
    ):

    q = info_db.sess.query(info_db.PackageInfo).all()

    for i in q:
        if fnmatch.fnmatch(i.name, mask):
            filename = os.path.join(
                org.wayround.aipsetup.config.config['info'], '%(name)s.xml' % {
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

            r = package_info_record_to_dict(record=i, info_db=info_db)
            if isinstance(r, dict):
                if org.wayround.aipsetup.info.write_to_file(filename, r) != 0:
                    logging.error("can't write file %(name)s" % {
                        'name': filename
                        })

    return

def load_package_info_from_filesystem(
    filenames=[], rewrite_existing=False, info_db=None
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
    logging.info("Searching missing records")
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

        if not rewrite_existing:
            q = info_db.sess.query(info_db.PackageInfo).filter_by(
                name=name
                ).first()
            if q == None:
                missing.append(i)
        else:
            missing.append(i)

    org.wayround.utils.file.progress_write_finish()

    org.wayround.utils.file.progress_write("-i- Loading missing records")

    for i in missing:
        struct = org.wayround.aipsetup.info.read_from_file(i)
        name = os.path.basename(i)[:-4]
        if isinstance(struct, dict):
            org.wayround.utils.file.progress_write(
                "    loading record: %(name)s" % {
                    'name': name
                    }
                )

            package_info_dict_to_record(
                name, struct, info_db
                )
            loaded += 1
        else:
            logging.error("can't get info from file %(name)s" % {
                'name': i
                })
    info_db.commit()
    org.wayround.utils.file.progress_write_finish()

    logging.info("Totally loaded %(n)d records" % {'n': loaded})
    return

def delete_pkg_info_records(mask='*', info_db=None):

    q = info_db.sess.query(info_db.PackageInfo).all()

    deleted = 0

    for i in q:

        if fnmatch.fnmatch(i.name, mask):
            info_db.sess.delete(i)
            deleted += 1
            logging.info("deleted pkg info: %(name)s" % {
                'name': i.name
                })
            sys.stdout.flush()

    logging.info("Totally deleted %(n)d records" % {
        'n': deleted
        })
    return

def list_pkg_info_records(mask='*', mute=False, info_db=None):
    lst = []

    q = info_db.sess.query(info_db.PackageInfo).order_by(info_db.PackageInfo.name).all()

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
    create_templates=False, force_rewrite=False, index_db=None, info_db=None
    ):

    q = index_db.sess.query(index_db.Package).order_by(index_db.Package.name).all()

    pkgs_checked = 0
    pkgs_missing = 0
    pkgs_written = 0
    pkgs_exists = 0
    pkgs_failed = 0
    pkgs_forced = 0

    missing = []

    for each in q:

        pkgs_checked += 1

        q2 = info_db.sess.query(info_db.PackageInfo).filter_by(name=each.name).first()

        if q2 == None:

            pkgs_missing += 1
            missing.append(each.name)

            logging.warning("missing package DB info record: %(name)s" % {
                'name': each.name
                })

            if create_templates:

                filename = os.path.join(
                    org.wayround.aipsetup.config.config['info'],
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

def find_outdated_pkg_info_records(mute=True, info_db=None):

    ret = []

    query_result = (
        info_db.sess.query(info_db.PackageInfo).order_by(info_db.PackageInfo.name).all()
        )

    for i in query_result:

        filename = os.path.join(
            org.wayround.aipsetup.config.config['info'],
            '{}.xml'.format(i.name)
            )

        if not os.path.exists(filename):
            if not mute:
                logging.warning("File missing: {}".format(filename))
            ret.append(i.name)
            continue

        d1 = org.wayround.aipsetup.info.read_from_file(filename)

        if not isinstance(d1, dict):
            if not mute:
                logging.error("Error parsing file: {}".format(filename))
            ret.append(i.name)
            continue

        d2 = package_info_record_to_dict(record=i, info_db=info_db)
        if not org.wayround.aipsetup.info.is_info_dicts_equal(d1, d2):
            if not mute:
                logging.warning("xml init file differs to `%(name)s' record" % {
                    'name': i.name
                    })
            ret.append(i.name)

    return ret

def update_outdated_pkg_info_records(info_db=None):

    opir = find_outdated_pkg_info_records(mute=True, info_db=info_db)

    opir2 = []

    for i in opir:
        opir2.append(
            os.path.join(
                org.wayround.aipsetup.config.config['info'],
                '%(name)s.xml' % {'name': i}
                )
            )

    load_package_info_from_filesystem(
        filenames=opir2,
        rewrite_existing=True,
        info_db=info_db
        )

    return


def print_pkg_info_record(name, info_db=None, index_db=None):

    r = package_info_record_to_dict(name=name, info_db=info_db)

    if r == None:
        logging.error("Not found named info record")
    else:

        cid = pkgindex.get_package_category_by_name(name, index_db=index_db)
        if cid != None:
            category = pkgindex.get_category_path_string(cid, index_db=index_db)
        else:
            category = "< Package not indexed! >"

        # TODO: add all fields
        print("""\
+---[{name}]---------------------------------------+
          basename: {basename}
    version regexp: {version_re}
         buildscript: {buildscript}
          homepage: {home_page}
          category: {category}
              tags: {tags}
installation priority: {installation_priority}
         removable: {removable}
         reducible: {reducible}
   auto newest src: {auto_newest_src}
   auto newest pkg: {auto_newest_pkg}
        newest src: {newest_src}
        newest pkg: {newest_pkg}
+---[{name}]---------------------------------------+
{description}
+---[{name}]---------------------------------------+
""".format_map(
    {
    'tags'                  : ', '.join(r['tags']),
    'category'              : category,
    'name'                  : name,
    'description'           : r['description'],
    'home_page'             : r['home_page'],
    'buildscript'           : r['buildscript'],
    'basename'              : r['basename'],
    'version_re'            : r['version_re'],
    'installation_priority' : r['installation_priority'],
    'removable'             : r['removable'],
    'reducible'             : r['reducible'],
    'auto_newest_src'       : r['auto_newest_src'],
    'auto_newest_pkg'       : r['auto_newest_pkg'],
    'newest_src'            : pkglatest.get_latest_source(name),
    'newest_pkg'            : pkglatest.get_latest_package(name),
    }
    )
)

def find_package_info_by_basename_and_version(basename, version, info_db):

    ret = {}

    q = info_db.sess.query(info_db.PackageInfo).filter_by(basename=basename).all()

    for i in q:
        if re.match(i.version_re, version):
            ret[i.name] = package_info_record_to_dict(i.name, i, info_db=info_db)
            break

    return ret

def get_list_of_non_automatic_package_info(info_db):

    q = info_db.sess.query(
        info_db.PackageInfo
        ).filter(
            info_db.PackageInfo.auto_newest_pkg == False
            or info_db.PackageInfo.auto_newest_src == False
            ).all()

    lst = []
    for i in q:
        lst.append(package_info_record_to_dict(i.name, i, info_db=info_db))

    return lst

def guess_package_homepage(pkg_name, src_db=None):

    files = src_db.objects_by_tags([pkg_name])

    ret = {}
    for i in files:
        domain = i[1:].split('/')[0]

        if not domain in ret:
            ret[domain] = 0

        ret[domain] += 1
    logging.debug('Possibilities for {} are: {}'.format(pkg_name, repr(ret)))

    return ret