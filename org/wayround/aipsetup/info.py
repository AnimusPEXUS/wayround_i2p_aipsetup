
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

import sqlalchemy.ext.declarative

import org.wayround.aipsetup.repository
import org.wayround.utils.db
import org.wayround.utils.file
import org.wayround.utils.path
import org.wayround.utils.tarball_name_parser
import org.wayround.utils.terminal
import org.wayround.utils.version


SAMPLE_PACKAGE_INFO_STRUCTURE = collections.OrderedDict([
    # description
    ('description', ""),

    # not required, but can be useful
    ('home_page', ""),

    # string
    ('buildscript', ''),

    # file name base
    ('basename', ''),

    # filters. various filters to provide correct list of acceptable tarballs
    # by they filenames
    ('filters', ''),

    # from 0 to 9. default 5. lower number - higher priority
    ('installation_priority', 5),

    # can package be deleted without hazard to aipsetup functionality
    # (including system stability)?
    ('removable', True),

    # can package be updated without hazard to aipsetup functionality
    # (including system stability)?
    ('reducible', True),

    # package can not be installed
    ('non_installable', False),

    # package outdated and need to be removed
    ('deprecated', False)

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
    ('installation_priority', "Installation Priority"),
    ('removable', "Is Removable?"),
    ('reducible', "Is Reducible?"),
    ('non_installable', "Is Non Installable?"),
    ('deprecated', "Is Deprecated?")
    ])

#pkg_info_file_template = Template(text="""\
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


class PackageInfo(org.wayround.utils.db.BasicDB):
    """
    Main package index DB handling class
    """

    Base = sqlalchemy.ext.declarative.declarative_base()

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

    def __init__(self, config):

        org.wayround.utils.db.BasicDB.__init__(
            self,
            config,
            echo=False,
            create_all=True
            )

        return


