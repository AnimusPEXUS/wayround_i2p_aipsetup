# -*- coding: utf-8 -*-

import os
import os.path
import sys
import stat
import re

import lxml.etree

import aipsetup.version
import aipsetup.utils.error


def print_help():
    print """\

    install [-b=DIR] FILES

       -b - Change basedir. Default is /

"""

def router(opts, args, config):
    ret = 0

    args_l = len(args)


    if args_l == 0:
        print "-e- command not given"
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
            ret = 0


        elif args[0] == 'install':

            if args_l == 1:
                print '-e- docbook-xml zip or docbook-xsl-*.tar* archive filenames reaquired as arguments'
                ret = 10
            else:

                base_dir = '/'

                for i in opts:
                    if i[0] == '-b':
                        base_dir = i[1]

                install(args[1:], base_dir)

        else:
            print "-e- Wrong command"


        ret = 0

    return ret



def set_correct_modes(directory):

    for each in os.walk(directory):

        for d in each[1]:
            fd = os.path.abspath(os.path.join(each[0], d))
            # print fd
            os.chmod(fd,
                     stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                     stat.S_IRGRP |                stat.S_IXGRP |
                     stat.S_IROTH |                stat.S_IXOTH )

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

    print "-i- Preparing base dir: %(dir)s" % {'dir': base_dir}

    for i in [base_dir_etc_xml, base_dir_share_docbook]:
        print "-i-    checking: %(dir)s" % {'dir': i}
        try:
            os.makedirs(i)
        except:
            pass

        if not os.path.isdir(i):
            print "-e-       not a dir %(i)s" % {
                'i': i
                }
            return 1

    return 0

def unpack_tar(docbook_xsl_tar, dir_name):
    r = os.system("tar -xf '%(docbook_xsl_tar)s' -C '%(dir_name)s'" % {
            'docbook_xsl_tar': docbook_xsl_tar,
            'dir_name': dir_name
            })

    return r


def unpack_zip(docbook_zip, base_dir, base_dir_etc_xml, base_dir_share_docbook):

    if not os.path.isfile(docbook_zip):
        print "-e- Wrong zip file"
        return 10

    if len(docbook_zip) == 0:
        print "-e- Wrong zip file"
        return 20

    if not docbook_zip.endswith('.zip'):
        print '-e- Not a zip file: %(file)s' % {'file': docbook_zip}
        return 30

    docbook_no_zip = ''

    try:
        docbook_no_zip = docbook_zip[:-4]
    except:
        print "-e- Wrong zip file"
        return 40

    version = ''

    try:
        version = docbook_no_zip[docbook_no_zip.rfind('-')+1:]
    except:
        print "-e- Wrong zip file version"
        return 50

    if version == '':
        "-e- Wrong zip file version"
        return 60

    base_dir_share_docbook_dtd = os.path.abspath(os.path.join(base_dir_share_docbook, 'xml-dtd-%(ver)s' % {'ver': version}))

    print "-i- making dtd dir: %(dir)s" % {'dir': base_dir_share_docbook_dtd}

    try:
        os.makedirs(base_dir_share_docbook_dtd)
    except:
        pass

    if not os.path.isdir(base_dir_share_docbook_dtd):
        print "-e-    can not create dtd dir: %(dir)s" % {'dir': base_dir_share_docbook_dtd}
        return 70

    print '-i-    unzipping...'

    e = os.system("7z -o'%(dir)s' x '%(file)s'" % {'file': docbook_zip, 'dir': base_dir_share_docbook_dtd} )

    if e != 0:
        print "-e-    error unzipping %(file)s" % {'file': docbook_zip}
        return 80

    print '-i-    ok'

    return base_dir_share_docbook_dtd



def prepare_catalog(base_dir_etc_xml_catalog):

    r = 0

    print "-i- Checking for catalog %(cat)s" % {'cat': base_dir_etc_xml_catalog}
    if not os.path.isfile(base_dir_etc_xml_catalog):
        print "-i-    creating new"
        r = os.system("xmlcatalog --noout --create '%(cat)s'" % {'cat': base_dir_etc_xml_catalog})
    else:
        print "-i-    already exists"

    return r


