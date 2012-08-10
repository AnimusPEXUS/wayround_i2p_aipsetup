
import os.path
import logging
import time

import cherrypy

import org.wayround.utils.xml
import org.wayround.utils.dict


import org.wayround.aipsetup.pkgindex


def page_index():

    tree = org.wayround.utils.xml.html(
        title="Unicorn distribution server",
        content=[]
        )

    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True,
        css_and_js_holder=tree['00020_html']['content']['00010_head']
        )

    a.set_tree(tree)

    txt = a.render()

    if len(a.log) != 0:
        # TODO: rework this
        for i in a.log:
            print(i)
        txt = 'Error'

    return txt


def page_pkg_list(db_connection):

#    db = org.wayround.aipsetup.pkgindex.PackageDatabase()
#    lst = db.ls_packages()
#    del db


#    pack_sel = pkg_select(lst, lst)

    tree = org.wayround.utils.xml.html(
        title="Unicorn distribution server",
        content=[category_tree(db_connection)]
        )

    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True,
        css_and_js_holder=tree['00020_html']['content']['00010_head']
        )

    a.set_tree(tree)

    txt = a.render()

    if len(a.log) != 0:
        # TODO: rework this
        for i in a.log:
            print(i)
        txt = 'Error'

    return txt


def _category_tree(start_cat_id=0, db=None):

    logging.debug("Getting package ids in cat {}".format(start_cat_id))
    pack_ids = db.ls_package_ids(start_cat_id)
    logging.debug("Getting cat ids in cat {}".format(start_cat_id))
    cats_ids = db.ls_category_ids(start_cat_id)

    cats_tags = []
    pack_tags = []

    logging.debug("Formatting cats in cat {}".format(start_cat_id))

    for i in cats_ids:

        cat_path = db.get_category_path_string(i)

        cats_tags.append(
            org.wayround.utils.xml.tag(
                'div',
                attributes={
                    'class': 'dir_entry',
                    'style': 'border: 3px blue solid;'
                    },
                content=[
                    org.wayround.utils.xml.tag(
                        'div',
                        attributes={
                            'class': 'dir_title',
                            'style': 'padding-left: 10px; border: 3px green solid;'
                            },
                        content=cat_path
                        ),
                    org.wayround.utils.xml.tag(
                        'div',
                        attributes={
                            'class': 'dir_title_entries',
                            'style': 'border: 3px black solid;'
                            },
                        content=_category_tree(i, db)
                        )
                    ]
                )
            )

    logging.debug("Formatting packs in cat {}".format(start_cat_id))

    for i in pack_ids:
        pack_tags.append(
            org.wayround.utils.xml.tag(
                'div',
                attributes={
                    'class': 'pack_entry',
                    'style': 'padding-left: 10px; border: 3px red solid;'
                    },
                content=db.get_package_by_id(i)
                )
            )


    ret = cats_tags + pack_tags

    return ret



def category_tree(db):

    ret = org.wayround.utils.xml.tag(
        'div',
        content=_category_tree(0, db)
        )

    return ret