class PackageInfoCtl:

    def __init__(self, info_dir, info_db):

        if not isinstance(info_dir, str):
            raise TypeError("`info_dir' must be str")

        if not isinstance(info_db, PackageInfo):
            raise TypeError("`info_db' must be PackageInfo")

        self._info_dir = org.wayround.utils.path.abspath(info_dir)
        self._info_db = info_db

        return

    def get_info_dir(self):
        return self._info_dir

    def get_lists_of_packages_missing_and_present_info_records(
        self,
        names, pkg_index_ctl
        ):

        """
        :param names: can be a string or a ``list`` of names to check. if names
        is ``None`` - check all.
        """

        index_db = pkg_index_ctl.get_db_connection()
        info_db = self._info_db

        found = []

        not_found = []

        names_found = []

        if names == None:
            q = index_db.session.query(index_db.Package).all()
            for i in q:
                names_found.append(i.name)
        else:
            names_found = names

        for i in names_found:
            q = info_db.session.query(info_db.Info).filter_by(name=i).first()

            if q == None:
                not_found.append(q)
            else:
                found.append(q)

        return (found, not_found)

    def get_package_info_record(self, name=None, record=None):
        """
        This method can accept package name or complete record instance.

        If name is given, record is not used and method does db query itself.

        If name is not given, record is used as if it were this method's query
        result.
        """

        info_db = self._info_db

        ret = None

        if name != None:
            q = info_db.session.query(info_db.Info).filter_by(name=name).\
                first()
        else:
            q = record

        if q == None:

            ret = None

        else:

            ret = collections.OrderedDict()

            keys = SAMPLE_PACKAGE_INFO_STRUCTURE.keys()

            for i in keys:
                ret[i] = eval('q.{}'.format(i))

            ret['name'] = q.name

        return ret

    def set_package_info_record(self, name, struct):

        info_db = self._info_db

        q = info_db.session.query(info_db.Info).filter_by(name=name).first()

        creating_new = False
        if q == None:
            q = info_db.Info()
            creating_new = True

        keys = set(SAMPLE_PACKAGE_INFO_STRUCTURE.keys())

        for i in keys:
            kt = type(SAMPLE_PACKAGE_INFO_STRUCTURE[i])

            if not kt in [builtins.int, builtins.str, builtins.bool]:
                raise TypeError("Wrong type supplied: {}".format(kt))

            ktt = 'str'
            if kt == builtins.int:
                ktt = 'int'
            elif kt == builtins.str:
                ktt = 'str'
            elif kt == builtins.bool:
                ktt = 'bool'
            else:
                raise Exception("Programming Error")

            exec(
                "q.{name} = {type}(struct['{name}'])".format(type=ktt, name=i)
                )

        q.name = name

        if creating_new:
            info_db.session.add(q)

        return

    def get_info_records_list(self, mask='*', mute=False):

        info_db = self._info_db

        ret = []

        q = info_db.session.query(info_db.Info).order_by(info_db.Info.name).\
            all()

        found = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                found += 1
                ret.append(i.name)

        if not mute:
            org.wayround.utils.text.columned_list_print(ret)
            logging.info("Total found {} records".format(found))

        return ret

    def get_missing_info_records_list(
        self, pkg_index_ctl, create_templates=False, force_rewrite=False
        ):

        if not isinstance(
            pkg_index_ctl,
            org.wayround.aipsetup.repository.PackageRepoCtl
            ):
            raise ValueError(
                "pkg_index_ctl must be of type "
                "org.wayround.aipsetup.repository.PackageRepoCtl"
                )

        info_db = self._info_db
        index_db = pkg_index_ctl.get_db_connection()

        q = index_db.session.query(
            index_db.Package
            ).order_by(index_db.Package.name).all()

        pkgs_checked = 0
        pkgs_missing = 0
        pkgs_written = 0
        pkgs_exists = 0
        pkgs_failed = 0
        pkgs_forced = 0

        missing = []

        for each in q:

            pkgs_checked += 1

            q2 = info_db.session.query(
                info_db.Info
                ).filter_by(name=each.name).first()

            if q2 == None:

                pkgs_missing += 1
                missing.append(each.name)

                logging.warning(
                    "missing package DB info record: {}".format(each.name)
                    )

                if create_templates:

                    filename = os.path.join(
                        self._info_dir,
                        '{}.json'.format(each.name)
                        )

                    if os.path.exists(filename):
                        if not force_rewrite:
                            logging.info("XML info file already exists")
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

        info_db = self._info_db

        ret = []

        query_result = (
            info_db.session.query(info_db.Info).order_by(info_db.Info.name).\
                all()
            )

        for i in query_result:

            filename = os.path.join(
                self._info_dir,
                '{}.json'.format(i.name)
                )

            if not os.path.exists(filename):
                if not mute:
                    logging.warning("File missing: {}".format(filename))
                ret.append(i.name)
                continue

            d1 = read_info_file(filename)

            if not isinstance(d1, dict):
                if not mute:
                    logging.error("Error parsing file: {}".format(filename))
                ret.append(i.name)
                continue

            d2 = self.get_package_info_record(record=i)
            if not is_info_dicts_equal(d1, d2):
                if not mute:
                    logging.warning(
                        "xml init file differs to `{}' record".format(i.name)
                        )
                ret.append(i.name)

        return ret

    def get_info_rec_by_tarball_filename(self, tarball_filename):
        ret = None

        r = self.get_package_name_by_tarball_filename(tarball_filename)

        if r:
            ret = self.get_package_info_record(r)
        else:
            ret = None

        return ret

    def get_package_name_by_tarball_filename(
        self,
        tarball_filename, mute=True
        ):

        ret = None

        parsed = org.wayround.utils.tarball_name_parser.parse_tarball_name(
            tarball_filename,
            mute=mute
            )

        if not isinstance(parsed, dict):
            ret = None
        else:

            lst = [tarball_filename]

            info_db = self._info_db

            q = info_db.session.query(
                info_db.Info
                ).filter_by(
                    basename=parsed['groups']['name']
                    ).all()

            possible_names = []

            for i in q:

                res = filter_tarball_list(
                    lst,
                    i.filters
                    )

                if isinstance(res, list) and len(res) == 1:
                    possible_names.append(i.name)

            if len(possible_names) < 1:
                if not mute:
                    logging.error(
                        "Not found package name "
                        "for tarball `{}'".format(tarball_filename)
                        )

                ret = None

            elif len(possible_names) > 1:
                if not mute:
                    logging.error(
                        "Too many possible package names "
                        "for tarball `{}':".format(tarball_filename)
                        )

                for i in q:
                    print("       {}".format(possible_names))

                ret = None

            else:
                ret = possible_names[0]

        return ret

    def get_non_automatic_packages_info_list(self):

        info_db = self._info_db

        # FIXME: error
        lst = []
        for i in q:
            lst.append(self.get_package_info_record(i.name, i))

        return lst

    def guess_package_homepage(self, pkg_name):

        src_db = self._info_db

        files = src_db.objects_by_tags([pkg_name])

        ret = {}
        for i in files:
            domain = i[1:].split('/')[0]

            if not domain in ret:
                ret[domain] = 0

            ret[domain] += 1
        logging.debug(
            'Possibilities for {} are: {}'.format(pkg_name, repr(ret))
            )

        return ret

    def update_outdated_pkg_info_records(self):

        logging.info("Getting outdated records list")

        oir = self.get_outdated_info_records_list(mute=True)

        logging.info("Found {} outdated records".format(len(oir)))

        for i in range(len(oir)):
            oir[i] = os.path.join(
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

        r = self.get_package_info_record(name=name)

        if r == None:
            logging.error("Not found named info record")
        else:

            cid = pkg_index_ctl.get_package_category_by_name(
                name
                )
            if cid != None:
                category = pkg_index_ctl.get_category_path_string(
                    cid
                    )
            else:
                category = "< Package not indexed! >"

            tag_db = tag_ctl.tag_db

            tags = tag_db.get_tags(name[:-4])
            tags.sort()

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
                'tags'                  : ', '.join(tags),
                'category'              : category,
                'name'                  : name,
                'description'           : r['description'],
                'home_page'             : r['home_page'],
                'buildscript'           : r['buildscript'],
                'basename'              : r['basename'],
                'filters'               : r['filters'],
                'installation_priority' : r['installation_priority'],
                'removable'             : r['removable'],
                'reducible'             : r['reducible'],
                'non_installable'       : r['non_installable'],
                'deprecated'            : r['deprecated']
                }
                )
            )

    def delete_info_records(self, mask='*'):

        info_db = self._info_db

        q = info_db.session.query(info_db.Info).all()

        deleted = 0

        for i in q:

            if fnmatch.fnmatch(i.name, mask):
                info_db.session.delete(i)
                deleted += 1
                logging.info(
                    "deleted pkg info: {}".format(i.name)
                    )
                sys.stdout.flush()

        logging.info("Totally deleted {} records".format(deleted))

        return

    def save_info_records_to_fs(
        self, mask='*', force_rewrite=False
        ):

        info_db = self._info_db

        q = info_db.session.query(info_db.Info).order_by(info_db.Info.name).\
            all()

        for i in q:
            if fnmatch.fnmatch(i.name, mask):
                filename = os.path.join(
                    self._info_dir,
                    '{}.json'.format(i.name))
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

                r = self.get_package_info_record(record=i)
                if isinstance(r, dict):
                    if write_info_file(filename, r) != 0:
                        logging.error("can't write file {}".format(filename))

        return 0

    def load_info_records_from_fs(
        self, filenames=[], rewrite_existing=False
        ):
        """
        If names list is given - load only named and don't delete
        existing
        """

        info_db = self._info_db

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
            org.wayround.utils.terminal.progress_write(
                '    {:6.2f}%'.format(perc)
                )

            name = os.path.basename(i)[:-5]

            if not rewrite_existing:
                q = info_db.session.query(info_db.Info).filter_by(
                    name=name
                    ).first()
                if q == None:
                    missing.append(i)
            else:
                missing.append(i)

        org.wayround.utils.terminal.progress_write_finish()

        org.wayround.utils.terminal.progress_write(
            "-i- Loading missing records"
            )

        for i in missing:
            struct = read_info_file(i)
            name = os.path.basename(i)[:-5]
            if isinstance(struct, dict):
                org.wayround.utils.terminal.progress_write(
                    "    loading record: {}\n".format(name)
                    )

                self.set_package_info_record(
                    name, struct
                    )
                loaded += 1
            else:
                logging.error("Can't get info from file {}".format(i))
        info_db.commit()
    #    org.wayround.utils.file.progress_write_finish()

        logging.info("Totally loaded {} records".format(loaded))
        return


