
import os.path
import logging
import time
import functools

import cherrypy

import org.wayround.utils.xml

import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.version


def pathed_css_path_renderer(obj, inname):
    return 'css/' + inname

def pathed_js_path_renderer(obj, inname):
    return 'js/' + inname

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
                        module='categories',
                        uid='single-page-cat-category-div',
                        content=[
                            org.wayround.utils.xml.tag(
                                'a',
                                attributes={
                                    'href': 'category?path={}'.format(cat_path)
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'img',
                                        closed=True,
                                        attributes={
                                            'alt': 'open',
                                            'src': 'css/icons/icons/folder.png',
                                            },
                                        ),
                                    ' ',
                                    db.get_category_by_id(i)
                                    ]
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
                module='categories',
                uid='single-page-cat-package-div',
                content=[
                    org.wayround.utils.xml.tag(
                        'a',
                        attributes={
                            'href': 'package?name={}'.format(package_name)
                            },
                        content=[
                            org.wayround.utils.xml.tag(
                                'img',
                                closed=True,
                                attributes={
                                    'alt': 'open',
                                    'src': 'css/icons/icons/package-x-generic.png',
                                    },
                                ),
                            ' ',
                            package_name
                            ]
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
                            'href': 'category?path={}'.format(parent_cat_path)
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
        module='categories',
        uid='single-page-div',
        required_css=['single-page-div.css'],
        content=ret
        )

    return ret

def page_category(db, path):

    head = org.wayround.utils.xml.html_head(
        path
        )

    table = category(db, path)

    tree = org.wayround.utils.xml.html(
        head=head,
        content=[table],
        body_module='aipsetup_server_basic',
        body_uid='body',
        body_css=['body.css']
        )

    renderer = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True,
        css_and_js_holder=head
        )

    renderer.set_tree(tree)

    txt = renderer.render(
        pathed_css_path_renderer,
        pathed_js_path_renderer
        )

    if len(renderer.log) != 0:
        # TODO: rework this
        for i in renderer.log:
            print(i)
        txt = 'Error'

    return txt

class TimestampSortKey:

    def __init__(self, files_dict):
        self.files_dict = files_dict

    def timestamp_sort_key(self, i):
        return self.files_dict[i]['groups']['timestamp']

def package_file_list(db, name):

    files = org.wayround.aipsetup.pkgindex.get_package_files(name)

    keys = list(files.keys())

    tsk = TimestampSortKey(files)

    keys.sort(key=tsk.timestamp_sort_key, reverse=True)

    del tsk

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
                                    'href': package_url,
                                    'title': "Download File"
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'img',
                                        closed=True,
                                        attributes={
                                            'alt': 'download',
                                            'src': 'css/icons/icons/document-save.png',
                                            },
                                        ),
                                    ' ',
                                    files[i]['groups']['version']
                                    ]
                                )
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content=files[i]['groups']['timestamp']
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
                        content="Version"
                        ),
                    org.wayround.utils.xml.tag(
                        'th',
                        content="Timestamp"
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
        module='package-info-module',
        uid='file-list-table',
        required_css=['file-list-table.css'],
        content=rows
        )

    return table


def package_sources_file_list(db, name):

    files = org.wayround.aipsetup.pkgindex.get_package_source_files(name)

    org.wayround.utils.list.list_sort(
        files,
        cmp=org.wayround.aipsetup.version.source_version_comparator
        )

    files.reverse()

    rows = []

    for i in files:

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
                                    'href': source_url,
                                    'title': "Download File"
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'img',
                                        closed=True,
                                        attributes={
                                            'alt': 'download',
                                            'src': 'css/icons/icons/document-save.png',
                                            },
                                        ),
                                    ' ',
                                    os.path.basename(i)
                                    ]
                                )
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content=os.path.dirname(i)[1:]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content="{m:.2f}MiB".format(
                            m=float(source_filesize) / 1024 / 1024
                            )
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        content=str(source_moddate)
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
                        content="Path"
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
        module='package-info-module',
        uid='file-list-table',
        required_css=['file-list-table.css'],
        content=rows
        )

    return table