def import_dtd_to_docbook(base_dir, base_dir_etc_xml_catalog_docbook, dtd_dir):

    print "-i-    Importing into docbook: %(dir)s" % {'dir': os.path.basename(dtd_dir)}

    specific_cat_file = os.path.join(dtd_dir, 'catalog.xml')


    if not os.path.isfile(specific_cat_file):
        print "-e-    %(file)s not found" % {'file': specific_cat_file}
        return 10

    tmp_cat_lxml = None

    try:
        tmp_cat_lxml = lxml.etree.parse(specific_cat_file)
    except:
        e = sys.exc_info()
        aipsetup.utils.error.print_exception_info(e)

    tmp_cat_lxml_ns = '{%(ns)s}' % {'ns': tmp_cat_lxml.getroot().nsmap[None]}

    for tag in ['public', 'system']:

        for each in tmp_cat_lxml.findall(tmp_cat_lxml_ns + tag):

            if each.tag == tmp_cat_lxml_ns + tag:
                print "-i-       %(tag)s - %(Id)s"  % {'Id': each.get(tag + 'Id'), 'tag': tag}

                src_uri = each.get('uri')
                dst_uri = ''

                if src_uri.startswith('http://') or src_uri.startswith('https://') or src_uri.startswith('file://'):
                    dst_uri = src_uri
                else:
                    t_joined_path = os.path.join(dtd_dir, src_uri)
                    if os.path.isfile(t_joined_path):
                        dst_uri = os.path.normpath('/'+ os.path.relpath(t_joined_path, base_dir))
                    else:
                        dst_uri = src_uri

                r = os.system("xmlcatalog --noout --add '%(tag)s' '%(Id)s' '%(uri)s' '%(catalog)s'"  % {
                        'Id': each.get(tag + 'Id'),
                        'uri': 'file://%(uri)s' % {'uri': dst_uri},
                        'catalog': base_dir_etc_xml_catalog_docbook,
                        'tag': tag
                        })
                if r != 0:
                    print "-e-          error"

    return 0

def import_docbook_to_catalog(base_dir_etc_xml_catalog):

    for each in ["xmlcatalog --noout --add 'delegatePublic' '-//OASIS//ENTITIES DocBook XML' 'file:///etc/xml/docbook' '{0}'",
                 "xmlcatalog --noout --add 'delegatePublic' '-//OASIS//DTD DocBook XML' 'file:///etc/xml/docbook' '{0}'",
                 "xmlcatalog --noout --add 'delegateSystem' 'http://www.oasis-open.org/docbook/' 'file:///etc/xml/docbook' '{0}'",
                 "xmlcatalog --noout --add 'delegateURI' 'http://www.oasis-open.org/docbook/' 'file:///etc/xml/docbook' '{0}'"
                 ]:
        each1 = each.format(base_dir_etc_xml_catalog)

        if 0 != os.system(each1):
            print "-e- error doing %(cmd)s" % {'cmd': each1}

    return 0


def install_docbook_zips(docbook_zip_list,
                         base_dir,
                         base_dir_etc_xml,
                         base_dir_etc_xml_catalog,
                         base_dir_etc_xml_catalog_docbook,
                         base_dir_share_docbook):

    dtd_dirs = []

    for i in docbook_zip_list:

        r = unpack_zip(i, base_dir, base_dir_etc_xml,
                       base_dir_share_docbook)

        if isinstance(r, int):
            print "-w- error processing file %(file)s" % {'file': i}
            continue

        dtd_dirs.append(r)

    dtd_dirs.sort()

    if len(dtd_dirs) == 0:
        print "-e- no DTD directories created. Nothing to do farther..."
        return 10

    print "-i- Installing DTDs:"

    for i in dtd_dirs:
        import_dtd_to_docbook(
            base_dir, base_dir_etc_xml_catalog_docbook, i
            )


    print "-i- Installing docbook into catalog"
    import_docbook_to_catalog(base_dir_etc_xml_catalog)

    return 0