class Tags(org.wayround.utils.tag.TagEngine):
    pass


class TagsControl:

    def __init__(self, tag_db, tags_json):

        self.tag_db = tag_db
        self.tags_json = tags_json

    def load_tags_from_fs(self):

        tag_db = self.tag_db

        file_name = self.tags_json

        try:
            f = open(file_name, 'r')
        except:
            logging.exception("Couldn't open file `{}'".format(file_name))
        else:
            try:
                txt = f.read()

                d = json.loads(txt)

                tag_db.clear()

                keys = list(d.keys())
                keys.sort()

                count = len(keys)
                num = 0
                for i in keys:
                    num += 1

                    if num == 0:
                        perc = 0
                    else:
                        perc = float(100) / (float(count) / float(num))
                    org.wayround.utils.terminal.progress_write(
                        '    {:6.2f}%'.format(perc)
                        )
                    tag_db.set_tags(i, d[i])

                org.wayround.utils.terminal.progress_write_finish()
            finally:

                f.close()

        return

    def save_tags_to_fs(self):

        tag_db = self.tag_db

        file_name = self.tags_json

        logging.info("Getting tags from DB")

        d = tag_db.get_objects_and_tags_dict()

        logging.info("Creating JSON object")

        txt = json.dumps(d, sort_keys=True, indent=2)

        logging.info("Saving to file `{}'".format(file_name))
        try:
            f = open(file_name, 'w')
        except:
            logging.exception("Couldn't create file `{}'".format(file_name))
        else:
            try:
                f.write(txt)
            except:
                raise
            else:
                logging.info("Saved")
            finally:

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


