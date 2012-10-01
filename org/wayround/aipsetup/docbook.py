
"""
Install docbook data into current (or selected) system
"""

import os.path
import stat
import re
import logging
import subprocess

# FIXME: look for new lxml releases supporting Python 3.3
#import lxml.etree

import org.wayround.utils.file

def cli_name():
    return 'docbook'


def exported_commands():

    return {
        'install': docbook_install_files
        }

def commands_order():
    return ['install']


def docbook_install_files(opts, args):
    """
    Analyze supplied archives and install them if they are correct

    [-b=DIR] [FILE1] [FILE2] .. [FILEn]

    -b - Change basedir. Default is `/'
    """

    if len(args) == 1:
        logging.error(
            "docbook-xml zip or docbook-xsl-*.tar* archive filenames " +
            "reaquired as arguments"
            )
        ret = 10
    else:

        base_dir = '/'

        if '-b' in opts:
            base_dir = opts['-b']

        install(args[1:], base_dir)


    return ret



def set_correct_modes(directory):

    for each in os.walk(directory):

        for d in each[1]:
            fd = os.path.abspath(os.path.join(each[0], d))
            # print fd
            os.chmod(fd,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP | stat.S_IXGRP |
                     stat.S_IROTH | stat.S_IXOTH)

        for f in each[2]:
            fd = os.path.abspath(os.path.join(each[0], f))
            # print fd
            os.chmod(fd,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP |
                     stat.S_IROTH)
    return 0


def set_correct_owners(directory):

    for each in os.walk(directory):

        for d in each[1]:
            fd = os.path.abspath(os.path.join(each[0], d))
            # print fd
            os.chown(fd, 0, 0)

        for f in each[2]:
            fd = os.path.abspath(os.path.join(each[0], f))
            # print fd
            os.chown(fd, 0, 0)

    return 0



def prepare_base(base_dir, base_dir_etc_xml, base_dir_share_docbook):

    logging.info("Preparing base dir: {}".format(base_dir))

    for i in [base_dir_etc_xml, base_dir_share_docbook]:
        logging.info("   checking: {}".format(i))
        try:
            os.makedirs(i)
        except:
            pass

        if not os.path.isdir(i):
            logging.error("      not a dir {}".format(i))
            return 1

    return 0

def unpack_tar(docbook_xsl_tar, dir_name):
    # TODO: use aipsetup.utils
    r = subprocess.Popen(
        [
            'tar', '-xf', docbook_xsl_tar, '-C', dir_name
            ]
        ).wait()

    return r


def unpack_zip(docbook_zip, base_dir, base_dir_etc_xml, base_dir_share_docbook):
    # TODO: use aipsetup.utils

    if not os.path.isfile(docbook_zip):
        logging.error("Wrong zip file")
        return 10

    if len(docbook_zip) == 0:
        logging.error("Wrong zip file")
        return 20

    if not docbook_zip.endswith('.zip'):
        logging.error("Not a zip file: {}".format(docbook_zip))
        return 30

    docbook_no_zip = ''

    try:
        docbook_no_zip = docbook_zip[:-4]
    except:
        logging.error("Wrong zip file")
        return 40

    version = ''

    try:
        version = docbook_no_zip[docbook_no_zip.rfind('-') + 1:]
    except:
        logging.error("Wrong zip file version")
        return 50

    if version == '':
        logging.error("Wrong zip file version")
        return 60

    base_dir_share_docbook_dtd = os.path.abspath(
        os.path.join(
            base_dir_share_docbook,
            'xml-dtd-' + version
            )
        )

    logging.info("making dtd dir: {}".format(base_dir_share_docbook_dtd))

    try:
        os.makedirs(base_dir_share_docbook_dtd)
    except:
        pass

    if not os.path.isdir(base_dir_share_docbook_dtd):
        logging.error(
            "   can not create dtd dir: {}".format(
                base_dir_share_docbook_dtd
                )
            )
        return 70

    logging.info("   unzipping...")

    e = subprocess.Popen(
        [
            '7z', '-o' + base_dir_share_docbook_dtd, 'x', docbook_zip
            ]
        ).wait()

    if e != 0:
        logging.error("   error unzipping {}".format(docbook_zip))
        return 80

    logging.info("   ok")

    return base_dir_share_docbook_dtd



def prepare_catalog(base_dir_etc_xml_catalog):

    r = 0

    logging.info("Checking for catalog {}".format(base_dir_etc_xml_catalog))
    if not os.path.isfile(base_dir_etc_xml_catalog):
        logging.info("   creating new")
        r = subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--create', base_dir_etc_xml_catalog
                ]
            ).wait()
    else:
        logging.info("   already exists")

    return r