def category(db, path):

    cat_id = db.get_category_by_path(path)

    if cat_id == None:
        raise cherrypy.HTTPError(404, "Category not found")

    logging.debug("Category `{}' corresponds to path `{}'".format(cat_id, path))

    logging.debug("Getting package ids in cat {}".format(cat_id))
    pack_ids = db.ls_package_ids(cat_id)
    logging.debug("Getting cat ids in cat {}".format(cat_id))
    cats_ids = db.ls_category_ids(cat_id)

    cats_tags = []
    pack_tags = []

    logging.debug("Formatting cats in cat {}".format(cat_id))

    for i in cats_ids:

        cat_path = db.get_category_path_string(i)

        cats_tags.append(
            org.wayround.utils.xml.tag(
                'div',
                attributes={
                    'class': 'dir_entry'
                    },
                content=[
                    org.wayround.utils.xml.tag(
                        'div',
                        content=[
                            org.wayround.utils.xml.tag(
                                'a',
                                attributes={
                                    'href': 'directory?path={}'.format(cat_path)
                                    },
                                content='[CAT] {}'.format(db.get_category_by_id(i))
                                )
                            ]
                        )
                    ]
                )
            )

    logging.debug("Formatting packs in cat {}".format(cat_id))

    for i in pack_ids:
        package_name = db.get_package_by_id(i)
        pack_tags.append(
            org.wayround.utils.xml.tag(
                'div',
                content=[
                    org.wayround.utils.xml.tag(
                        'a',
                        attributes={
                            'href': 'package?name={}'.format(package_name)
                            },
                        content='[pac] {}'.format(package_name)
                        )
                    ]
                )
            )


    ret = cats_tags + pack_tags

    double_dot = []
    if cat_id != 0:
        parent_cat_id = db.get_category_parent_by_id(cat_id)
        parent_cat_path = db.get_category_path_string(parent_cat_id)

        double_dot = [
            org.wayround.utils.xml.tag(
                'div',
                content=[
                    org.wayround.utils.xml.tag(
                        'a',
                        attributes={
                            'href': 'directory?path={}'.format(parent_cat_path)
                            },
                        content=".. (Parent Category: '{}')".format(parent_cat_path)
                        )
                    ]
                )
            ]

    ret = double_dot + ret + double_dot

    ret.insert(
        0,
        org.wayround.utils.xml.tag(
            'h1',
            content='Category: {}'.format(db.get_category_path_string(cat_id))
            )
        )

    ret = org.wayround.utils.xml.tag(
        'div',
        content=ret
        )

    return ret

def page_category(db, path):

    cat = org.wayround.utils.xml.html(
        title='Category: {}'.format(path),
        content=[category(db, path)]
        )

    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True,
        css_and_js_holder=cat['00020_html']['content']['00010_head']
        )

    a.set_tree(cat)

    txt = a.render()

    if len(a.log) != 0:
        # TODO: rework this
        for i in a.log:
            print(i)
        txt = 'Error'

    return txt

def package_file_list(db, name):

    files = org.wayround.aipsetup.pkgindex.get_package_files(name)

    keys = list(files.keys())
    keys.sort()

    rows = []

    for i in keys:

        pid = db.get_package_id(name)
        package_path = db.get_package_path_string(pid)

        package_url = (
            'files_repository'
            + os.path.sep + package_path + os.path.sep + 'pack' + os.path.sep
            + files[i]['name'] + '.asp'
            )

        package_filename = os.path.abspath(
            org.wayround.aipsetup.config.config['repository']
            + os.path.sep + package_path + os.path.sep + 'pack' + os.path.sep
            + files[i]['name'] + '.asp'
            )

        try:
            package_file_stat = os.stat(package_filename)
        except:
            package_filesize = 0
            package_moddate = 0
        else:
            package_filesize = package_file_stat.st_size
            t = time.gmtime(package_file_stat.st_mtime)
            package_moddate = "{Y:04}-{M:02}-{D:02} {h:02}:{m:02}:{s:02}".format(
                Y=t.tm_year,
                M=t.tm_mon,
                D=t.tm_mday,
                h=t.tm_hour,
                m=t.tm_min,
                s=t.tm_sec
                )

        rows.append(
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'td',
                        content=[
                            org.wayround.utils.xml.tag(
                                'a',
                                attributes={
                                    'href': package_url
                                    },
                                content=files[i]['name']
                                )
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content="{m:.2f}MiB".format(
                            m=float(package_filesize) / 1024 / 1024
                            )
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content="{}".format(package_moddate)
                        )
                    ]
                )
            )

    if len(rows) == 0:
        rows.append(
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'td',
                        content="no packages found"
                        )
                    ]
                )
            )
    else:
        rows.insert(
            0,
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Package Name"
                        ),
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Size"
                        ),
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Modify"
                        )
                    ]
                )
            )

    table = org.wayround.utils.xml.tag(
        'table',
        content=rows
        )

    return table


