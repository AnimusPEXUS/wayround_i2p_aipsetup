
import os.path
import logging
import time
import functools
import urllib.parse

import mako.template
import mako.filters

mako.filters.DEFAULT_ESCAPES['u_path'] = 'filters.u_path_escape'

def u_path_escape(text):
    return urllib.parse.quote(text)

mako.filters.u_path_escape = u_path_escape

#import cherrypy

import org.wayround.utils.path
import org.wayround.utils.xml

import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.pkglatest
import org.wayround.utils.version


class UI:

    def __init__(self, templates_dir):

        self.templates = {}

        for i in [
            'category',

#            'page_index',
#            'page_package',
#
            'package_file_list',
#            'package_sources_file_list',
#            'package_info',

            'category_double_dot',

            'package',

            'html'
            ]:
            self.templates[i] = mako.template.Template(
                filename=os.path.join(templates_dir, i + '.html')
                )

    def html(self, title, body):
        return self.templates['html'].render(
            title=title,
            body=body,
            js=[],
            css=['default.css']
            )

    def category(self, category_path, double_dot, categories, packages):

        return self.templates['category'].render(
            category_path=category_path,
            double_dot=double_dot,
            categories=categories,
            packages=packages
            )

    def category_double_dot(self, parent_path):

        return self.templates['category_double_dot'].render(
            parent_path=parent_path
            )

    def package_file_list(self, files):

        return self.templates['package_file_list'].render(
            files=files
            )

    def package(
        self,
        autorows,
        basename,
        category,
        homepage,
        description,
        tags,
        latest_asp_basename,
        latest_src_basename,
        asp_list,
        tarball_list
        ):

        return self.templates['package'].render(
            autorows=autorows,
            basename=basename,
            category=category,
            homepage=homepage,
            description=description,
            tags=tags,
            latest_asp_basename=latest_asp_basename,
            latest_src_basename=latest_src_basename,
            asp_list=asp_list,
            tarball_list=tarball_list
            )




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


