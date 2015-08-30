
"""
Update system bindings and such
"""

import os.path
import subprocess
import logging
import wayround_org.utils.checksum
import wayround_org.utils.path


def sysupdates_all_actions(opts, args):
    all_actions()
    return 0

def sync():
    logging.info("sync")
    os.sync()
    return 

def all_actions():
    ret = 0

    if os.getuid() == 0:

        for i in [
                sync,
                ldconfig,
                update_mime_database,
                gdk_pixbuf_query_loaders,
                pango_querymodules,
                glib_compile_schemas,
                gtk_query_immodules_2_0,
                gtk_query_immodules_3_0,
                sync
                ]:
            try:
                i()
            except:
                logging.exception("Updates error")
                ret = 1

    return ret


def list_arch_roots(basedir='/'):

    ret = []

    march_dir = wayround_org.utils.path.join(basedir, 'multiarch')

    march_dir_files = os.listdir(march_dir)

    for i in march_dir_files:
        joined = wayround_org.utils.path.join(march_dir, i)

        if os.path.isdir(joined) and not os.path.islink(joined):
            ret.append(joined)

    return sorted(ret)


def ldconfig():
    logging.info('ldconfig')
    return subprocess.Popen(['ldconfig']).wait()


def _update_mime_database_check(path):
    """
    return: 0 - passed, not 0 - not passed
    """
    ret = 0

    errors = 0

    mime_dir = wayround_org.utils.path.join(path, 'share', 'mime')

    try:

        os.makedirs(mime_dir, exist_ok=True)

        mime_dir_sha512sums = wayround_org.utils.path.join(
            mime_dir,
            'sha512sums'
            )

        mime_dir_sha512sums_tmp = mime_dir_sha512sums + '.tmp'

        wayround_org.utils.checksum.make_dir_checksums(
            mime_dir,
            mime_dir_sha512sums_tmp,
            rel_to='/',
            exclude=[
                mime_dir_sha512sums,
                mime_dir_sha512sums_tmp
                ]
            )
        summ1 = wayround_org.utils.checksum.make_file_checksum(
            mime_dir_sha512sums
            )
        summ2 = wayround_org.utils.checksum.make_file_checksum(
            mime_dir_sha512sums_tmp
            )
        os.unlink(mime_dir_sha512sums_tmp)

        errors += int(summ1 != summ2)

    except:
        logging.exception('error')
        errors += 1

    ret = int(errors != 0)

    return ret


def _update_mime_database_recalculate(path):
    p = subprocess.Popen(
        ['{}/bin/update-mime-database'.format(path), '{}/share/mime'.format(path)]
        )
    ret = p.wait()

    wayround_org.utils.checksum.make_dir_checksums(
        '{}/share/mime'.format(path),
        '{}/share/mime/sha512sums'.format(path),
        rel_to='/',
        exclude=[
            '{}/share/mime/sha512sums'.format(path),
            '{}/share/mime/sha512sums.tmp'.format(path)
            ]
        )
    return ret


def update_mime_database():
    logging.info('update-mime-database')

    ret = 0

    roots = list_arch_roots()

    for i in roots:

        if (not os.path.isfile('{}/share/mime/sha512sums'.format(i))
                or _update_mime_database_check(i) != 0):
            logging.info("    regeneration required. please wait..")
            ret = _update_mime_database_recalculate(i)
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