def package_info(db, name):

    package_info = db.package_info_record_to_dict(name)
    logging.debug(
        "package_info: package_info_record_to_dict({}) == {}".format(
            name,
            package_info
            )
        )

    ret = None

    if package_info == None:
        raise cherrypy.HTTPError(404, "No page for package `{}'".format(name))
    else:

        cid = db.get_package_category_by_name(name)
        if cid != None:
            category = db.get_category_path_string(cid)
        else:
            category = "< Package not indexed! >"

        ret = org.wayround.utils.xml.tag(
            'div',
            module='package-info-module',
            uid='info-div',
            required_css=['info-div.css'],
            content=[
                 org.wayround.utils.xml.tag(
                    'table',
                    module='package-info-module',
                    uid='info-info-table',
                    required_css=['info-info-table.css'],

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
                                            content='basename:'
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
                                            content=package_info['basename']
                                            )
                                        ]
                                    ),
                                org.wayround.utils.xml.tag(
                                    'td',
                                    attributes={
                                        'rowspan': '6'
                                        },
                                    content=[
                                        org.wayround.utils.xml.tag(
                                            'pre',
                                            new_line_before_content=False,
                                            new_line_after_content=False,
                                            content=package_info['description']
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
                                            content='version regexp:'
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
                                            content=package_info['version_re']
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
                                            content=package_info['buildinfo']
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
                                                        'href': package_info['home_page'],
                                                        'target': '_blank'
                                                        },
                                                    content=package_info['home_page']
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
                                                        'href': "category?path={}".format(category)
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
                                            content=', '.join(package_info['tags'])
                                            )
                                        ]
                                    )
                                ]
                            ),
                        ]
                    )
                ]
            )

    return ret


