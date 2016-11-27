
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

import wayround_org.utils.file
import wayround_org.utils.archive
import wayround_org.utils.path

# TODO: error checks

INSTRUCTION = """\

1. Get sources:
    aipsetup pkg-client-src get-lat docbook-sgml3
        will get docbk31.zip
    aipsetup pkg-client-src get-lat docbook-sgml4
        will get docbook-4.5.zip
    aipsetup pkg-client-src get-lat docbook-xml4
        will get docbook-xml-4.5.zip
    aipsetup pkg-client-src get-lat docbook-xsl
        will get docbook-xsl-[some version].tar[.some compressor]

    BIG FAT NOTE: YOU DO NOT NEED ALPHAS, BETAS AND RELISE CANDIDATES!!!
                  DO NOT PLAY WITH VERSIONS SUCH AS:
                  docbook-4.5b or docbook-4.5CR.

                  IF AIPSETUP DOWNLOADS SUCH FILES DO NOT TRUST IT AND
                  DOWNLOAD RIGHT FILES MANUALLY!!

2. Build files (root rights not required for this):
   aipsetup build full -d *

3. Install completed files (root rights required):
   aipsetup sys install *

4. Use command "aipsetup docbook install" as root

At this point docbook must be installed

NOTE: xmlcatalog command from vanilla libxml2-2.9.2.tar.gz has bug,
      which leads to incorrect work with xml catalog, which leads to
      damagede docbook installation

      following patch need to be appyed on libxml2-2.9.2 for xmlcatalog
      to work properly:

sed \
  -e /xmlInitializeCatalog/d \
  -e 's/((ent->checked =.*&&/(((ent->checked == 0) ||\
          ((ent->children == NULL) \&\& (ctxt->options \& XML_PARSE_NOENT))) \&\&/' \
  -i parser.c

    this patch is taken from here:
    http://www.linuxfromscratch.org/blfs/view/stable/general/libxml2.html
"""


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
    return install()


def set_correct_modes(directory):

    for each in os.walk(directory):

        for d in each[1]:
            fd = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(
                    each[0],
                    d))
            # print fd
            os.chmod(fd,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP | stat.S_IXGRP |
                     stat.S_IROTH | stat.S_IXOTH)

        for f in each[2]:
            fd = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(
                    each[0],
                    f))
            # print fd
            os.chmod(fd,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP |
                     stat.S_IROTH)
    return 0


def set_correct_owners(directory):

    for each in os.walk(directory):

        for d in each[1]:
            fd = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(
                    each[0],
                    d))
            # print fd
            os.chown(fd, 0, 0)

        for f in each[2]:
            fd = wayround_org.utils.path.abspath(
                wayround_org.utils.path.join(
                    each[0],
                    f))
            # print fd
            os.chown(fd, 0, 0)

    return 0


def make_directories(base_dir, lst):

    base_dir = wayround_org.utils.path.abspath(base_dir)

    logging.info("Preparing base dir: {}".format(base_dir))

    for i in lst:

        i_ap = wayround_org.utils.path.abspath(i)
        i_ap_fn = wayround_org.utils.path.join(base_dir, i_ap)

        logging.info("    preparing: {}".format(i_ap_fn))
        try:
            os.makedirs(i_ap_fn)
        except:
            pass

        if not os.path.isdir(i_ap_fn):
            logging.error("      not a dir {}".format(i_ap_fn))
            return 1

    return 0


def prepare_sgml_catalog(base_dir_etc_xml_catalog, base_dir_etc_xml_docbook):

    ret = 0

    for i in [base_dir_etc_xml_catalog, base_dir_etc_xml_docbook]:

        logging.info("Checking for catalog {}".format(i))
        if not os.path.isfile(i):
            logging.info("    creating new")
            ret = subprocess.Popen(
                ['xmlcatalog', '--sgml', '--noout', '--create', i]
                ).wait()
        else:
            logging.info("    already exists")

    return ret


