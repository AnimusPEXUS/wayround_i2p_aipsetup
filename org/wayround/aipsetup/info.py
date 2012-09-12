
"""
XML info files manipulations.

Print, read, write, fix info files.
"""

import os.path
import copy
import glob
import logging

try:
    import lxml.etree
except:
    logging.exception("lxml xml pareser is required")
    raise

try:
    from mako.template import Template
except:
    logging.exception("mako template engine is required")
    raise


import org.wayround.utils.file
import org.wayround.utils.edit
import org.wayround.utils.tag

import org.wayround.aipsetup.config
import org.wayround.aipsetup.name
import org.wayround.aipsetup.pkgindex


SAMPLE_PACKAGE_INFO_STRUCTURE = dict(
    # description
    description="",
    # not required, but can be useful
    home_page="",
    # string list
    tags=[],
    # string
    buildinfo='',
    # file name base
    basename='',
    # acceptable version regexp
    version_re='',
    # from 0 to 9. default 5. lower number - higher priority
    installation_priority=5,
    # can package be deleted without hazard to aipsetup functionality 
    # (including system stability)?
    removable=True,
    # can package be updated without hazard to aipsetup functionality 
    # (including system stability)?
    reducible=True,
    # can aipsetup automatically find and update latest version? 
    # (can't not for files containing statuses, 
    #  e.g. openssl-1.0.1a.tar.gz, where 'a' is status)
    auto_newest_src=True,
    # can aipsetup automatically find and update latest version? 
    # (can't not for files containing statuses, 
    #  e.g. openssl-1.0.1a.tar.gz, where 'a' is status)
    auto_newest_pkg=True,
    )

pkg_info_file_template = Template(text="""\
<package>

    <!-- This file is generated using aipsetup v3 -->

    <description>${ description | x}</description>

    <home_page url="${ home_page | x}"/>

    % if len(tags) == 0:
    <!-- Use <tag name="" /> constructions for listing
         tags -->
    % endif
    % for i in tags:
    <tag name="${ i | x}"/>
    % endfor

    <buildinfo value="${ buildinfo | x }"/>

    <basename value="${ basename | x }"/>

    <version_re value="${ version_re | x }"/>

    <installation_priority value="${ installation_priority | x }"/>

    <removable value="${ removable | x }"/>
    <reducible value="${ reducible | x }"/>

    <auto_newest_src value="${ auto_newest_src | x }"/>
    <auto_newest_pkg value="${ auto_newest_pkg | x }"/>

</package>
""")

def exported_commands():
    return {
        'mass_info_fix': info_mass_info_fix,
        'list': info_list_files,
        'edit': info_edit_file,
        'editor': info_editor,
        'copy': info_copy
        }

def commands_order():
    return [
        'editor',
        'list',
        'edit',
        'copy',
        'mass_info_fix'
        ]

