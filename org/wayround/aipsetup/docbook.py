
"""
Install docbook data into current (or selected) system
"""

import os.path
import stat
import re
import logging
import subprocess
import copy

try:
    import lxml.etree
except:
    logging.error("Error importing XML parser. reinstall lxml!")
    raise

import org.wayround.utils.file
import org.wayround.utils.archive
import org.wayround.utils.path


def commands():
    """
    Internally used by aipsetup
    """
    return {
        'docbook': {
            'install': docbook_install
            }
        }


def docbook_install(opts, args):
    install()


def set_correct_modes(directory):

    for each in os.walk(directory):

        for d in each[1]:
            fd = org.wayround.utils.path.abspath(os.path.join(each[0], d))
            # print fd
            os.chmod(fd,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP | stat.S_IXGRP |
                     stat.S_IROTH | stat.S_IXOTH)

        for f in each[2]:
            fd = org.wayround.utils.path.abspath(os.path.join(each[0], f))
            # print fd
            os.chmod(fd,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP |
                     stat.S_IROTH)
    return 0


def set_correct_owners(directory):

    for each in os.walk(directory):

        for d in each[1]:
            fd = org.wayround.utils.path.abspath(os.path.join(each[0], d))
            # print fd
            os.chown(fd, 0, 0)

        for f in each[2]:
            fd = org.wayround.utils.path.abspath(os.path.join(each[0], f))
            # print fd
            os.chown(fd, 0, 0)

    return 0


def make_directories(base_dir, lst):

    base_dir = org.wayround.utils.path.abspath(base_dir)

    logging.info("Preparing base dir: {}".format(base_dir))

    for i in lst:

        i_ap = org.wayround.utils.path.abspath(i)
        i_ap_fn = org.wayround.utils.path.join(base_dir, i_ap)

        logging.info("   checking: {}".format(i_ap_fn))
        try:
            os.makedirs(i_ap_fn)
        except:
            pass

        if not os.path.isdir(i_ap_fn):
            logging.error("      not a dir {}".format(i_ap_fn))
            return 1

    return 0


def prepare_catalog(base_dir_etc_xml_catalog, base_dir_etc_xml_docbook):

    ret = 0

    for i in [base_dir_etc_xml_catalog, base_dir_etc_xml_docbook]:

        logging.info("Checking for catalog {}".format(i))
        if not os.path.isfile(i):
            logging.info("   creating new")
            ret = subprocess.Popen(
                ['xmlcatalog', '--noout', '--create', i]
                ).wait()
        else:
            logging.info("   already exists")

    return ret


def import_docbook_to_catalog(base_dir_etc_xml_catalog):

    for each in [
        [
            'xmlcatalog', '--noout', '--add', 'delegatePublic',
            '-//OASIS//ENTITIES DocBook XML',
            'file:///etc/xml/docbook'
            ],
        [
            'xmlcatalog', '--noout', '--add', 'delegatePublic',
            '-//OASIS//DTD DocBook XML',
            'file:///etc/xml/docbook'
            ],
        [
            'xmlcatalog', '--noout', '--add', 'delegateSystem',
            'http://www.oasis-open.org/docbook/',
            'file:///etc/xml/docbook'
            ],
        [
            'xmlcatalog', '--noout', '--add', 'delegateURI',
            'http://www.oasis-open.org/docbook/',
            'file:///etc/xml/docbook'
            ]
        ]:

        p = subprocess.Popen(each + [base_dir_etc_xml_catalog])

        if 0 != p.wait():
            logging.error("error doing {}".format(repr(each)))

    return 0


def import_docbook_xsl_to_catalog(
    target_xsl_dir, base_dir='/', current=False,
    super_xml_catalog='/etc/xml/catalog'
    ):

    """
    target_xsl_dir: [/base_dir]/usr/share/xml/docbook/docbook-xsl-1.78.1
    super_xml_catalog: [/base_dir]/etc/xml/catalog
    """

    target_xsl_dir = org.wayround.utils.path.abspath(target_xsl_dir)
    base_dir = org.wayround.utils.path.abspath(base_dir)
    super_xml_catalog = org.wayround.utils.path.abspath(super_xml_catalog)

    target_xsl_dir_fn = org.wayround.utils.path.join(base_dir, target_xsl_dir)
    target_xsl_dir_fn_no_base = \
        org.wayround.utils.path.remove_base(target_xsl_dir_fn, base_dir)

    super_xml_catalog_fn = \
        org.wayround.utils.path.join(base_dir, super_xml_catalog)

    bn = os.path.basename(target_xsl_dir)

    version = bn.replace('docbook-xsl-', '')
    logging.info("Importing version: {}".format(version))

    subprocess.Popen(
        [
            'xmlcatalog', '--noout', '--add', 'rewriteSystem',
            'http://docbook.sourceforge.net/release/xsl/' + version,
            target_xsl_dir_fn_no_base,
            super_xml_catalog_fn
            ]
        ).wait()

    subprocess.Popen(
        [
            'xmlcatalog', '--noout', '--add', 'rewriteURI',
            'http://docbook.sourceforge.net/release/xsl/' + version,
            target_xsl_dir_fn_no_base,
            super_xml_catalog_fn
            ]
        ).wait()

    if current:
        subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', 'rewriteSystem',
                'http://docbook.sourceforge.net/release/xsl/current',
                target_xsl_dir_fn_no_base,
                super_xml_catalog_fn
                ]
            ).wait()

        subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', 'rewriteURI',
                'http://docbook.sourceforge.net/release/xsl/current',
                target_xsl_dir_fn_no_base,
                super_xml_catalog_fn
            ]
            ).wait()

    return