#def package_file_list(index_db, name):
#
#    files = org.wayround.aipsetup.pkgindex.get_package_files(name, index_db=index_db)
#
#    files.sort(
#        reverse=True,
#        key=functools.cmp_to_key(
#            org.wayround.utils.version.package_version_comparator
#            )
#        )
#
##    org.wayround.utils.list.list_sort(
##        files, cmp=org.wayround.utils.version.package_version_comparator
##        )
##
##    files.reverse()
#
#    rows = []
#
#    for i in files:
#
#        parsed = org.wayround.aipsetup.name.package_name_parse(
#            i, mute=True
#            )
#
#        package_url = (
#            'files_repository'
#            + i
#            )
#
#        package_filename = org.wayround.utils.path.abspath(
#            org.wayround.aipsetup.config.config['repository']
#            + i
#            )
#
#        try:
#            package_file_stat = os.stat(package_filename)
#        except:
#            package_filesize = 0
#            package_moddate = 0
#        else:
#            package_filesize = package_file_stat.st_size
#            t = time.gmtime(package_file_stat.st_mtime)
#            package_moddate = "{Y:04}-{M:02}-{D:02} {h:02}:{m:02}:{s:02}".format(
#                Y=t.tm_year,
#                M=t.tm_mon,
#                D=t.tm_mday,
#                h=t.tm_hour,
#                m=t.tm_min,
#                s=t.tm_sec
#                )
#
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'a',
#                                attributes={
#                                    'href': package_url,
#                                    'title': "Download File"
#                                    },
#                                content=[
#                                    org.wayround.utils.xml.tag(
#                                        'img',
#                                        closed=True,
#                                        attributes={
#                                            'alt': 'download',
#                                            'src': 'css/icons/icons/document-save.png',
#                                            },
#                                        ),
#                                    ' ',
#                                    parsed['groups']['version']
#                                    ]
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=parsed['groups']['timestamp']
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content="{m:.2f} MiB".format(
#                            m=float(package_filesize) / 1024 / 1024
#                            )
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content="{}".format(package_moddate)
#                        )
#                    ]
#                )
#            )
#
#    if len(rows) == 0:
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content="no packages found"
#                        )
#                    ]
#                )
#            )
#    else:
#        rows.insert(
#            0,
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="Version"
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="Timestamp"
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="Size"
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="Modify"
#                        )
#                    ]
#                )
#            )
#
#    table = org.wayround.utils.xml.tag(
#        'table',
#        module='package-info-module',
#        uid='file-list-table',
#        required_css=['file-list-table.css'],
#        content=rows
#        )
#
#    return table


#def package_sources_file_list(info_db, name):
#
#    files = org.wayround.aipsetup.pkgindex.get_package_source_files(name, info_db=info_db)
#
#    # TODO: rework this
#    if not isinstance(files, list):
#        files = []
#
#    files.sort(
#        reverse=True,
#        key=functools.cmp_to_key(
#            org.wayround.utils.version.source_version_comparator
#            )
#        )
#
##    org.wayround.utils.list.list_sort(
##        files,
##        cmp=org.wayround.utils.version.source_version_comparator
##        )
##
##    files.reverse()
#
#    rows = []
#
#    for i in files:
#
#        source_url = 'files_source' + i
#
#        source_filename = org.wayround.utils.path.abspath(
#            org.wayround.aipsetup.config.config['source']
#            + i
#            )
#
#        try:
#            source_file_stat = os.stat(source_filename)
#        except:
#            source_filesize = 0
#            source_moddate = 0
#        else:
#            source_filesize = source_file_stat.st_size
#            t = time.gmtime(source_file_stat.st_mtime)
#            source_moddate = "{Y:04}-{M:02}-{D:02} {h:02}:{m:02}:{s:02}".format(
#                Y=t.tm_year,
#                M=t.tm_mon,
#                D=t.tm_mday,
#                h=t.tm_hour,
#                m=t.tm_min,
#                s=t.tm_sec
#                )
#
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'a',
#                                attributes={
#                                    'href': source_url,
#                                    'title': "Download File"
#                                    },
#                                content=[
#                                    org.wayround.utils.xml.tag(
#                                        'img',
#                                        closed=True,
#                                        attributes={
#                                            'alt': 'download',
#                                            'src': 'css/icons/icons/document-save.png',
#                                            },
#                                        ),
#                                    ' ',
#                                    os.path.basename(i)
#                                    ]
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=os.path.dirname(i)[1:]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content="{m:.2f} MiB".format(
#                            m=float(source_filesize) / 1024 / 1024
#                            )
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=str(source_moddate)
#                        )
#                    ]
#                )
#            )
#
#    if len(rows) == 0:
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content="no sources found"
#                        )
#                    ]
#                )
#            )
#    else:
#        rows.insert(
#            0,
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="File Name"
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="Path"
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="Size"
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'th',
#                        content="Modify"
#                        )
#                    ]
#                )
#            )
#
#    table = org.wayround.utils.xml.tag(
#        'table',
#        module='package-info-module',
#        uid='file-list-table',
#        required_css=['file-list-table.css'],
#        content=rows
#        )
#
#    return table


#def package_info(index_db, info_db, latest_db, tag_db, name):
#
#    pkg_info = org.wayround.aipsetup.pkginfo.get_package_info_record(name, info_db=info_db)
#    logging.debug(
#        "package_info: package_info_record_to_dict({}) == {}".format(
#            name,
#            pkg_info
#            )
#        )
#
#    tags = tag_db.get_tags(name)
#
#    ret = None
#
#    if pkg_info == None:
#        raise cherrypy.HTTPError(404, "No page for package `{}'".format(name))
#    else:
#
#        cid = org.wayround.aipsetup.pkgindex.get_package_category_by_name(name, index_db=index_db)
#        if cid != None:
#            category = org.wayround.aipsetup.pkgindex.get_category_path_string(cid, index_db=index_db)
#        else:
#            category = "< Package not indexed! >"
#
#        rows = []
#
#        keys = set(org.wayround.aipsetup.info.SAMPLE_PACKAGE_INFO_STRUCTURE.keys())
#
#        for i in [
#            'tags', 'name', 'description', 'basename', 'home_page',
#            'newest_src', 'newest_pkg'
#            ]:
#            if i in keys:
#                keys.remove(i)
#
#
#        for i in keys:
#            rows.append(
#                org.wayround.utils.xml.tag(
#                    'tr',
#                    content=[
#                        org.wayround.utils.xml.tag(
#                            'td',
#                            attributes={
#                                'align': 'right'
#                                },
#                            content=[
#                                org.wayround.utils.xml.tag(
#                                    'strong',
#                                    content='{}:'.format(i.replace('_', ' ').capitalize())
#                                    )
#                                ]
#                            ),
#                        org.wayround.utils.xml.tag(
#                            'td',
#                            content=[
#                                org.wayround.utils.xml.tag(
#                                    'pre',
#                                    new_line_before_content=False,
#                                    new_line_after_content=False,
#                                    content=str(pkg_info[i])
#                                    )
#                                ]
#                            )
#                        ]
#                    )
#                )
#
#        rows.insert(
#            0,
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        attributes={
#                            'align': 'right'
#                            },
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'strong',
#                                content='Base Name:'
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'pre',
#                                new_line_before_content=False,
#                                new_line_after_content=False,
#                                content=pkg_info['basename']
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        attributes={
#                            'rowspan': '13'
#                            },
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'pre',
#                                new_line_before_content=False,
#                                new_line_after_content=False,
#                                content=pkg_info['description']
#                                )
#                            ]
#                        )
#                    ]
#                ),
#            )
#
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        attributes={
#                            'align': 'right'
#                            },
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'strong',
#                                content='Category:'
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'pre',
#                                new_line_before_content=False,
#                                new_line_after_content=False,
#                                content=[
#                                    org.wayround.utils.xml.tag(
#                                        'a',
#                                        new_line_before_start=False,
#                                        new_line_after_end=False,
#                                        attributes={
#                                            'href': "category?path={}".format(category)
#                                            },
#                                        content=category
#                                        )
#                                    ]
#                                )
#                            ]
#                        )
#                    ]
#                )
#            )
#
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        attributes={
#                            'align': 'right'
#                            },
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'strong',
#                                content='Home Page:'
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'pre',
#                                new_line_before_content=False,
#                                new_line_after_content=False,
#                                content=[
#                                    org.wayround.utils.xml.tag(
#                                        'a',
#                                        new_line_before_start=False,
#                                        new_line_after_end=False,
#                                        attributes={
#                                            'href': pkg_info['home_page'],
#                                            'target': '_blank'
#                                            },
#                                        content=pkg_info['home_page']
#                                        )
#                                    ]
#                                )
#                            ]
#                        )
#                    ]
#                )
#            )
#
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        attributes={
#                            'align': 'right'
#                            },
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'strong',
#                                content='Tags:'
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'pre',
#                                new_line_before_content=False,
#                                new_line_after_content=False,
#                                content=', '.join(tags)
#                                )
#                            ]
#                        )
#                    ]
#                )
#            )
#
#        a = org.wayround.aipsetup.pkglatest.get_latest_pkg_from_record(name, latest_db=latest_db, info_db=info_db, index_db=index_db)
#        if a == None:
#            a = 'None'
#        else:
#            a = os.path.basename(a)
#
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        attributes={
#                            'align': 'right'
#                            },
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'strong',
#                                content='Latest Package:'
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'pre',
#                                new_line_before_content=False,
#                                new_line_after_content=False,
#                                content=a
#                                )
#                            ]
#                        )
#                    ]
#                )
#            )
#
#        a = org.wayround.aipsetup.pkglatest.get_latest_src_from_record(name, latest_db=latest_db, info_db=info_db, index_db=index_db)
#        if a == None:
#            a = 'None'
#        else:
#            a = os.path.basename(a)
#
#        rows.append(
#            org.wayround.utils.xml.tag(
#                'tr',
#                content=[
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        attributes={
#                            'align': 'right'
#                            },
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'strong',
#                                content='Newest src:'
#                                )
#                            ]
#                        ),
#                    org.wayround.utils.xml.tag(
#                        'td',
#                        content=[
#                            org.wayround.utils.xml.tag(
#                                'pre',
#                                new_line_before_content=False,
#                                new_line_after_content=False,
#                                content=a
#                                )
#                            ]
#                        )
#                    ]
#                )
#            )
#
#        ret = org.wayround.utils.xml.tag(
#            'div',
#            module='package-info-module',
#            uid='info-div',
#            required_css=['info-div.css'],
#            content=[
#                 org.wayround.utils.xml.tag(
#                    'table',
#                    module='package-info-module',
#                    uid='info-info-table',
#                    required_css=['info-info-table.css'],
#                    content=rows
#                    )
#                ]
#            )
#
#    return ret


def page_package(index_db, info_db, latest_db, tag_db, name):

    cid = org.wayround.aipsetup.pkgindex.get_package_category_by_name(name, index_db=index_db)
    if cid != None:
        category = org.wayround.aipsetup.pkgindex.get_category_path_string(cid, index_db=index_db)
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
                            package_info(index_db, info_db, latest_db, tag_db, name)
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
                            package_file_list(index_db, name)
                            ]
                        ),
                    org.wayround.utils.xml.tag(
                        'td',
                        attributes={
                            'valign':'top'
                            },
                        content=[
                            package_sources_file_list(info_db, name)
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