def prepare_catalog(base_dir_etc_xml_catalog, base_dir_etc_xml_docbook):

    ret = 0

    for i in [base_dir_etc_xml_catalog, base_dir_etc_xml_docbook]:

        logging.info("Checking for catalog {}".format(i))
        if not os.path.isfile(i):
            logging.info("    creating new")
            ret = subprocess.Popen(
                ['xmlcatalog', '--noout', '--create', i]
                ).wait()
        else:
            logging.info("    already exists")

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

    ret = 0

    target_xsl_dir = wayround_org.utils.path.abspath(target_xsl_dir)
    base_dir = wayround_org.utils.path.abspath(base_dir)
    super_xml_catalog = wayround_org.utils.path.abspath(super_xml_catalog)

    target_xsl_dir_fn = wayround_org.utils.path.join(base_dir, target_xsl_dir)
    target_xsl_dir_fn_no_base = \
        wayround_org.utils.path.remove_base(target_xsl_dir_fn, base_dir)

    super_xml_catalog_fn = \
        wayround_org.utils.path.join(base_dir, super_xml_catalog)

    bn = os.path.basename(target_xsl_dir)

    version = bn.replace('docbook-xsl-', '')
    logging.info("Importing version: {}".format(version))

    ret = subprocess.Popen(
        [
            'xmlcatalog', '--noout', '--add', 'rewriteSystem',
            'http://docbook.sourceforge.net/release/xsl/' + version,
            target_xsl_dir_fn_no_base,
            super_xml_catalog_fn
            ]
        ).wait()

    if ret != 0:
        logging.error(
            "error adding rewriteSystem to {}".format(super_xml_catalog_fn))

    ret = subprocess.Popen(
        [
            'xmlcatalog', '--noout', '--add', 'rewriteURI',
            'http://docbook.sourceforge.net/release/xsl/' + version,
            target_xsl_dir_fn_no_base,
            super_xml_catalog_fn
            ]
        ).wait()

    if ret != 0:
        logging.error(
            "error adding rewriteURI to {}".format(super_xml_catalog_fn))

    if current:
        ret = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', 'rewriteSystem',
                'http://docbook.sourceforge.net/release/xsl/current',
                target_xsl_dir_fn_no_base,
                super_xml_catalog_fn
                ]
            ).wait()
        if ret != 0:
            logging.error(
                "[current] error adding rewriteURI to {}".format(
                    super_xml_catalog_fn
                    )
                )

        ret = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', 'rewriteURI',
                'http://docbook.sourceforge.net/release/xsl/current',
                target_xsl_dir_fn_no_base,
                super_xml_catalog_fn
            ]
            ).wait()
        if ret != 0:
            logging.error(
                "[current] error adding rewriteURI to {}".format(
                    super_xml_catalog_fn
                    )
                )

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

    target_catalog_xml = wayround_org.utils.path.abspath(target_catalog_xml)
    base_dir = wayround_org.utils.path.abspath(base_dir)
    super_docbook_catalog_xml = wayround_org.utils.path.abspath(
        super_docbook_catalog_xml
        )

    target_catalog_xml_fn = wayround_org.utils.path.abspath(
        wayround_org.utils.path.join(base_dir, target_catalog_xml)
        )
    target_catalog_xml_fn_dir = os.path.dirname(target_catalog_xml_fn)

    target_catalog_xml_fn_dir_virtual = target_catalog_xml_fn_dir
    target_catalog_xml_fn_dir_virtual = wayround_org.utils.path.remove_base(
        target_catalog_xml_fn_dir_virtual, base_dir
        )

    super_docbook_catalog_xml_fn = wayround_org.utils.path.join(
        base_dir,
        super_docbook_catalog_xml
        )
    super_docbook_catalog_xml_fn_dir = os.path.dirname(
        super_docbook_catalog_xml_fn
        )

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

                    dst_uri = wayround_org.utils.path.join(
                        '/', target_catalog_xml_fn_dir_virtual, src_uri
                        )

                logging.info("    adding {}".format(i.get(tag + 'Id')))

                cmd = [
                    'xmlcatalog', '--noout', '--add',
                    tag,
                    i.get(tag + 'Id'),
                    'file://{}'.format(dst_uri),
                    super_docbook_catalog_xml_fn,
                    #i.get(tag + 'Id')
                    ]

                p = subprocess.Popen(cmd)

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

    target_dir = wayround_org.utils.path.abspath(target_dir)
    base_dir = wayround_org.utils.path.abspath(base_dir)
    super_catalog_sgml = wayround_org.utils.path.abspath(super_catalog_sgml)
    super_catalog_xml = wayround_org.utils.path.abspath(super_catalog_xml)

    target_dir_fd = wayround_org.utils.path.join(base_dir, target_dir)

    files = os.listdir(target_dir_fd)

    if 'docbook.cat' in files:

        p = subprocess.Popen(
            [
                'xmlcatalog',
                '--sgml',
                '--noout',
                '--add',
                wayround_org.utils.path.join(target_dir, 'docbook.cat'),
                super_catalog_sgml
                ]
            )
        p.wait()

    if 'catalog.xml' in files:

        target_catalog_xml = wayround_org.utils.path.join(
            target_dir,
            'catalog.xml'
            )

        import_catalog_xml_to_super_docbook_catalog(
            target_catalog_xml, base_dir, super_catalog_xml
            )

    return


