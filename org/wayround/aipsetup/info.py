
"""
XML info files manipulations.

Print, read, write, fix info files.
"""

import os.path
import copy
import glob
import logging
import json

import org.wayround.utils.file
import org.wayround.utils.edit

import org.wayround.aipsetup.config
import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.name
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkginfo


SAMPLE_PACKAGE_INFO_STRUCTURE = dict(
    # description
    description="",

    # not required, but can be useful
    home_page="",

    # string
    buildscript='',

    # file name base
    basename='',

    # prefix for filtering source files
    src_path_prefix='',

    # filters. various filters to provide correct list of acceptable tarballs by
    # they filenames
    filters='',

    # from 0 to 9. default 5. lower number - higher priority
    installation_priority=5,

    # can package be deleted without hazard to aipsetup functionality (including
    # system stability)?
    removable=True,

    # can package be updated without hazard to aipsetup functionality (including
    # system stability)?
    reducible=True,

    # package can not be installed
    non_installable=False,

    # package outdated and need to be removed
    deprecated=False,

    # can aipsetup automatically find and update latest version? (can't not for
    # files containing statuses, e.g. openssl-1.0.1a.tar.gz, where 'a' is
    # status)
    auto_newest_src=True,

    # can aipsetup automatically find and update latest version? (can't not for
    # files containing statuses, e.g. openssl-1.0.1a.tar.gz, where 'a' is
    # status)
    auto_newest_pkg=True,
    )

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
#    <auto_newest_src value="${ auto_newest_src | x }"/>
#    <auto_newest_pkg value="${ auto_newest_pkg | x }"/>
#
#</package>
#""")

def exported_commands():
    return {
        'fix': info_mass_info_fix,
        'list': info_list_files,
        'edit': info_edit_file,
        'editor': info_editor,
        'copy': info_copy,
        'script': info_mass_script
        }

def commands_order():
    return [
        'editor',
        'list',
        'edit',
        'copy',
        'fix',
        'script'
        ]

def cli_name():
    return 'i'

def info_list_files(opts, args, typ='info', mask='*.json'):
    """
    List XML files in pkg_info dir of UNICORN dir

    [FILEMASK]

    One argument is allowed - FILEMASK, which defaults to '*.json'

    example:
    aipsetup info list '*doc*.json'
    """

    args_l = len(args)

    if args_l > 1:
        logging.error("Too many arguments")
    else:

        if args_l == 1:
            mask = args[0]

        # FIXME: what's this?
        org.wayround.utils.file.list_files(
            org.wayround.aipsetup.config.config[typ], mask
            )

    return 0

def info_edit_file(opts, args, typ='info'):
    """
    Edit selected info-file in editor designated in aipsetup.conf

    FILENAME

    One argument required - FILENAME
    """
    ret = 0
    if len(args) != 1:
        logging.error("file to edit not specified")
        ret = 1
    else:
        ret = org.wayround.utils.edit.edit_file(
            os.path.join(
                org.wayround.aipsetup.config.config[typ],
                args[0]
                ),
            org.wayround.aipsetup.config.config['editor']
            )
    return ret

def info_editor(opts, args):
    """
    Start special info-file editor
    """
    import org.wayround.aipsetup.infoeditor

    ret = 0

    file_name = None
    len_args = len(args)
    if len_args == 0:
        pass
    elif len_args == 1:
        file_name = args[0]
    else:
        ret = 1

    if ret == 0:

        if isinstance(file_name, str) and os.path.isfile(file_name):

            pkg_name = (
                org.wayround.aipsetup.pkginfo.get_package_name_by_tarball_filename(file_name)
                )

            if not pkg_name:
                logging.error(
                    "Could not find package name of `{}'".format(
                        file_name
                        )
                    )
                ret = 4
            else:
                file_name = pkg_name

        if isinstance(file_name, str):
            if not file_name.endswith('.json'):
                file_name = file_name + '.json'
        org.wayround.aipsetup.infoeditor.main(file_name)

    return ret

def info_copy(opts, args):
    """
    Creates a copy of one info file into another

    OLDNAME NEWNAME
    """
    if len(args) != 2:
        logging.error("wrong argument count")
    else:

        org.wayround.utils.file.inderictory_copy_file(
            org.wayround.aipsetup.config.config['info'],
            args[0],
            args[1]
            )

    return 0

