
"""
Package info related functions
"""

import builtins
import collections
import copy
import fnmatch
import json
import logging
import os.path
import re
import sys
import datetime

import sqlalchemy.ext.declarative

import wayround_org.aipsetup.repository
import wayround_org.utils.db
import wayround_org.utils.file
import wayround_org.utils.path
import wayround_org.utils.tarball
import wayround_org.utils.terminal
import wayround_org.utils.version


SAMPLE_PACKAGE_INFO_STRUCTURE = collections.OrderedDict([
    # description
    ('description', ""),

    # not required, but can be useful
    ('home_page', ""),

    # string
    ('buildscript', ''),

    # string
    ('version_tool', ''),

    # file name base
    ('basename', ''),

    # filters. various filters to provide correct list of acceptable tarballs
    # by they filenames
    ('filters', ''),

    # can package be deleted without hazard to aipsetup functionality
    # (including system stability)?
    ('removable', True),

    # can package be updated without hazard to aipsetup functionality
    # (including system stability)?
    ('reducible', True),

    # package can not be installed
    ('non_installable', False),

    # package outdated and need to be removed
    ('deprecated', False),

    # some shitty packages 
    # (like python2 and python3: see https://bugs.python.org/issue1294959)
    # can't be forced to be installed in lib64
    ('only_primary_install', False),

    # list of str
    ('tags', []),

    # to make search faster and exclude not related sources
    ('source_path_prefixes', []),

    # following packages required to build this package
    ('build_deps', []),

    # depends on .so files in following packages
    ('so_deps', []),

    # run time dependenties. (man pages reader requiers 'less' command i.e.)
    ('runtime_deps', [])

    ])
"""
Package info skeleton.
"""

SAMPLE_PACKAGE_INFO_STRUCTURE_TITLES = collections.OrderedDict([
    ('description', 'Description'),
    ('home_page', "Homepage"),
    ('buildscript', "Building Script"),
    ('basename', 'Tarball basename'),
    ('filters', "Filters"),
    ('removable', "Is Removable?"),
    ('reducible', "Is Reducible?"),
    ('non_installable', "Is Non Installable?"),
    ('deprecated', "Is Deprecated?")
    ])

# pkg_info_file_template = Template(text="""\
#<package>
#
#    <!-- This file is generated using aipsetup v3 -->
#
#    <description>${ description | x}</description>
#
#    <home_page url="${ home_page | x}"/>
#
#    <buildscript value="${ buildscript | x }"/>
#
#    <basename value="${ basename | x }"/>
#
#    <version_re value="${ version_re | x }"/>
#
#    <installation_priority value="${ installation_priority | x }"/>
#
#    <removable value="${ removable | x }"/>
#    <reducible value="${ reducible | x }"/>
#
#</package>
#""")


