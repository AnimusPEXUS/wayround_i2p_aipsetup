
import logging

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

