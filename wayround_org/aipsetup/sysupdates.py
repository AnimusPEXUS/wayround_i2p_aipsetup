
"""
Update system bindings and such
"""

import os
import subprocess
import logging
import wayround_org.utils.checksum


def sysupdates_all_actions(opts, args):
    all_actions()
    return 0


def all_actions():
    ret = 0

    if os.getuid() == 0:

        for i in [
                os.sync,
                ldconfig,
                update_mime_database,
                gdk_pixbuf_query_loaders,
                pango_querymodules,
                glib_compile_schemas,
                gtk_query_immodules_2_0,
                gtk_query_immodules_3_0,
                os.sync
                ]:
            try:
                i()
            except:
                logging.exception("Updates error")
                ret = 1

    return ret


def ldconfig():
    logging.info('ldconfig')
    return subprocess.Popen(['ldconfig']).wait()


def _update_mime_database_check():
    """
    return: 0 - passed, not 0 - not passed
    """
    wayround_org.utils.checksum.make_dir_checksums(
        '/usr/share/mime',
        '/usr/share/mime/sha512sums.tmp',
        rel_to='/',
        exclude=[
            '/usr/share/mime/sha512sums',
            '/usr/share/mime/sha512sums.tmp'
            ]
        )
    summ1 = wayround_org.utils.checksum.make_file_checksum(
        '/usr/share/mime/sha512sums'
        )
    summ2 = wayround_org.utils.checksum.make_file_checksum(
        '/usr/share/mime/sha512sums.tmp'
        )
    os.unlink('/usr/share/mime/sha512sums.tmp')
    ret = int(summ1 != summ2)
    return ret


def _update_mime_database_recalculate():
    p = subprocess.Popen(
        ['update-mime-database', '/usr/share/mime']
        )
    ret = p.wait()

    wayround_org.utils.checksum.make_dir_checksums(
        '/usr/share/mime',
        '/usr/share/mime/sha512sums',
        rel_to='/',
        exclude=[
            '/usr/share/mime/sha512sums',
            '/usr/share/mime/sha512sums.tmp'
            ]
        )
    return ret


def update_mime_database():
    logging.info('update-mime-database')
    ret = 0
    if (not os.path.isfile('/usr/share/mime/sha512sums')
            or _update_mime_database_check() != 0):
        logging.info("    regeneration required. please wait..")
        ret = _update_mime_database_recalculate()
    else:
        logging.info("    regeneration not required")

    return ret


def gdk_pixbuf_query_loaders():
    logging.info('gdk-pixbuf-query-loaders')
    return subprocess.Popen(
        ['gdk-pixbuf-query-loaders', '--update-cache']
        ).wait()


def pango_querymodules():
    if not os.path.exists('/etc/pango'):
        os.mkdir('/etc/pango')
        logging.info('Created /etc/pango')
    logging.info('pango-querymodules')
    f = open('/etc/pango/pango.modules', 'wb')
    r = subprocess.Popen(
        ['pango-querymodules'], stdout=f
        ).wait()
    f.close()
    return r


def glib_compile_schemas():
    logging.info('glib-compile-schemas')
    r = subprocess.Popen(
        ['glib-compile-schemas', '/usr/share/glib-2.0/schemas'],
        ).wait()
    return r


def gtk_query_immodules_2_0():
    logging.info('gtk-query-immodules-2.0')
    f = open('/etc/gtk-2.0/gtk.immodules', 'wb')
    r = subprocess.Popen(
        ['gtk-query-immodules-2.0'],
        stdout=f
        ).wait()
    f.close()
    return r


def gtk_query_immodules_3_0():
    logging.info('gtk-query-immodules-3.0')
    r = subprocess.Popen(
        ['gtk-query-immodules-3.0', '--update-cache']
        ).wait()
    return r