class PackageInfo(wayround_org.utils.db.BasicDB):

    """
    Main package index DB handling class
    """

    def init_table_mappings(self, init_table_data):

        class Info(self.decl_base):

            __tablename__ = 'info'

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

            filters = sqlalchemy.Column(
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

            version_tool = sqlalchemy.Column(
                sqlalchemy.UnicodeText,
                nullable=False,
                default=''
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

            non_installable = sqlalchemy.Column(
                sqlalchemy.Boolean,
                nullable=False,
                default=False
                )

            deprecated = sqlalchemy.Column(
                sqlalchemy.Boolean,
                nullable=False,
                default=False
                )

            only_primary_install = sqlalchemy.Column(
                sqlalchemy.Boolean,
                nullable=False,
                default=False
                )

            last_set_date = sqlalchemy.Column(
                sqlalchemy.DateTime,
                nullable=False
                )

        self.Info = Info

        return

    def get_mapped_info_table(self):
        ret = None
        if self.Info.__tablename__ in self.decl_base.metadata.tables:
            ret = self.decl_base.metadata.tables[self.Info.__tablename__]
        return ret

    def create_tables(self):
        self.get_mapped_info_table().create(checkfirst=True)
        return

    def get_names(self):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        q = session\
            .query(sqlalchemy.distinct(self.Info.name))\
            .order_by(self.Info.name)\
            .all()

        ret = list()

        for i in q:
            ret.append(i[0])

        session.close()

        return ret

    def get_by_name(self, name):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        ret = None

        q = session.query(self.Info).filter_by(name=name).\
            first()

        if q is None:

            ret = None

        else:

            ret = collections.OrderedDict()

            keys = SAMPLE_PACKAGE_INFO_STRUCTURE.keys()

            for i in keys:
                if i in [
                        'tags',
                        'source_path_prefixes',
                        'build_deps',
                        'so_deps',
                        'runtime_deps'
                        ]:
                    continue
                #ret[i] = eval("q['{}']".format(i))
                ret[i] = getattr(q, i)

            ret['name'] = q.name

        session.close()

        return ret

    def set_by_name(self, name, struct):

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        if not 'last_set_date' in struct:
            raise KeyError("`last_set_date' must be supplied")

        q = session.query(self.Info).filter_by(name=name).first()

        creating_new = False
        if q is None:
            q = self.Info()
            creating_new = True

        keys = set(SAMPLE_PACKAGE_INFO_STRUCTURE.keys())

        for i in keys:

            if i in [
                    'tags',
                    'source_path_prefixes',
                    'build_deps',
                    'so_deps',
                    'runtime_deps',
                    'last_set_date'
                    ]:
                continue

            kt = type(SAMPLE_PACKAGE_INFO_STRUCTURE[i])

            if not kt in [int, str, bool, datetime.datetime]:
                raise TypeError("Wrong type supplied: {}".format(kt))

            if kt == builtins.int:
                setattr(q, i, int(struct[i]))
                #a = getattr(q, i)
                #a = int(struct[i])

            elif kt == builtins.str:
                setattr(q, i, str(struct[i]))
                #a = getattr(q, i)
                #a = str(struct[i])

            elif kt == builtins.bool:
                setattr(q, i, bool(struct[i]))
                #a = getattr(q, i)
                #a = bool(struct[i])

            else:
                raise Exception("Programming Error")

        q.last_set_date = struct['last_set_date']

        q.name = name

        q.last_set_date = datetime.datetime.utcnow()

        if creating_new:
            session.add(q)

        session.commit()
        session.close()

        return

    def get_last_set_date(self, name):

        ret = None

        session = sqlalchemy.orm.Session(self.decl_base.metadata.bind)

        q = session.query(self.Info).filter_by(name=name).first()

        if q is not None:
            ret = q.last_set_date

        session.close()

        return ret


class PackageInfoCtl:

    def __init__(self, info_dir, info_db):

        if not isinstance(info_dir, str):
            raise TypeError("`info_dir' must be str")

        if not isinstance(info_db, PackageInfo):
            raise TypeError("`info_db' must be PackageInfo")
    
        #print("info_dir: {}".format(info_dir))
        #raise Exception('123')

        self._info_dir = wayround_org.utils.path.abspath(info_dir)

        self.info_db = info_db

        self.tag_db = Tags(
            bind=self.info_db.decl_base.metadata.bind,
            decl_base=self.info_db.decl_base,
            init_table_data='tags'
            )

        meta_bind = self.info_db.decl_base.metadata.bind
        decl_base = self.info_db.decl_base

        self.source_path_prefixes_db = SourcePathsRepo(
            bind=meta_bind,
            decl_base=decl_base,
            init_table_data='source_path_prefixes'
            )

        self.build_deps_db = BuildDepsRepo(
            bind=meta_bind,
            decl_base=decl_base,
            init_table_data='build_deps'
            )

        self.so_deps_db = SODepsRepo(
            bind=meta_bind,
            decl_base=decl_base,
            init_table_data='so_deps'
            )

        self.runtime_deps_db = RuntimeDepsRepo(
            bind=meta_bind,
            decl_base=decl_base,
            init_table_data='runtime_deps'
            )

        self.info_db.decl_base.metadata.create_all()

        return

    def get_info_dir(self):
        return self._info_dir

    def get_package_info_record(self, name):

        _debug = False

        info_db = self.info_db

        ret = info_db.get_by_name(name)

        ret['tags'] = self.tag_db.get_object_tags(name)

        ret['source_path_prefixes'] =\
            self.source_path_prefixes_db.get_object_tags(name)

        ret['build_deps'] = self.build_deps_db.get_object_tags(name)

        ret['so_deps'] = self.so_deps_db.get_object_tags(name)

        ret['runtime_deps'] = self.runtime_deps_db.get_object_tags(name)

        if _debug:
            print("requested: `{}' response:\n{}".format(name, ret))

        return ret

    def set_package_info_record(self, name, struct):

        info_db = self.info_db

        info_db.set_by_name(name, struct)

        self.tag_db.set_object_tags(
            name,
            wayround_org.utils.list.
            list_strip_remove_empty_remove_duplicated_lines(
                struct['tags']
                )
            )

        self.source_path_prefixes_db.set_object_tags(
            name,
            wayround_org.utils.list.
            list_strip_remove_empty_remove_duplicated_lines(
                struct['source_path_prefixes']
                )
            )

        self.build_deps_db.set_object_tags(
            name,
            wayround_org.utils.list.
            list_strip_remove_empty_remove_duplicated_lines(
                struct['build_deps']
                )
            )

        self.so_deps_db.set_object_tags(
            name,
            wayround_org.utils.list.
            list_strip_remove_empty_remove_duplicated_lines(
                struct['so_deps']
                )
            )

        self.runtime_deps_db.set_object_tags(
            name,
            wayround_org.utils.list.
            list_strip_remove_empty_remove_duplicated_lines(
                struct['runtime_deps']
                )
            )

        return

    def get_missing_info_records_list(
            self, pkg_index_ctl, create_templates=False, force_rewrite=False
            ):

        if not isinstance(
                pkg_index_ctl,
                wayround_org.aipsetup.repository.PackageRepoCtl
                ):
            raise ValueError(
                "pkg_index_ctl must be of type "
                "wayround_org.aipsetup.repository.PackageRepoCtl"
                )

        info_db = self.info_db

        index_db = pkg_index_ctl.get_db_connection()

        pkg_names = pkg_index_ctl.get_package_name_list()
        #pkg_names = index_db.get_package_names()

        pkgs_checked = 0
        pkgs_missing = 0
        pkgs_written = 0
        pkgs_exists = 0
        pkgs_failed = 0
        pkgs_forced = 0

        missing = []

        for each in pkg_names:

            pkgs_checked += 1

            q2 = info_db.get_by_name(each)

            if q2 is None:

                pkgs_missing += 1
                missing.append(each)

                logging.warning(
                    "missing package DB info record: {}".format(each)
                    )

                if create_templates:

                    filename = wayround_org.utils.path.join(
                        self._info_dir,
                        '{}.json'.format(each)
                        )

                    if os.path.exists(filename):
                        if not force_rewrite:
                            logging.info("JSON info file already exists")
                            pkgs_exists += 1
                            continue
                        else:
                            pkgs_forced += 1

                    if force_rewrite:
                        logging.info(
                            "Forced template rewriting: {}".format(filename)
                            )

                    if write_info_file(
                            filename,
                            SAMPLE_PACKAGE_INFO_STRUCTURE
                            ) != 0:
                        pkgs_failed += 1
                        logging.error(
                            "failed writing template to `{}'".format(filename)
                            )
                    else:
                        pkgs_written += 1

        logging.info(
            """\
    Total records checked     : {n1}
        Missing records           : {n2}
        Missing but present on FS : {n3}
        Written                   : {n4}
        Write failed              : {n5}
        Write forced              : {n6}
    """.format_map(
                {
                    'n1': pkgs_checked,
                    'n2': pkgs_missing,
                    'n3': pkgs_exists,
                    'n4': pkgs_written,
                    'n5': pkgs_failed,
                    'n6': pkgs_forced
                    }
                )
            )

        missing.sort()

        return missing

    def get_outdated_info_records_list(self, mute=True):

        info_db = self.info_db

        ret = []

        obj_lst = info_db.get_names()

        for i in obj_lst:

            filename = wayround_org.utils.path.join(
                self._info_dir,
                '{}.json'.format(i)
                )

            if not os.path.exists(filename):
                if not mute:
                    logging.warning("File missing: {}".format(filename))
                continue

            ctime = datetime.datetime.utcfromtimestamp(
                os.stat(filename).st_ctime
                )

            info_ctime = info_db.get_last_set_date(i)

            if info_ctime is None or ctime > info_ctime:
                logging.info(
                    "outdated (UTC): {} > {}".format(
                        ctime,
                        info_ctime
                        )
                )
                ret.append(i)

        return ret

    def get_package_name_by_tarball_filename(
            self,
            tarball_filename, mute=True
            ):

        ret = None

        parsed = wayround_org.utils.tarball.parse_tarball_name(
            tarball_filename,
            mute=mute
            )

        if not isinstance(parsed, dict):
            ret = None
        else:

            lst = [tarball_filename]

            info_db = self.info_db
            session = sqlalchemy.orm.Session(info_db.decl_base.metadata.bind)

            q = session.query(
                info_db.Info
                ).filter_by(
                    basename=parsed['groups']['name']
                    ).all()

            session.close()

            possible_names = []

            for i in q:

                res = wayround_org.utils.tarball.filter_tarball_list(
                    lst,
                    i.filters
                    )

                if isinstance(res, list) and len(res) == 1:
                    possible_names.append(i.name)

            ret = possible_names

        return ret

    def update_outdated_pkg_info_records(self):

        logging.info("Getting outdated records list")

        oir = self.get_outdated_info_records_list(mute=True)

        logging.info("Found {} outdated records".format(len(oir)))

        for i in range(len(oir)):
            oir[i] = wayround_org.utils.path.join(
                self._info_dir,
                oir[i] + '.json'
                )
        self.load_info_records_from_fs(
            filenames=oir,
            rewrite_existing=True
            )

        return

    def print_info_record(self, name, pkg_index_ctl, tag_ctl):

        # TODO: move this method to package_client
        # TODO: we have no tag_ctl longer, it's table control moved under
        #       info_ctl

        r = self.get_package_info_record(name=name)

        if r is None:
            logging.error("Not found named info record")
        else:

            cid = pkg_index_ctl.get_package_category_by_name(
                name
                )
            if cid is not None:
                category = pkg_index_ctl.get_category_path_string(
                    cid
                    )
            else:
                category = "< Package not indexed! >"

            tag_db = tag_ctl.tag_db

            tags = sorted(tag_db.get_tags(name[:-4]))

            print("""\
+---[{name}]----Overal Information-----------------+

                  basename: {basename}
               buildscript: {buildscript}
                  homepage: {home_page}
                  category: {category}
                      tags: {tags}
     installation priority: {installation_priority}
                 removable: {removable}
                 reducible: {reducible}
           non-installable: {non_installable}
                deprecated: {deprecated}

+---[{name}]----Tarball Filters--------------------+

{filters}

+---[{name}]----Description------------------------+

{description}

+---[{name}]----Info Block End---------------------+
""".format_map(
                {
                    'tags': ', '.join(tags),
                    'category': category,
                    'name': name,
                    'description': r['description'],
                    'home_page': r['home_page'],
                    'buildscript': r['buildscript'],
                    'basename': r['basename'],
                    'filters': r['filters'],
                    'installation_priority': r['installation_priority'],
                    'removable': r['removable'],
                    'reducible': r['reducible'],
                    'non_installable': r['non_installable'],
                    'deprecated': r['deprecated']
                }
                )
            )

        return

    def delete_info_records(self, mask='*'):

        info_db = self.info_db
        session = sqlalchemy.orm.Session(info_db.decl_base.metadata.bind)

        q = session.query(info_db.Info).all()

        deleted = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                session.delete(i)
                deleted += 1
                logging.info(
                    "deleted pkg info: {}".format(i.name)
                    )
                sys.stdout.flush()

        logging.info("Totally deleted {} records".format(deleted))

        session.commit() # TODO: found this line absent here. need to check others
        session.close()

        return

    def save_info_records_to_fs(
            self, mask='*', force_rewrite=False
            ):

        info_db = self.info_db

        obj_lst = info_db.get_names()

        for i in obj_lst:
            if fnmatch.fnmatch(i, mask):

                filename = wayround_org.utils.path.join(
                    self._info_dir,
                    '{}.json'.format(i))

                if not force_rewrite and os.path.exists(filename):
                    logging.warning(
                        "File exists - skipping: {}".format(filename)
                        )
                    continue

                if force_rewrite and os.path.exists(filename):
                    logging.info(
                        "File exists - rewriting: {}".format(filename)
                        )

                if not os.path.exists(filename):
                    logging.info("Writing: {}".format(filename))

                r = self.get_package_info_record(i)
                if isinstance(r, dict):
                    if write_info_file(filename, r) != 0:
                        logging.error("can't write file {}".format(filename))

        return 0

    def load_info_records_from_fs(
            self, filenames=[], rewrite_existing=False
            ):
        """
        If names list is given - load only named and don't delete existing
        """

        info_db = self.info_db
        session = sqlalchemy.orm.Session(info_db.decl_base.metadata.bind)

        files = []
        loaded = 0

        for i in filenames:
            if i.endswith('.json'):
                files.append(i)

        files.sort()

        missing = []
        logging.info("Searching missing records")
        files_l = len(files)
        num = 0
        for i in files:

            num += 1

            if num == 0:
                perc = 0
            else:
                perc = float(100) / (float(files_l) / float(num))
            wayround_org.utils.terminal.progress_write(
                '    {:6.2f}%'.format(perc)
                )

            name = os.path.basename(i)[:-5]

            if not rewrite_existing:
                q = session.query(info_db.Info).filter_by(
                    name=name
                    ).first()
                if q is None:
                    missing.append(i)
            else:
                missing.append(i)

        wayround_org.utils.terminal.progress_write_finish()

        wayround_org.utils.terminal.progress_write(
            "-i- Loading missing records"
            )

        for i in missing:
            struct = read_info_file(i)
            struct['last_set_date'] = datetime.datetime.utcnow()
            name = os.path.basename(i)[:-5]
            if isinstance(struct, dict):
                wayround_org.utils.terminal.progress_write(
                    "    loading record: {}\n".format(name)
                    )

                self.set_package_info_record(
                    name, struct
                    )
                loaded += 1
            else:
                logging.error("Can't get info from file {}".format(i))

        session.commit()

        logging.info("Totally loaded {} records".format(loaded))

        session.close()

        return

    def get_info_records_list(self, mask='*', mute=False):

        info_db = self.info_db
        session = sqlalchemy.orm.Session(info_db.decl_base.metadata.bind)

        ret = []

        q = session.query(info_db.Info).order_by(info_db.Info.name).all()

        found = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                found += 1
                ret.append(i.name)

        if not mute:
            wayround_org.utils.text.columned_list_print(ret)
            logging.info("Total found {} records".format(found))

        session.close()

        return ret


class Tags(wayround_org.utils.tag.TagEngine):
    pass


class SourcePathsRepo(wayround_org.utils.tag.TagEngine):
    pass


class BuildDepsRepo(wayround_org.utils.tag.TagEngine):
    pass


class SODepsRepo(wayround_org.utils.tag.TagEngine):
    pass


class RuntimeDepsRepo(wayround_org.utils.tag.TagEngine):
    pass


class SnapshotCtl:

    def __init__(self, dir_path):
        self._path = dir_path
        return

    def list(self):
        lst = []
        if os.path.isdir(self._path):
            lst = os.listdir(self._path)
        return lst

    def get(self, name, load_json=False):

        ret = None

        fn = wayround_org.utils.path.join(self._path, name)

        if os.path.isfile(fn):

            f = open(fn)
            txt = f.read()
            f.close()

            ret = txt
            if load_json:
                try:
                    ret = json.loads(ret)
                except:
                    logging.exception(
                        "Can't load json from file: {}".format(fn)
                        )
                    ret = None

        return ret

    def set(self, name, data):

        if not os.path.isdir(self._path):
            os.makedirs(self._path)

        fn = wayround_org.utils.path.join(self._path, name)

        f = open(fn, 'w')
        if isinstance(data, str):
            f.write(data)
        else:
            f.write(json.dumps(data, indent=2))
        f.close()
        return


def is_info_dicts_equal(d1, d2):
    """
    Compare two package info structures

    :rtype: ``bool``
    """

    ret = True

    for i in [
            'description',
            'home_page',
            'buildscript',
            'basename',
            'filters',
            'installation_priority',
            'removable',
            'reducible',
            'non_installable',
            'deprecated',
            ]:
        if d1[i] != d2[i]:
            ret = False
            break

    return ret


def read_info_file(name):
    """
    Read package info structure from named file. Return dict. On error return
    ``None``
    """

    ret = None

    txt = ''
    tree = None

    try:
        f = open(name, 'r')
    except:
        logging.error(
            "Can't open file `{}'".format(name)
            )
        ret = 1
    else:
        try:
            txt = f.read()

            try:
                tree = json.loads(txt)
            except:
                logging.exception("Can't parse file `{}'".format(name))
                ret = 2

            else:
                ret = copy.copy(SAMPLE_PACKAGE_INFO_STRUCTURE)

                ret.update(tree)

                ret['name'] = name
                # ret['last_set_date'] = 
                del(tree)
        finally:
            f.close()

    return ret


def write_info_file(name, struct):
    """
    Write package info structure into named file
    """

    ret = 0

    if 'name' in struct:
        del struct['name']

    struct_o = collections.OrderedDict()

    for i in SAMPLE_PACKAGE_INFO_STRUCTURE.keys():
        if i in [
                'last_set_date'
                ]:
            continue

        struct_o[i] = struct[i]

    struct = struct_o

    # do not add sort_keys=True here. struct must be OrderedDict
    txt = json.dumps(struct, indent=2)

    try:
        f = open(name, 'w')
    except:
        logging.exception("Can't rewrite file {}".format(name))
        ret = 1
    else:
        try:
            f.write(txt)
        finally:
            f.close()

    return ret