def filter_text_parse(filter_text):
    """
    Returns list of command structures

    ret = [
        dict(
            action   = '-' or '+',
            subject  = in ['path', 'filename', 'version', 'status'],
            function = <depends on subject> (no spaces allowed),
            data     = <depends on subject> (can contain spaces)
            )
        ]

    """
    ret = []

    lines = filter_text.splitlines()

    for i in lines:
        if not i.isspace():
            struct = i.split(' ', maxsplit=3)
            if not len(struct) == 4:
                logging.error("Wrong filter line: `{}'".format(i))
            else:
                struct = dict(
                    action=struct[0],
                    subject=struct[1],
                    function=struct[2],
                    data=struct[3],
                    )
                ret.append(struct)

    return ret


def filter_tarball_list(input_list, filter_text):

    """
    Filters supplied list with supplied filter

    subjects not in check_for_subjects will always be positive (but can be
    filtered out by proper leading rules)
    """

    ret = []

    inp_list = set(copy.copy(input_list))
    out_list = copy.copy(inp_list)

    filters = filter_text_parse(filter_text)

    for f in filters:

        action = f['action']
        subject = f['subject']
        function = f['function']
        no = False
        data = f['data']

        if not action in ['+', '-']:
            logging.error("Wrong action: `{}'".format(action))
            ret = 10
            break

        if function.startswith('!'):
            no = True
            function = function[1:]

        if not subject in ['filename', 'version', 'status']:
            logging.error("Wrong subject : `{}'".format(subject))
            ret = 1
            break

        if subject == 'filename' or subject == 'status':

            if not function in ['begins', 'contains', 'ends', 'fm', 're']:
                logging.error(
                    "Wrong `{}' function : `{}'".format(subject, function)
                    )
                ret = 3
                break

        elif subject == 'version':

            if not function in [
                    '<', '<=', '==', '>=', '>', 're', 'fm',
                    'begins', 'contains', 'ends'
                    ]:
                logging.error(
                    "Wrong `version' function : `{}'".format(function)
                    )
                ret = 4
                break

        else:
            raise Exception("Programming error")

        if not isinstance(ret, int):

            working_list = None

            if action == '+':
                working_list = copy.copy(inp_list)

            elif action == '-':
                working_list = copy.copy(out_list)
            else:
                raise Exception("Programming Error")

            for item in working_list:

                working_item = item

                if subject == 'filename':
                    working_item = os.path.basename(item)

                elif subject in ['version', 'status']:

                    working_item = None

                    parsed = org.wayround.utils.tarball_name_parser.\
                        parse_tarball_name(
                            os.path.basename(item),
                            mute=True
                            )

                    if not isinstance(parsed, dict):
                        # TODO: it's not error, but may be it's need to do
                        # something than just a `pass'
                        pass
                    else:
                        if subject == 'version':
                            working_item = parsed['groups']['version']

                        elif subject == 'status':
                            working_item = parsed['groups']['status']

                        else:
                            raise Exception("Programming error")

                else:
                    raise Exception("Programming error")

                matched = False

                if function == 'begins':
                    matched = working_item.startswith(data)

                elif function == 'contains':
                    matched = working_item.find(data) != -1

                elif function == 'end':
                    matched = working_item.endswith(data)

                elif function == 're':
                    matched = re.match(data, working_item) != None

                elif function == 'fm':
                    logging.debug(
                        "filter_tarball_list: "
                        "fm-matching `{}' and `{}'".format(
                            working_item,
                            data
                            )
                        )
                    matched = fnmatch.fnmatch(working_item, data)

                elif function in ['<', '<=', '==', '>=', '>']:
                    matched = (
                        org.wayround.aipsetup.version.lb_comparator(
                            working_item,
                            function + ' ' + data
                            )
                        )
                else:
                    raise Exception("Programming error")

                if no:
                    matched = not matched

                if matched:

                    logging.debug(
                        "filter_tarball_list: "
                        "match: `{}'\n       `{}'".format(item, f)
                        )

                    if action == '+':
                        logging.debug(
                            "filter_tarball_list: adding: {}".format(item)
                            )
                        out_list.add(item)

                    elif action == '-':
                        logging.debug(
                            "filter_tarball_list: removing: {}".format(
                                item
                                )
                            )
                        if item in out_list:
                            out_list.remove(item)

                    else:
                        raise Exception("Programming error")

                else:
                    logging.debug(
                        "filter_tarball_list: NOT "
                        "match: `{}'\n       `{}'".format(item, f)
                        )

    if not isinstance(ret, int):
        ret = out_list

    if isinstance(ret, set):
        ret = list(ret)

    return ret
