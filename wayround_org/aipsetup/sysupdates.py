
"""
Update system bindings and such
"""

import subprocess
import logging


def sysupdates_all_actions(opts, args):
    all_actions()
    return 0


def all_actions():
    ret = 0

    try:
        ldconfig()
        update_mime_database()
        gdk_pixbuf_query_loaders()
        pango_querymodules()
        glib_compile_schemas()
        gtk_query_immodules_2_0()
        gtk_query_immodules_3_0()

    except:
        ret = 1

    return ret


def ldconfig():
    logging.info('ldconfig')
    return subprocess.Popen(['ldconfig']).wait()


def update_mime_database():
    logging.info('update-mime-database')
    return subprocess.Popen(
        ['update-mime-database', '/usr/share/mime']
        ).wait()


def gdk_pixbuf_query_loaders():
    logging.info('gdk-pixbuf-query-loaders')
    return subprocess.Popen(
        ['gdk-pixbuf-query-loaders', '--update-cache']
        ).wait()


def pango_querymodules():
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