def import_catalog_xml_to_super_docbook_catalog(
    target_catalog_xml,
    base_dir='/',
    super_docbook_catalog_xml='/etc/xml/docbook'
    ):

    """
    target_catalog_xml:
    [/base_dir]/usr/share/xml/docbook/docbook-xml-4.5/catalog.xml

    super_docbook_catalog_xml: [/base_dir]/etc/xml/docbook
    """

    target_catalog_xml = org.wayround.utils.path.abspath(target_catalog_xml)
    base_dir = org.wayround.utils.path.abspath(base_dir)
    super_docbook_catalog_xml = \
        org.wayround.utils.path.abspath(super_docbook_catalog_xml)

    target_catalog_xml_fn = org.wayround.utils.path.abspath(
        org.wayround.utils.path.join(base_dir, target_catalog_xml)
        )
    target_catalog_xml_fn_dir = os.path.dirname(target_catalog_xml_fn)

    target_catalog_xml_fn_dir_virtual = target_catalog_xml_fn_dir
    target_catalog_xml_fn_dir_virtual = org.wayround.utils.path.remove_base(
        target_catalog_xml_fn_dir_virtual, base_dir
        )

    super_docbook_catalog_xml_fn = \
        org.wayround.utils.path.join(base_dir, super_docbook_catalog_xml)
    super_docbook_catalog_xml_fn_dir = \
        os.path.dirname(super_docbook_catalog_xml_fn)

    if not os.path.exists(super_docbook_catalog_xml_fn_dir):
        os.makedirs(super_docbook_catalog_xml_fn_dir)

    tmp_cat_lxml = None

    try:
        tmp_cat_lxml = lxml.etree.parse(target_catalog_xml_fn)
    except:
        logging.exception(
            "Can't parse catalog file {}".format(target_catalog_xml_fn)
            )

    for i in tmp_cat_lxml.getroot():

        if type(i) == lxml.etree._Element:

            qname = lxml.etree.QName(i.tag)

            tag = qname.localname

            src_uri = i.get('uri')

            if src_uri:

                dst_uri = ''

                if (src_uri.startswith('http://')
                    or src_uri.startswith('https://')
                    or src_uri.startswith('file://')):

                    dst_uri = src_uri

                else:

                    dst_uri = org.wayround.utils.path.join(
                        '/', target_catalog_xml_fn_dir_virtual, src_uri
                        )

                logging.info(
                    "    adding {}".format(
                        i.get(tag + 'Id')
                        )
                    )

                p = subprocess.Popen(
                    [
                        'xmlcatalog', '--noout', '--add',
                        tag,
                        i.get(tag + 'Id'),
                        'file://{}'.format(dst_uri),
                        super_docbook_catalog_xml_fn,
                        ]
                    )

                p.wait()

    return


def import_to_super_docbook_catalog(
    target_dir,
    base_dir='/',
    super_catalog_sgml='/etc/sgml/sgml-docbook.cat',
    super_catalog_xml='/etc/xml/docbook'
    ):
    """
    target_dir: [/base_dir]/usr/share/xml/docbook/docbook-xml-4.5

    super_catalog_sgml: [/base_dir]/etc/sgml/sgml-docbook.cat
    super_catalog_xml: [/base_dir]/etc/xml/docbook
    """

    target_dir = org.wayround.utils.path.abspath(target_dir)
    base_dir = org.wayround.utils.path.abspath(base_dir)
    super_catalog_sgml = org.wayround.utils.path.abspath(super_catalog_sgml)
    super_catalog_xml = org.wayround.utils.path.abspath(super_catalog_xml)

    target_dir_fd = org.wayround.utils.path.join(base_dir, target_dir)

    files = os.listdir(target_dir_fd)

    if 'docbook.cat' in files:

        p = subprocess.Popen(
            [
                'xmlcatalog',
                '--sgml',
                '--noout',
                '--add',
                org.wayround.utils.path.join(target_dir, 'docbook.cat'),
                super_catalog_sgml
                ]
            )
        p.wait()

    if 'catalog.xml' in files:

        target_catalog_xml = org.wayround.utils.path.join(
            target_dir,
            'catalog.xml'
            )

        import_catalog_xml_to_super_docbook_catalog(
            target_catalog_xml, base_dir, super_catalog_xml
            )