def package_sources_file_list(db, name):

    files = org.wayround.aipsetup.pkgindex.get_package_source_files(name)

    keys = list(files.keys())
    keys.sort()

    rows = []

    for i in keys:

        source_url = 'files_source' + i

        source_filename = os.path.abspath(
            org.wayround.aipsetup.config.config['source']
            + i
            )

        try:
            source_file_stat = os.stat(source_filename)
        except:
            source_filesize = 0
            source_moddate = 0
        else:
            source_filesize = source_file_stat.st_size
            t = time.gmtime(source_file_stat.st_mtime)
            source_moddate = "{Y:04}-{M:02}-{D:02} {h:02}:{m:02}:{s:02}".format(
                Y=t.tm_year,
                M=t.tm_mon,
                D=t.tm_mday,
                h=t.tm_hour,
                m=t.tm_min,
                s=t.tm_sec
                )

        rows.append(
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'td',
                        content=[
                            org.wayround.utils.xml.tag(
                                'a',
                                attributes={
                                    'href': source_url
                                    },
                                content=files[i]['name']
                                )
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content="{m:.2f}MiB".format(
                            m=float(source_filesize) / 1024 / 1024
                            )
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content="{}".format(source_moddate)
                        )
                    ]
                )
            )

    if len(rows) == 0:
        rows.append(
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'td',
                        content="no sources found"
                        )
                    ]
                )
            )
    else:
        rows.insert(
            0,
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'th',
                        content="File Name"
                        ),
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Size"
                        ),
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Modify"
                        )
                    ]
                )
            )

    table = org.wayround.utils.xml.tag(
        'table',
        content=rows
        )

    return table


def package_info(db, name):

    dic = db.package_info_record_to_dict(name)
    logging.debug("package_info: package_info_record_to_dict({}) == {}".format(name, dic))

    ret = None

    if dic == None:
        raise cherrypy.HTTPError(404, "No page for package `{}'".format(name))
    else:

        cid = db.get_package_category_by_name(name)
        if cid != None:
            category = db.get_category_path_string(cid)
        else:
            category = "< Package not indexed! >"

        regexp = '< Wrong regexp type name >'
        if dic['pkg_name_type'] in org.wayround.aipsetup.name.NAME_REGEXPS:
            regexp = org.wayround.aipsetup.name.NAME_REGEXPS[dic['pkg_name_type']]

        ret = org.wayround.utils.xml.tag(
            'div',
            content=[
                org.wayround.utils.xml.tag(
                    'h1',
                    content="Package: {}".format(name)
                    ),
                 org.wayround.utils.xml.tag(
                    'table',
                    content=[
                        org.wayround.utils.xml.tag(
                            'tr',
                            content=[
                                org.wayround.utils.xml.tag(
                                    'td',
                                    attributes={
                                        'align': 'right'
                                        },
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'strong',
                                            content='file name type:'
                                            )
                                        ]
                                    ),
                                org.wayround.utils.xml.tag(
                                    'td',
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'pre',
                                            new_line_before_content=False,
                                            new_line_after_content=False,
                                            content=dic['pkg_name_type']
                                            )
                                        ]
                                    )
                                ]
                            ),
                        org.wayround.utils.xml.tag(
                            'tr',
                            content=[
                                org.wayround.utils.xml.tag(
                                    'td',
                                    attributes={
                                        'align': 'right'
                                        },
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'strong',
                                            content='filename regexp:'
                                            )
                                        ]
                                    ),
                                org.wayround.utils.xml.tag(
                                    'td',
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'pre',
                                            new_line_before_content=False,
                                            new_line_after_content=False,
                                            content=regexp
                                            )
                                        ]
                                    )
                                ]
                            ),
                        org.wayround.utils.xml.tag(
                            'tr',
                            content=[
                                org.wayround.utils.xml.tag(
                                    'td',
                                    attributes={
                                        'align': 'right'
                                        },
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'strong',
                                            content='buildinfo:'
                                            )
                                        ]
                                    ),
                                org.wayround.utils.xml.tag(
                                    'td',
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'pre',
                                            new_line_before_content=False,
                                            new_line_after_content=False,
                                            content=dic['buildinfo']
                                            )
                                        ]
                                    )
                                ]
                            ),
                        org.wayround.utils.xml.tag(
                            'tr',
                            content=[
                                org.wayround.utils.xml.tag(
                                    'td',
                                    attributes={
                                        'align': 'right'
                                        },
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'strong',
                                            content='homepage:'
                                            )
                                        ]
                                    ),
                                org.wayround.utils.xml.tag(
                                    'td',
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'pre',
                                            new_line_before_content=False,
                                            new_line_after_content=False,
                                            content=[
                                                org.wayround.utils.xml.tag(
                                                    'a',
                                                    new_line_before_start=False,
                                                    new_line_after_end=False,
                                                    attributes={
                                                        'href': dic['homepage']
                                                        },
                                                    content=dic['homepage']
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                        org.wayround.utils.xml.tag(
                            'tr',
                            content=[
                                org.wayround.utils.xml.tag(
                                    'td',
                                    attributes={
                                        'align': 'right'
                                        },
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'strong',
                                            content='category:'
                                            )
                                        ]
                                    ),
                                org.wayround.utils.xml.tag(
                                    'td',
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'pre',
                                            new_line_before_content=False,
                                            new_line_after_content=False,
                                            content=[
                                                org.wayround.utils.xml.tag(
                                                    'a',
                                                    new_line_before_start=False,
                                                    new_line_after_end=False,
                                                    attributes={
                                                        'href': "directory?path={}".format(category)
                                                        },
                                                    content=category
                                                    )
                                                ]
                                            )
                                        ]
                                    )
                                ]
                            ),
                        org.wayround.utils.xml.tag(
                            'tr',
                            content=[
                                org.wayround.utils.xml.tag(
                                    'td',
                                    attributes={
                                        'align': 'right'
                                        },
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'strong',
                                            content='tags:'
                                            )
                                        ]
                                    ),
                                org.wayround.utils.xml.tag(
                                    'td',
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'pre',
                                            new_line_before_content=False,
                                            new_line_after_content=False,
                                            content=', '.join(dic['tags'])
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )

    return ret