def import_dtd_to_docbook(base_dir, base_dir_etc_xml_catalog_docbook, dtd_dir):

    logging.info(
        "   Importing into docbook: {}".format(
            os.path.basename(dtd_dir)
            )
        )

    specific_cat_file = os.path.join(dtd_dir, 'catalog.xml')


    if not os.path.isfile(specific_cat_file):
        logging.error("   {} not found".format(specific_cat_file))
        return 10

    tmp_cat_lxml = None

    try:
        tmp_cat_lxml = lxml.etree.parse(specific_cat_file)
    except:
        logging.exception("Can't parse catalog file")

    tmp_cat_lxml_ns = '{{{}}}'.format(tmp_cat_lxml.getroot().nsmap[None])

    for tag in ['public', 'system']:

        for each in tmp_cat_lxml.findall(tmp_cat_lxml_ns + tag):

            if each.tag == tmp_cat_lxml_ns + tag:
                logging.info(
                    "      {tag} - {Id}".format_map(
                        {
                            'Id': each.get(tag + 'Id'),
                            'tag': tag
                            }
                        )
                    )

                src_uri = each.get('uri')
                dst_uri = ''

                if src_uri.startswith('http://') or src_uri.startswith('https://') or src_uri.startswith('file://'):
                    dst_uri = src_uri
                else:
                    t_joined_path = os.path.join(dtd_dir, src_uri)
                    if os.path.isfile(t_joined_path):
                        dst_uri = os.path.normpath('/' + os.path.relpath(t_joined_path, base_dir))
                    else:
                        dst_uri = src_uri

                r = subprocess.Popen(
                    [
                        'xmlcatalog', '--noout', '--add',
                        tag,
                        each.get(tag + 'Id'),
                        'file://{}'.format(dst_uri),
                        base_dir_etc_xml_catalog_docbook,
                        ]
                    ).wait()
                if r != 0:
                    logging.error("         error")

    return 0

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


def install_docbook_zips(
    docbook_zip_list,
    base_dir,
    base_dir_etc_xml,
    base_dir_etc_xml_catalog,
    base_dir_etc_xml_catalog_docbook,
    base_dir_share_docbook
    ):

    dtd_dirs = []

    for i in docbook_zip_list:

        r = unpack_zip(i, base_dir, base_dir_etc_xml,
                       base_dir_share_docbook)

        if isinstance(r, int):
            logging.warning("error processing file {}".format(i))
            continue

        dtd_dirs.append(r)

    dtd_dirs.sort()

    if len(dtd_dirs) == 0:
        logging.error("no DTD directories created. Nothing to do farther...")
        return 10

    logging.info("Installing DTDs:")

    for i in dtd_dirs:
        import_dtd_to_docbook(
            base_dir, base_dir_etc_xml_catalog_docbook, i
            )


    logging.info("Installing docbook into catalog")
    import_docbook_to_catalog(base_dir_etc_xml_catalog)

    return 0