def info_list_files(opts, args, typ='info', mask='*.xml'):
    """
    List XML files in pkg_info dir of UNICORN dir

    [FILEMASK]

    One argument is allowed - FILEMASK, which defaults to '*.xml'

    example:
    aipsetup info list '*doc*.xml'
    """

    args_l = len(args)

    if args_l > 1:
        logging.error("Too many arguments")
    else:

        if args_l == 1:
            mask = args[0]

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
    Does various .xml info files fixes

    [--forced-homepage-fix]

    --forced-homepage-fix    forces fixes on homepage fields
    """

    lst = glob.glob(os.path.join(org.wayround.aipsetup.config.config['info'], '*.xml'))
    lst.sort()

    forced_homepage_fix = '--forced-homepage-fix' in opts

    lst_c = len(lst)
    lst_i = 0

    src_db = org.wayround.utils.tag.TagEngine(
        org.wayround.aipsetup.config.config['source_index']
        )

    for i in lst:

        name = os.path.basename(i)[:-4]

        dicti = read_from_file(i)

        info_fixes(dicti, name, src_db, forced_homepage_fix)

        write_to_file(i, dicti)

        lst_i += 1

        org.wayround.utils.file.progress_write(
            "    {:3.0f}% ({}/{})".format(
                100.0 / (lst_c / lst_i),
                lst_i,
                lst_c
                )
            )

    del src_db

    org.wayround.utils.file.progress_write_finish()

    logging.info("Processed %(n)d files" % {
        'n': len(lst)
        })

    return 0


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
        'buildinfo',
        'basename',
        'version_re',
        'installation_priority',
        'removable',
        'reducible',
        'auto_newest_src',
        'auto_newest_pkg',
        # next two items must not participate in
        # equality checks, as they changing too often
        # 'newest_src',
        # 'newest_pkg'
        ]:
        if d1[i] != d2[i]:
            ret = False
            break

    if ret:
        for i in ['tags']:

            if ret:
                for each in d1[i]:
                    if not each in d2[i]:
                        ret = False
                        break

            if ret:
                for each in d2[i]:
                    if not each in d1[i]:
                        ret = False
                        break

            if not ret:
                break

    return ret

def read_from_file(name):
    ret = None

    txt = ''
    tree = None

    try:
        f = open(name, 'r')
    except:
        logging.exception("Can't open file %(name)s" % {
            'name': name
            })
        ret = 1
    else:
        try:
            txt = f.read()

            try:
                tree = lxml.etree.fromstring(txt)
            except:
                logging.exception("Can't parse file `%(name)s'" % {
                    'name': name
                    })
                ret = 2
            else:
                ret = copy.copy(SAMPLE_PACKAGE_INFO_STRUCTURE)

                x = _find_latest(tree, 'installation_priority', 'value')
                if x != None:
                    try:
                        x = int(x)
                    except:
                        x = 5

                    if x >= 0 and x <= 9:
                        ret['installation_priority'] = x
                    else:
                        raise ValueError(
                            "Wrong installation_priority value in `{}'".format(
                                name
                                )
                            )

                for i in [
                    'removable',
                    'reducible',
                    'auto_newest_src',
                    'auto_newest_pkg'
                    ]:
                    x = _find_latest(tree, i, 'value')
                    if x != None:
                        if not x in ['True', 'False']:
                            raise ValueError(
                                "Wrong `{}' value in `{}'".format(
                                    i,
                                    name
                                    )
                                )
                        else:
                            ret[i] = eval(x)


                for i in [
                    ('buildinfo', 'value'),
                    ('home_page', 'url'),
                    ('basename', 'value'),
                    ('version_re', 'value'),
                    ]:

                    x = _find_latest(tree, i[0], i[1])
                    if x != None:
                        ret[i[0]] = x

                x = tree.findall('description')
                if len(x) > 0:
                    ret['description'] = x[-1].text

                ret['tags'] = _find_list(tree, 'tag', 'name')

                ret['tags'].sort()

                ret['name'] = name
                del(tree)
        finally:
            f.close()

    return ret

def write_to_file(name, struct):

    ret = 0

    struct['tags'].sort()

    txt = pkg_info_file_template.render(
        description=struct['description'],
        home_page=struct['home_page'],
        tags=struct['tags'],
        buildinfo=struct['buildinfo'],
        basename=struct['basename'],
        version_re=struct['version_re'],
        installation_priority=struct['installation_priority'],
        removable=struct['removable'],
        reducible=struct['reducible'],
        auto_newest_src=struct['auto_newest_src'],
        auto_newest_pkg=struct['auto_newest_pkg']
#        newest_src=struct['newest_src'],
#        newest_pkg=struct['newest_pkg']
        )

    try:
        f = open(name, 'w')
    except:
        logging.exception("Can't rewrite file %(name)s" % {
            'name': name
            })
        ret = 1
    else:
        try:
            f.write(txt)
        finally:
            f.close()

    return ret

def info_fixes(info, pkg_name, src_db_connected=None, forced_homepage_fix=False):
    """
    This function is used by `info_mass_info_fix'

    Sometime it will contain checks and fixes for
    info files
    """

    if info['basename'] == '':
        info['basename'] = pkg_name

    if info['version_re'] == '':
        info['version_re'] = '.*'

    if forced_homepage_fix or info['home_page'] in ['', 'None']:
        possibilities = org.wayround.aipsetup.pkgindex.guess_package_homepage(
            pkg_name,
            src_db_connected
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