def make_new_docbook_xml_look_like_old(
    base_dir='/',
    installed_docbook_xml_dir='/usr/share/xml/docbook/docbook-xml-4.5',
    super_catalog_xml='/etc/xml/docbook',
    xml_catalog='/etc/xml/catalog'
    ):

    base_dir = org.wayround.utils.path.abspath(base_dir)
    installed_docbook_xml_dir = \
        org.wayround.utils.path.abspath(installed_docbook_xml_dir)
    super_catalog_xml = org.wayround.utils.path.abspath(super_catalog_xml)
    xml_catalog = org.wayround.utils.path.abspath(xml_catalog)

    super_catalog_xml_fn = org.wayround.utils.path.join(
        base_dir,
        super_catalog_xml
        )

    logging.info("Adding support for older docbook-xml versions")

    for i in ['4.1.2', '4.2', '4.3', '4.4']:

        logging.info("    {}".format(i))

        p = subprocess.Popen(
            [
             'xmlcatalog', '--noout', '--add', 'public',
             '-//OASIS//DTD DocBook XML V{}//EN'.format(i),
             "http://www.oasis-open.org/docbook/xml/{}/docbookx.dtd".format(i),
             super_catalog_xml_fn
             ]
            )
        p.wait()

        p = subprocess.Popen(
            [
             'xmlcatalog', '--noout', '--add', "rewriteSystem",
             "http://www.oasis-open.org/docbook/xml/{}".format(i),
             "file://{}".format(installed_docbook_xml_dir),
             super_catalog_xml_fn
             ]
            )
        p.wait()

        p = subprocess.Popen(
            [
             'xmlcatalog', '--noout', '--add', "rewriteURI",
             "http://www.oasis-open.org/docbook/xml/{}".format(i),
             "file://{}".format(installed_docbook_xml_dir),
             super_catalog_xml_fn
             ]
            )
        p.wait()

        p = subprocess.Popen(
            [
             'xmlcatalog', '--noout', '--add', "delegateSystem",
             "http://www.oasis-open.org/docbook/xml/{}".format(i),
             "file://{}".format(super_catalog_xml),
             super_catalog_xml_fn
             ]
            )
        p.wait()

        p = subprocess.Popen(
            [
             'xmlcatalog', '--noout', '--add', "delegateURI",
             "http://www.oasis-open.org/docbook/xml/{}".format(i),
             "file://{}".format(super_catalog_xml),
             super_catalog_xml_fn
             ]
            )

        p.wait()

    return


def make_new_docbook_4_5_look_like_old(
    base_dir='/',
    installed_docbook_sgml_dir='/usr/share/sgml/docbook/docbook-4.5',
    ):

    base_dir = org.wayround.utils.path.abspath(base_dir)

    installed_docbook_xml_dir = \
        org.wayround.utils.path.abspath(
            installed_docbook_sgml_dir
            )

    installed_docbook_xml_dir_fn = \
        org.wayround.utils.path.join(
            base_dir,
            installed_docbook_xml_dir
            )

    catalog_fn = org.wayround.utils.path.join(
        installed_docbook_xml_dir_fn,
        'docbook.cat'
        )

    f = open(catalog_fn)

    lines = f.read().splitlines()

    f.close()

    logging.info("Adding support for older docbook-4.* versions")

    for i in ['4.4', '4.3', '4.2', '4.1', '4.0']:

        logging.info("    {}".format(i))

        new_line = \
            'PUBLIC "-//OASIS//DTD DocBook V{}//EN" "docbook.dtd"'.format(i)

        if not new_line in lines:
            lines.append(new_line)

    f = open(catalog_fn, 'w')

    f.write('\n'.join(lines))

    f.close()

    return


def make_new_docbook_3_1_look_like_old(
    base_dir='/',
    installed_docbook_sgml_dir='/usr/share/sgml/docbook/docbook-3.1',
    ):

    base_dir = org.wayround.utils.path.abspath(base_dir)

    installed_docbook_xml_dir = \
        org.wayround.utils.path.abspath(
            installed_docbook_sgml_dir
            )

    installed_docbook_xml_dir_fn = \
        org.wayround.utils.path.join(
            base_dir,
            installed_docbook_xml_dir
            )

    catalog_fn = org.wayround.utils.path.join(
        installed_docbook_xml_dir_fn,
        'docbook.cat'
        )

    f = open(catalog_fn)

    lines = f.read().splitlines()

    f.close()

    logging.info("Adding support for older docbook-3.* versions")

    for i in ['3.0']:

        logging.info("    {}".format(i))

        new_line = \
            'PUBLIC "-//Davenport//DTD DocBook V{}//EN" "docbook.dtd"'.format(
                i
                )

        if not new_line in lines:
            lines.append(new_line)

    f = open(catalog_fn, 'w')

    f.write('\n'.join(lines))

    f.close()

    return