def info_mass_info_fix(opts, args):
    """
    Does various .json info files fixes

    [--forced-homepage-fix]

    --forced-homepage-fix    forces fixes on homepage fields
    """

    lst = glob.glob(os.path.join(org.wayround.aipsetup.config.config['info'], '*.json'))
    lst.sort()

    forced_homepage_fix = '--forced-homepage-fix' in opts

    lst_c = len(lst)
    lst_i = 0

    for i in lst:

        name = os.path.basename(i)[:-5]

        dicti = read_from_file(i)

        info_fixes(dicti, name, forced_homepage_fix)

        write_to_file(i, dicti)

        lst_i += 1

        org.wayround.utils.file.progress_write(
            "    {:3.0f}% ({}/{})".format(
                100.0 / (lst_c / lst_i),
                lst_i,
                lst_c
                )
            )

    org.wayround.utils.file.progress_write_finish()

    logging.info("Processed {} files".format(lst_c))

    return 0

def info_mass_script(opts, args):
    """
    Mass buildscript applience

    scriptname [-f] [tarballs list]

    -f    force (by default new script name will not be applied to
          records with existing ones)
    """

    ret = 0

    sources = []

    force = '-f' in opts


    script_name = None

    if len(args) > 0:
        script_name = args[0]

    if len(args) > 1:
        sources = args[1:]

    if script_name == None:
        logging.error("Script name required")
        ret = 3

    if len(sources) == 0:
        logging.error("No source files named")
        ret = 2

    if ret == 0:


        for i in sources:

            pkg_name = (
                org.wayround.aipsetup.pkginfo.get_package_name_by_tarball_filename(i)
                )

            if not pkg_name:
                logging.error("Could not find package name of `{}'".format(i))
                ret = 4
            else:

                info_dir = org.wayround.aipsetup.config.config['info']

                p1 = info_dir + os.path.sep + pkg_name + '.json'

                info = read_from_file(p1)

                if not isinstance(info, dict):
                    logging.error("Wrong info {}".format(p1))
                    ret = 5
                else:

                    if force or info['buildscript'] == '':
                        info['buildscript'] = script_name

                        write_to_file(p1, info)

                        logging.info("Applied to {}".format(pkg_name))
                    else:
                        logging.warning(
                            "{} already have defined script".format(
                                pkg_name
                                )
                            )


        org.wayround.aipsetup.pkginfo.update_outdated_pkg_info_records()

    return ret

def _find_latest(tree, tag, field):
    y = None
    x = tree.findall(tag)
    if len(x) > 0:
        y = x[-1].get(field)
    return y

def _find_list(tree, tag, field):
    y = []
    x = tree.findall(tag)
    lx = len(x)
    for i in range(lx):
        z = x[i].get(field)
        if isinstance(z, str):
            y.append(z)
    return y

def is_info_dicts_equal(d1, d2):

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
        'auto_newest_src',
        'auto_newest_pkg',
        'src_path_prefix'
        ]:
        if d1[i] != d2[i]:
            ret = False
            break

    return ret

def read_from_file(name):
    ret = None

    txt = ''
    tree = None

    try:
        f = open(name, 'r')
    except:
        logging.exception(
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

def write_to_file(name, struct):

    ret = 0

    struct = copy.copy(struct)

    if 'name' in struct:
        del struct['name']

    txt = json.dumps(struct, indent=2, sort_keys=True)

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

def info_fixes(
    info, pkg_name,
    forced_homepage_fix=False
    ):
    """
    This function is used by `info_mass_info_fix'

    Sometime it will contain checks and fixes for
    info files
    """
    # TODO: re do all this when aipsetup will be more or less complete
    raise Exception("Outdated")

    if info['basename'] == '':
        info['basename'] = pkg_name

    if forced_homepage_fix or info['home_page'] in ['', 'None']:
        possibilities = org.wayround.aipsetup.pkginfo.guess_package_homepage(
            pkg_name
            )

        keys = list(possibilities.keys())

        homepage = None
        if len(keys) > 0:
            max_key = keys[0]
            max = possibilities[max_key]

            for i in keys:
                if possibilities[i] > max:
                    max_key = i
                    max = possibilities[i]

            homepage = max_key

        info['home_page'] = 'http://' + str(homepage)