def page_package(db, name):

    cid = db.get_package_category_by_name(name)
    if cid != None:
        category = db.get_category_path_string(cid)
    else:
        category = "< Package not indexed! >"

    table = org.wayround.utils.xml.tag(
        'table',
        module='package-info-module',
        uid='info-upper-table',
        required_css=['info-upper-table.css'],
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
                            org.wayround.utils.xml.tag(
                                'h1',
                                content=name
                                ),
                            ]
                        )
                    ]
                ),
            org.wayround.utils.xml.tag(
                'tr',
                content=[
                    org.wayround.utils.xml.tag(
                        'td',
                        module='package-info-module',
                        uid='info-upper-table-buttons-cell',
                        required_css=['info-upper-table-buttons-cell.css'],
                        attributes={
                            'colspan': '2'
                            },
                        content=[
                            org.wayround.utils.xml.tag(
                                'form',
                                attributes={
                                    'action': "..",
                                    'mode': 'GET'
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'button',
                                        attributes={
                                            'type': 'submit',
                                            },
                                        content=[
                                            org.wayround.utils.xml.tag(
                                                'img',
                                                closed=True,
                                                attributes={
                                                    'src': 'css/icons/icons/go-home.png',
                                                    'alt': "Go Home"
                                                    }
                                                ),
                                            " ",
                                            "Go Home"
                                            ]
                                        )
                                    ]
                                ),
                            org.wayround.utils.xml.tag(
                                'form',
                                attributes={
                                    'action': "category",
                                    'mode': 'GET'
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'button',
                                        attributes={
                                            'type': 'submit',
                                            'name': 'path',
                                            'value': category
                                            },
                                        content=[
                                            org.wayround.utils.xml.tag(
                                                'img',
                                                closed=True,
                                                attributes={
                                                    'src': 'css/icons/icons/go-up.png',
                                                    'alt': "Up to category"
                                                    }
                                                ),
                                            " ",
                                            "{}".format(category)
                                            ]
                                        )
                                    ]
                                ),


                            org.wayround.utils.xml.tag(
                                'form',
                                attributes={
                                    'action': "",
                                    'mode': 'GET'
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'input',
                                        closed=True,
                                        attributes={
                                            'type': 'hidden',
                                            'name': 'name',
                                            'value': name
                                            }
                                        ),
                                    org.wayround.utils.xml.tag(
                                        'input',
                                        closed=True,
                                        attributes={
                                            'type': 'hidden',
                                            'name': 'mode',
                                            'value': 'packages'
                                            }
                                        ),
                                    org.wayround.utils.xml.tag(
                                        'button',
                                        attributes={
                                            'type': 'submit'
                                            },
                                        content=[
                                            org.wayround.utils.xml.tag(
                                                'img',
                                                closed=True,
                                                attributes={
                                                    'src': 'css/icons/icons/gnome-mime-application-x-cd-image.png',
                                                    'alt': "Packages JSON"
                                                    }
                                                ),
                                            " ",
                                            "Packages JSON"
                                            ]
                                        )
                                    ]
                                ),
                            org.wayround.utils.xml.tag(
                                'form',
                                attributes={
                                    'action': "",
                                    'mode': 'GET'
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'input',
                                        closed=True,
                                        attributes={
                                            'type': 'hidden',
                                            'name': 'name',
                                            'value': name
                                            }
                                        ),
                                    org.wayround.utils.xml.tag(
                                        'input',
                                        closed=True,
                                        attributes={
                                            'type': 'hidden',
                                            'name': 'mode',
                                            'value': 'sources'
                                            }
                                        ),
                                    org.wayround.utils.xml.tag(
                                        'button',
                                        attributes={
                                            'type': 'submit'
                                            },
                                        content=[
                                            org.wayround.utils.xml.tag(
                                                'img',
                                                closed=True,
                                                attributes={
                                                    'src': 'css/icons/icons/gnome-mime-application-x-cd-image.png',
                                                    'alt': "Sources JSON"
                                                    }
                                                ),
                                            " ",
                                            "Sources JSON"
                                            ]
                                        )
                                    ]
                                ),
                            org.wayround.utils.xml.tag(
                                'form',
                                attributes={
                                    'action': "",
                                    'mode': 'GET'
                                    },
                                content=[
                                    org.wayround.utils.xml.tag(
                                        'input',
                                        closed=True,
                                        attributes={
                                            'type': 'hidden',
                                            'name': 'name',
                                            'value': name
                                            }
                                        ),
                                    org.wayround.utils.xml.tag(
                                        'input',
                                        closed=True,
                                        attributes={
                                            'type': 'hidden',
                                            'name': 'mode',
                                            'value': 'info'
                                            }
                                        ),
                                    org.wayround.utils.xml.tag(
                                        'button',
                                        attributes={
                                            'type': 'submit'
                                            },
                                        content=[
                                            org.wayround.utils.xml.tag(
                                                'img',
                                                closed=True,
                                                attributes={
                                                    'src': 'css/icons/icons/gnome-mime-application-x-cd-image.png',
                                                    'alt': "Info JSON"
                                                    }
                                                ),
                                            " ",
                                            "Info JSON"
                                            ]
                                        )
                                    ]
                                ),
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
                        attributes={
                            'valign':'top'
                            },
                        content=[
                            package_file_list(db, name)
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        attributes={
                            'valign':'top'
                            },
                        content=[
                            package_sources_file_list(db, name)
                            ]
                        )
                    ]
                )
            ]
        )

    head = org.wayround.utils.xml.html_head(
        name
        )

    tree = org.wayround.utils.xml.html(
        head=head,
        content=[table],
        body_module='aipsetup_server_basic',
        body_uid='body',
        body_css=['body.css']
        )

    renderer = org.wayround.utils.xml.DictTreeToXMLRenderer(
        xml_indent_size=2,
        generate_css=True,
        generate_js=True,
        css_and_js_holder=head
        )

    renderer.set_tree(tree)

    txt = renderer.render(
        pathed_css_path_renderer,
        pathed_js_path_renderer
        )

    if len(renderer.log) != 0:
        # TODO: rework this
        for i in renderer.log:
            print(i)
        txt = 'Error'

    del renderer

#    print(pprint.pformat(tree, 4))

    return txt