def install_docbook_xsl_zips(docbook_xsl_zip_list,
                             base_dir,
                             base_dir_etc_xml_catalog,
                             base_dir_share_docbook
                             ):

    print "-i- Installing XSLs"

    installed_versions = []

    for docbook_xsl_zip in docbook_xsl_zip_list:

        bn = os.path.basename(docbook_xsl_zip)
        r_res = re.match(r'(docbook-xsl-(\d\.?)*)tar\.(.*)', bn)
        name = r_res.group(1)[:-1]
        version = name[name.rfind('-')+1:]


        base_dir_share_docbook_name = \
            os.path.join(base_dir_share_docbook, name)

        base_dir_share_docbook_xsl_stylesheets = \
            os.path.join(base_dir_share_docbook, 'xsl-stylesheets-%(version)s' % {'version': version})

        print "-i- Installing XSL %(xsl_name)s into %(xsl_dest)s" % {
            'xsl_name': name,
            'xsl_dest': base_dir_share_docbook_xsl_stylesheets}

        print '-i-    preparing dirs'


        if 0 != aipsetup.utils.file.remove_if_exists(
                    base_dir_share_docbook_name
                    ):
            print "-e-       error"
            # return 10
            continue

        if 0 != aipsetup.utils.file.remove_if_exists(
                    base_dir_share_docbook_xsl_stylesheets
                    ):
            print "-e-       error"
            # return 20
            continue

        print "-i- Extracting into %(name)s" % {'name': base_dir_share_docbook_name}

        if 0 != unpack_tar(docbook_xsl_zip, base_dir_share_docbook):
            print "-e-    Extraction error"


        print "-i- extracted"

        print "-i- renaming %(one)s to %(another)s" % {
            'one':     base_dir_share_docbook_name,
            'another': base_dir_share_docbook_xsl_stylesheets}
        try:
            os.rename(base_dir_share_docbook_name,
                      base_dir_share_docbook_xsl_stylesheets)
        except:
            aipsetup.utils.error.print_exception_info(sys.exc_info())
            # return 30
            continue

        print "-i- XSL extraction complited"
        print "-i-"

        installed_versions.append(version)

    installed_versions.sort(version.standard_comparison)

    print "-i- Installed XSL: %(versions)s" % {'versions': ', '.join(installed_versions)}


    iv_l = len(installed_versions)

    if iv_l == 0:
        print "-e- no versions"
        return 40

    current = installed_versions[iv_l-1]

    print "-i- Presuming current XSL: %(version)s" % {'version': current}

    print "-i- Updating XML catalog"

    for i in installed_versions:
        os.system(
            "xmlcatalog --noout --add 'rewriteSystem' 'http://docbook.sourceforge.net/release/xsl/%(version)s' '/usr/share/xml/docbook/xsl-stylesheets-%(version)s' '%(catalog)s'" % {
                'version': i,
                'catalog': base_dir_etc_xml_catalog
                })

        os.system(
            "xmlcatalog --noout --add 'rewriteURI' 'http://docbook.sourceforge.net/release/xsl/%(version)s' '/usr/share/xml/docbook/xsl-stylesheets-%(version)s' '%(catalog)s'" % {
                'version': i,
                'catalog': base_dir_etc_xml_catalog
                })


    os.system(
        "xmlcatalog --noout --add 'rewriteSystem' 'http://docbook.sourceforge.net/release/xsl/current' '/usr/share/xml/docbook/xsl-stylesheets-%(version)s' '%(catalog)s'" % {
            'version': current,
            'catalog': base_dir_etc_xml_catalog
            })

    os.system(
        "xmlcatalog --noout --add 'rewriteURI' 'http://docbook.sourceforge.net/release/xsl/current' '/usr/share/xml/docbook/xsl-stylesheets-%(version)s' '%(catalog)s'" % {
            'version': current,
            'catalog': base_dir_etc_xml_catalog
            })


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
            print "-w- %(i)s is not a correct package" % {'i': i}

    docbook_zip_list.sort()
    docbook_xsl_zip_list.sort()


    print "-i- XMLs: %(xml)s;" % {'xml': ', '.join(docbook_zip_list)}
    print "-i- XSLs: %(xsl)s." % {'xsl': ', '.join(docbook_xsl_zip_list)}

    base_dir = os.path.abspath(base_dir)

    base_dir_etc_xml = os.path.join(base_dir, 'etc', 'xml')

    base_dir_etc_xml_catalog = os.path.join(base_dir_etc_xml, 'catalog')

    base_dir_etc_xml_catalog_docbook = os.path.join(base_dir_etc_xml, 'docbook')

    base_dir_share_docbook = os.path.join(base_dir, 'usr', 'share', 'xml', 'docbook')

    base_dir_share_docbook_xsl_stylesheets = os.path.join(base_dir_share_docbook, 'xsl-stylesheets')



    if 0 != prepare_base(base_dir, base_dir_etc_xml, base_dir_share_docbook):
        print "-e- Error preparing base dir"
        exit(20)


    for i in [base_dir_etc_xml_catalog_docbook, base_dir_etc_xml_catalog]:
        if 0 != prepare_catalog(i):
            print "-e- Error creating catalog"
            exit (25)


    if 0 != install_docbook_zips(docbook_zip_list,
                                 base_dir,
                                 base_dir_etc_xml,
                                 base_dir_etc_xml_catalog,
                                 base_dir_etc_xml_catalog_docbook,
                                 base_dir_share_docbook):
        print "-e- Error installing XML"
        exit(30)


    if 0 != install_docbook_xsl_zips(docbook_xsl_zip_list,
                                     base_dir,
                                     base_dir_etc_xml_catalog,
                                     base_dir_share_docbook):
        print "-e- Error installing XSL"
        exit(40)

    print "-i- Setting correct modes"
    try:
        set_correct_modes(base_dir_etc_xml)
        set_correct_modes(base_dir_share_docbook)
    except:
        aipsetup.utils.error.print_exception_info(sys.exc_info())

    print "-i- Setting correct owners"
    try:
        set_correct_owners(base_dir_etc_xml)
        set_correct_owners(base_dir_share_docbook)
    except:
        aipsetup.utils.error.print_exception_info(sys.exc_info())

    print
    print "-i- All operations complited. Bye!"


    return 0