def page_package(db, name):

    table = org.wayround.utils.xml.tag(
        'table',
        content=[
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'td',
                        attributes={
                            'colspan': '2'
                            },
                        content=[
                            package_info(db, name)
                            ]
                        )
                    ]
                ),
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Packages"
                        ),
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Sources"
                        )
                    ]
                ),
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'td',
                        content=[
                            package_file_list(db, name)
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content=[
                            package_sources_file_list(db, name)
                            ]
                        )
                    ]
                )
            ]
        )

    tree = org.wayround.utils.xml.html(
        title="Unicorn distribution server",
        content=[table]
        )

    a = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True,
        css_and_js_holder=tree['00020_html']['content']['00010_head']
        )

    a.set_tree(tree)

    txt = a.render()

    if len(a.log) != 0:
        # TODO: rework this
        for i in a.log:
            print(i)
        txt = 'Error'

    return txt


def pkg_select(pkg_list, category_list):
    lst1 = []
    lst2 = []

    for i in pkg_list:
        lst1.append(
            org.wayround.utils.xml.tag(
                'option',
                attributes={
                    'value': i
                    },
                content=i
                )
            )

    for i in category_list:
        lst2.append(
            org.wayround.utils.xml.tag(
                'option',
                attributes={
                    'value': i
                    },
                content=i
                )
            )

    return org.wayround.utils.xml.tag(
        'div',
        content=[
            org.wayround.utils.xml.tag(
                'table',
                content=[
                    org.wayround.utils.xml.tag(
                        'tr',
                        content=[
                            org.wayround.utils.xml.tag(
                                'td',
                                content='Select Package'
                                )
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'tr',
                        content=[
                            org.wayround.utils.xml.tag(
                                'td',
                                content=category_tree()
                                )
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'tr',
                        content=[
                            org.wayround.utils.xml.tag(
                                'td',
                                content=[
                                        org.wayround.utils.xml.tag(
                                            'input',
                                            attributes={
                                                'name': 'pkgname',
                                                'type': 'text'
                                                },
                                            closed=True
                                            )
                                    ]
                                )
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'tr',
                        content=[
                            org.wayround.utils.xml.tag(
                                'td',
                                content=[
                                        org.wayround.utils.xml.tag(
                                            'button',
                                            attributes={
                                                'type': 'submit'
                                                },
                                            content="Go to package page"
                                            )
                                    ]
                                )
                            ]
                        )
                    ]
                )
            ]
        )