def make_new_docbook_xml_look_like_old(
        base_dir='/',
        installed_docbook_xml_dir='/usr/share/xml/docbook/docbook-xml-4.5',
        super_catalog_xml='/etc/xml/docbook',
        xml_catalog='/etc/xml/catalog'
        ):

    base_dir = wayround_org.utils.path.abspath(base_dir)
    installed_docbook_xml_dir = \
        wayround_org.utils.path.abspath(installed_docbook_xml_dir)
    super_catalog_xml = wayround_org.utils.path.abspath(super_catalog_xml)
    xml_catalog = wayround_org.utils.path.abspath(xml_catalog)

    super_catalog_xml_fn = wayround_org.utils.path.join(
        base_dir,
        super_catalog_xml
        )

    logging.info("Adding support for older docbook-xml versions")
    logging.info("    ({})".format(super_catalog_xml_fn))

    for i in ['4.1.2', '4.2', '4.3', '4.4']:

        logging.info("    {}".format(i))

        p = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', 'public',
                '-//OASIS//DTD DocBook XML V{}//EN'.format(i),
                "http://www.oasis-open.org/docbook/xml/{}/docbookx.dtd".format(
                    i),
                super_catalog_xml_fn
                ]
            )
        ret = p.wait()
        if ret != 0:
            logging.error(
                "Error adding public {} to {}".format(
                    i,
                    super_catalog_xml_fn))

        p = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', "rewriteSystem",
                "http://www.oasis-open.org/docbook/xml/{}".format(i),
                "file://{}".format(installed_docbook_xml_dir),
                super_catalog_xml_fn
                ]
            )
        ret = p.wait()
        if ret != 0:
            logging.error(
                "Error adding rewriteSystem {} to {}".format(
                    i,
                    super_catalog_xml_fn))

        p = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', "rewriteURI",
                "http://www.oasis-open.org/docbook/xml/{}".format(i),
                "file://{}".format(installed_docbook_xml_dir),
                super_catalog_xml_fn
                ]
            )
        if ret != 0:
            logging.error(
                "Error adding rewriteURI {} to {}".format(
                    i,
                    super_catalog_xml_fn))

        p = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', "delegateSystem",
                "http://www.oasis-open.org/docbook/xml/{}".format(i),
                "file://{}".format(super_catalog_xml),
                super_catalog_xml_fn
                ]
            )
        ret = p.wait()
        if ret != 0:
            logging.error(
                "Error adding delegateSystem {} to {}".format(
                    i,
                    super_catalog_xml_fn))

        p = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', "delegateURI",
                "http://www.oasis-open.org/docbook/xml/{}".format(i),
                "file://{}".format(super_catalog_xml),
                super_catalog_xml_fn
                ]
            )

        ret = p.wait()
        if ret != 0:
            logging.error(
                "Error adding relegateURI {} to {}".format(
                    i,
                    super_catalog_xml_fn))

    return