def install_docbook_xsl_zips(
    docbook_xsl_zip_list,
    base_dir,
    base_dir_etc_xml_catalog,
    base_dir_share_docbook
    ):

    logging.info("Installing XSLs")

    installed_versions = []

    for docbook_xsl_zip in docbook_xsl_zip_list:

        bn = os.path.basename(docbook_xsl_zip)
        r_res = re.match(r'(docbook-xsl-(\d\.?)*)tar\.(.*)', bn)
        name = r_res.group(1)[:-1]
        version = name[name.rfind('-') + 1:]


        base_dir_share_docbook_name = os.path.join(
            base_dir_share_docbook, name
            )

        base_dir_share_docbook_xsl_stylesheets = (
            os.path.join(
                base_dir_share_docbook,
                'xsl-stylesheets-{}'.format(version)
                )
            )

        logging.info(
            "Installing XSL {xsl_name} into {xsl_dest}".format_map(
                {
                    'xsl_name': name,
                    'xsl_dest': base_dir_share_docbook_xsl_stylesheets
                    }
                )
            )

        logging.info("   preparing dirs")


        if 0 != org.wayround.utils.file.remove_if_exists(
                    base_dir_share_docbook_name
                    ):
            logging.error("      error")
            # return 10
            continue

        if 0 != org.wayround.utils.file.remove_if_exists(
                    base_dir_share_docbook_xsl_stylesheets
                    ):
            logging.error("      error")
            # return 20
            continue

        logging.info("Extracting into {}".format(base_dir_share_docbook_name))

        if 0 != unpack_tar(docbook_xsl_zip, base_dir_share_docbook):
            logging.error("   Extraction error")


        logging.info("extracted")

        logging.info(
            "renaming {one} to {another}".format_map(
                {
                    'one':     base_dir_share_docbook_name,
                    'another': base_dir_share_docbook_xsl_stylesheets
                    }
                )
            )
        try:
            os.rename(base_dir_share_docbook_name,
                      base_dir_share_docbook_xsl_stylesheets)
        except:
            logging.exception(
                "Can't rename file `{}' to `{}'".format(
                    base_dir_share_docbook_name,
                    base_dir_share_docbook_xsl_stylesheets
                    )
                )
            # return 30
            continue

        logging.info("XSL extraction complited")

        installed_versions.append(version)

    installed_versions.sort(version.standard_comparison)

    logging.info("Installed XSL: {}".format(', '.join(installed_versions)))


    iv_l = len(installed_versions)

    if iv_l == 0:
        logging.error("no versions")
        return 40

    current = installed_versions[iv_l - 1]

    logging.info("Presuming current XSL: {}".format(current))

    logging.info("Updating XML catalog")

    for i in installed_versions:
        subprocess.Popen(
            [
                'xmlcatalog', '--noout', '--add', 'rewriteSystem',
                'http://docbook.sourceforge.net/release/xsl/' + i,
                '/usr/share/xml/docbook/xsl-stylesheets-' + i,
                base_dir_etc_xml_catalog
                ]
            ).wait()

        subprocess.Popen(
            [
                'xmlcatalog' , '--noout', '--add' , 'rewriteURI',
                'http://docbook.sourceforge.net/release/xsl/' + i,
                '/usr/share/xml/docbook/xsl-stylesheets-' + i,
                 base_dir_etc_xml_catalog
                 ]
            ).wait()


    subprocess.Popen(
        [
            'xmlcatalog', '--noout' , '--add' , 'rewriteSystem',
            'http://docbook.sourceforge.net/release/xsl/current',
            '/usr/share/xml/docbook/xsl-stylesheets-' + current,
            base_dir_etc_xml_catalog
            ]
        ).wait()

    subprocess.Popen(
        [
            'xmlcatalog', '--noout', '--add', 'rewriteURI',
            'http://docbook.sourceforge.net/release/xsl/current',
            '/usr/share/xml/docbook/xsl-stylesheets-' + current,
            base_dir_etc_xml_catalog
        ]
        ).wait()

    return 0

def install(files, base_dir):

    docbook_zip_list = []
    docbook_xsl_zip_list = []

    for i in files:
        if re.match(r'docbook-xml-(\d\.?)*zip', os.path.basename(i)):
            docbook_zip_list.append(i)
        elif re.match(r'docbook-xsl-(\d\.?)*tar\.(.*)', os.path.basename(i)):
            docbook_xsl_zip_list.append(i)
        else:
            print("-w- {} is not a correct package".format(i))

    docbook_zip_list.sort()
    docbook_xsl_zip_list.sort()


    logging.info("XMLs: {};".format(', '.join(docbook_zip_list)))
    logging.info("XSLs: {}.".format(', '.join(docbook_xsl_zip_list)))

    base_dir = os.path.abspath(base_dir)

    base_dir_etc_xml = os.path.join(base_dir, 'etc', 'xml')

    base_dir_etc_xml_catalog = os.path.join(base_dir_etc_xml, 'catalog')

    base_dir_etc_xml_catalog_docbook = os.path.join(base_dir_etc_xml, 'docbook')

    base_dir_share_docbook = os.path.join(base_dir, 'usr', 'share', 'xml', 'docbook')

    # leave next comment line for visibility
    # base_dir_share_docbook_xsl_stylesheets = \
    #     os.path.join(base_dir_share_docbook, 'xsl-stylesheets')



    if 0 != prepare_base(base_dir, base_dir_etc_xml, base_dir_share_docbook):
        logging.error("Error preparing base dir")
        exit(20)


    for i in [base_dir_etc_xml_catalog_docbook, base_dir_etc_xml_catalog]:
        if 0 != prepare_catalog(i):
            logging.error("Error creating catalog")
            exit (25)


    if 0 != install_docbook_zips(docbook_zip_list,
                                 base_dir,
                                 base_dir_etc_xml,
                                 base_dir_etc_xml_catalog,
                                 base_dir_etc_xml_catalog_docbook,
                                 base_dir_share_docbook):
        logging.error("Error installing XML")
        exit(30)


    if 0 != install_docbook_xsl_zips(docbook_xsl_zip_list,
                                     base_dir,
                                     base_dir_etc_xml_catalog,
                                     base_dir_share_docbook):
        logging.error("Error installing XSL")
        exit(40)

    logging.info("Setting correct modes")
    try:
        set_correct_modes(base_dir_etc_xml)
        set_correct_modes(base_dir_share_docbook)
    except:
        logging.exception("Can't set correct file modes")

    logging.info("Setting correct owners")
    try:
        set_correct_owners(base_dir_etc_xml)
        set_correct_owners(base_dir_share_docbook)
    except:
        logging.exception("Can't set correct file owner")

    print()
    logging.info("All operations complited. Bye!")


    return 0