def install(
    base_dir='/',
    super_catalog_sgml='/etc/sgml/sgml-docbook.cat',
    super_catalog_xml='/etc/xml/docbook',
    sys_sgml_dir='/usr/share/sgml/docbook',
    sys_xml_dir='/usr/share/xml/docbook',
    xml_catalog='/etc/xml/catalog'
    ):

    ret = 0

    base_dir = org.wayround.utils.path.abspath(base_dir)
    super_catalog_sgml = org.wayround.utils.path.abspath(super_catalog_sgml)
    super_catalog_xml = org.wayround.utils.path.abspath(super_catalog_xml)
    sys_xml_dir = org.wayround.utils.path.abspath(sys_xml_dir)
    xml_catalog = org.wayround.utils.path.abspath(xml_catalog)

    super_catalog_xml_fn = \
        org.wayround.utils.path.join(base_dir, super_catalog_xml)
    sys_sgml_dir_fn = org.wayround.utils.path.join(base_dir, sys_sgml_dir)
    sys_xml_dir_fn = org.wayround.utils.path.join(base_dir, sys_xml_dir)
    xml_catalog_fn = org.wayround.utils.path.join(base_dir, xml_catalog)

    make_directories(
        base_dir,
        [
         '/etc/xml',
         '/usr/share/xml/docbook',
         '/usr/share/sgml/docbook'
         ]
        )
    prepare_catalog(xml_catalog_fn, super_catalog_xml_fn)

    dirs = os.listdir(sys_sgml_dir_fn)
    xml_dirs = os.listdir(sys_xml_dir_fn)
    xsl_dirs = copy.copy(xml_dirs)

    for i in dirs[:]:
        if not re.match(r'docbook-(\d+\.?)+', i):
            dirs.remove(i)

    for i in xml_dirs[:]:
        if not re.match(r'docbook-xml-(\d+\.?)+', i):
            xml_dirs.remove(i)

    for i in xsl_dirs[:]:
        if not re.match(r'docbook-xsl-(\d+\.?)+', i):
            xsl_dirs.remove(i)

    if (len(dirs) != 2
        or not 'docbook-3.1' in dirs
        or not 'docbook-4.5' in dirs):
        logging.error(
            "docbook-[version] dirs must be exacly:"
            " docbook-3.1 and docbook-4.5"
            )
        ret = 1

    if len(xml_dirs) != 1:
        logging.error("Exacly one docbook-xml-[version] dir required")
        ret = 1

    if len(xsl_dirs) != 1:
        logging.error("Exacly one docbook-xsl-[version] dir required")
        ret = 1

    if ret != 0:
        pass
    else:

        logging.info("Installing docbook")

        for i in dirs:
            logging.info("Installing {}".format(i))

            target_dir = org.wayround.utils.path.join(sys_sgml_dir_fn, i)
            target_dir = org.wayround.utils.path.remove_base(
                target_dir,
                base_dir
                )

            import_to_super_docbook_catalog(
                target_dir, base_dir, super_catalog_sgml, super_catalog_xml
                )

            if target_dir.endswith('4.5'):
                make_new_docbook_4_5_look_like_old(base_dir, target_dir)

            if target_dir.endswith('3.1'):
                make_new_docbook_3_1_look_like_old(base_dir, target_dir)

        logging.info("Installing docbook-xml")

        for i in xml_dirs:
            logging.info("Installing {}".format(i))

            target_dir = org.wayround.utils.path.join(sys_xml_dir_fn, i)
            target_dir = org.wayround.utils.path.remove_base(
                target_dir,
                base_dir
                )

            import_to_super_docbook_catalog(
                target_dir, base_dir, super_catalog_sgml, super_catalog_xml
                )

            make_new_docbook_xml_look_like_old(
                base_dir, target_dir, super_catalog_xml, xml_catalog
                )

        logging.info("Installing docbook-xsl")

        for i in xsl_dirs:
            logging.info("Installing {}".format(i))

            target_dir = org.wayround.utils.path.join(sys_xml_dir_fn, i)
            target_dir = org.wayround.utils.path.remove_base(
                target_dir,
                base_dir
                )

    #        import_to_super_docbook_catalog(
    #            target_dir, base_dir, super_catalog_sgml, super_catalog_xml
    #            )

            import_docbook_xsl_to_catalog(
                target_dir, base_dir, xml_catalog
                )

        import_docbook_to_catalog(xml_catalog_fn)

    return