def make_new_docbook_4_5_look_like_old(
        base_dir='/',
        installed_docbook_sgml_dir='/usr/share/sgml/docbook/docbook-4.5',
        ):

    base_dir = wayround_org.utils.path.abspath(base_dir)

    installed_docbook_xml_dir = \
        wayround_org.utils.path.abspath(
            installed_docbook_sgml_dir
            )

    installed_docbook_xml_dir_fn = \
        wayround_org.utils.path.join(
            base_dir,
            installed_docbook_xml_dir
            )

    catalog_fn = wayround_org.utils.path.join(
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
            'PUBLIC "-//OASIS//DTD DocBook V{}//EN" "docbook.dtd"\n'.format(i)

        if not new_line in lines:
            lines.append(new_line)

    f = open(catalog_fn, 'w')

    f.writelines(lines)

    f.close()

    return


def make_new_docbook_3_1_look_like_old(
        base_dir='/',
        installed_docbook_sgml_dir='/usr/share/sgml/docbook/docbook-3.1',
        ):

    base_dir = wayround_org.utils.path.abspath(base_dir)

    installed_docbook_xml_dir = \
        wayround_org.utils.path.abspath(
            installed_docbook_sgml_dir
            )

    installed_docbook_xml_dir_fn = \
        wayround_org.utils.path.join(
            base_dir,
            installed_docbook_xml_dir
            )

    catalog_fn = wayround_org.utils.path.join(
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
            'PUBLIC "-//Davenport//DTD DocBook V{}//EN" "docbook.dtd"\n'.format(
                i
                )

        if not new_line in lines:
            lines.append(new_line)

    f = open(catalog_fn, 'w')

    f.writelines(lines)

    f.close()

    return


def install(
        base_dir='/',
        super_catalog_sgml='/etc/sgml/sgml-docbook.cat',
        super_catalog_xml='/etc/xml/docbook',
        sys_sgml_dir='/multihost/x86_64-pc-linux-gnu/share/sgml/docbook',
        sys_xml_dir='/multihost/x86_64-pc-linux-gnu/share/xml/docbook',
        xml_catalog='/etc/xml/catalog'
        ):

    ret = 0

    base_dir = wayround_org.utils.path.abspath(base_dir)
    super_catalog_sgml = wayround_org.utils.path.abspath(super_catalog_sgml)
    super_catalog_xml = wayround_org.utils.path.abspath(super_catalog_xml)
    sys_xml_dir = wayround_org.utils.path.abspath(sys_xml_dir)
    xml_catalog = wayround_org.utils.path.abspath(xml_catalog)

    super_catalog_xml_fn = \
        wayround_org.utils.path.join(base_dir, super_catalog_xml)
    sys_sgml_dir_fn = wayround_org.utils.path.join(base_dir, sys_sgml_dir)
    sys_xml_dir_fn = wayround_org.utils.path.join(base_dir, sys_xml_dir)
    xml_catalog_fn = wayround_org.utils.path.join(base_dir, xml_catalog)

    make_directories(
        base_dir,
        [
            os.path.dirname(super_catalog_sgml),
            os.path.dirname(super_catalog_xml),
            sys_xml_dir,
            sys_sgml_dir
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

    logging.info("Checking {}".format(sys_sgml_dir_fn))
    if (len(dirs) != 2
            or not 'docbook-3.1' in dirs
            or not 'docbook-4.5' in dirs):
        logging.error(
            "    docbook-[version] dirs must be exacly:"
            " docbook-3.1 and docbook-4.5"
            )
        ret = 1
    else:
        logging.info("    Ok")

    logging.info("Checking XML in {}".format(sys_xml_dir_fn))
    if len(xml_dirs) != 1:
        logging.error("    Exacly one docbook-xml-[version] dir required")
        ret = 1
    else:
        logging.info("    Ok")

    logging.info("Checking XSL in {}".format(sys_xml_dir_fn))
    if len(xsl_dirs) != 1:
        logging.error("    Exacly one docbook-xsl-[version] dir required")
        ret = 1
    else:
        logging.info("    Ok")

    if ret != 0:
        pass
    else:

        logging.info("Installing docbook")

        for i in dirs:
            logging.info("Installing {}".format(i))

            target_dir = wayround_org.utils.path.join(sys_sgml_dir_fn, i)
            target_dir = wayround_org.utils.path.remove_base(
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

            target_dir = wayround_org.utils.path.join(sys_xml_dir_fn, i)
            target_dir = wayround_org.utils.path.remove_base(
                target_dir,
                base_dir
                )

            import_to_super_docbook_catalog(
                target_dir, base_dir, super_catalog_sgml, super_catalog_xml
                )

            make_new_docbook_xml_look_like_old(
                base_dir, target_dir, super_catalog_xml, xml_catalog
                )

        #raise Exception("breakpoint")

        logging.info("Installing docbook-xsl")

        for i in xsl_dirs:
            logging.info("Installing {}".format(i))

            target_dir = wayround_org.utils.path.join(sys_xml_dir_fn, i)
            target_dir = wayround_org.utils.path.remove_base(
                target_dir,
                base_dir
                )

            # import_to_super_docbook_catalog(
            #    target_dir, base_dir, super_catalog_sgml, super_catalog_xml
            #    )

            import_docbook_xsl_to_catalog(
                target_dir, base_dir, xml_catalog
                )

        import_docbook_to_catalog(xml_catalog_fn)

    return


# some unknown sgml subroutine taken from sgml_common.py builder srcipt


def main1111111111(basedir):

    subprocess.Popen(
        ['install-catalog',
         '--add',
         '/etc/sgml/sgml-ent.cat',
         '/usr/share/sgml/sgml-iso-entities-8879.1986/catalog'
         ]
        ).wait()

    subprocess.Popen(
        ['install-catalog',
         '--add',
         '/etc/sgml/sgml-docbook.cat',
         '/etc/sgml/sgml-ent.cat'
         ]
        ).wait()
