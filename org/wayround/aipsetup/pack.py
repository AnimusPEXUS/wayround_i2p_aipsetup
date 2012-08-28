
"""
Set of commands to perform package creation sequence

This module creates checksums, removes garbage, packs file and
all other preparations and actions needed to build final package
"""

import os.path
import tempfile
import shutil
import pprint
import logging
import sys

import org.wayround.aipsetup.buildingsite

import org.wayround.utils.time
import org.wayround.utils.checksum
import org.wayround.utils.archive
import org.wayround.utils.deps_c


FUNCTIONS_LIST = [
    'destdir_checksum',
    'destdir_filelist',
    'destdir_deps_c',
    'remove_source_and_build_dirs',
    'compress_patches_destdir_and_logs',
    'compress_files_in_lists_dir',
    'remove_patches_destdir_and_buildlogs_dirs',
    'remove_decompressed_files_from_lists_dir',
    'make_checksums_for_building_site',
    'pack_buildingsite'
    ]

FUNCTIONS_SET = frozenset(FUNCTIONS_LIST)

def help_texts(name):

    ret = None

    if name == 'destdir_checksum':
        ret = """\
Create checksums of distribution files
"""

    elif name == 'destdir_filelist':
        ret = """\
Create list of distribution files
"""

    elif name == 'destdir_deps_c':
        ret = """\
Create list of ELF dependencies
"""

    elif name == 'remove_source_and_build_dirs':
        ret = """\
Removes source dir and build dir (one of cleanups stages)
"""

    elif name == 'compress_patches_destdir_and_logs':
        ret = """\
Compress patches, distribution and logs.
"""

    elif name == 'compress_files_in_lists_dir':
        ret = """\
Compress files found in lists dir
"""

    elif name == 'remove_patches_destdir_and_buildlogs_dirs':
        ret = """\
Removes patches, destdir and logs (one of cleanups stages)
"""

    elif name == 'remove_decompressed_files_from_lists_dir':
        ret = """\
Remove decompressed files from lists dir (one of cleanups stages)
"""

    elif name == 'make_checksums_for_building_site':
        ret = """\
Make checksums for installers to check package integrity.
"""

    elif name == 'pack_buildingsite':
        ret = """\
Makes final packaging and creates UNICORN software package
"""

    if isinstance(ret, str):
        ret = """\
{text}
    [DIRNAME]

    DIRNAME - set building site. Default is current directory
""".format(text=ret)

    return ret

def exported_commands():

    commands = {}

    for i in FUNCTIONS_SET:
        commands[i] = eval("pack_{}".format(i))

    commands['complete'] = pack_complete

    return commands

def commands_order():
    return ['complete'] + FUNCTIONS_LIST

def _pack_x(opts, args, action):

    if not action in FUNCTIONS_SET:
        raise ValueError("Wrong action parameter")

    ret = 0

    dir_name = '.'
    args_l = len(args)

    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        ret = eval("{}(dir_name)".format(action))

    return ret

for i in FUNCTIONS_SET:
    exec("""\
def pack_{name}(opts, args):
    return _pack_x(opts, args, '{name}')

pack_{name}.__doc__ = help_texts('{name}')
""".format(name=i))

def pack_complete(opts, args):
    """
    Fullcircle action set for creating package

    [DIRNAME]

    DIRNAME - set building site. Default is current directory
    """
    ret = 0

    dir_name = '.'
    args_l = len(args)


    if args_l > 1:
        logging.error("Too many parameters")

    else:
        if args_l == 1:
            dir_name = args[0]

        ret = complete(dir_name)

    return ret


def destdir_checksum(buildingsite):

    ret = 0

    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    output_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.sha512'
            )
        )

    try:
        os.makedirs(lists_dir)
    except:
        pass

    if not os.path.isdir(destdir):
        logging.error("DESTDIR not found")
        ret = 1
    elif not os.path.isdir(lists_dir):
        logging.error("LIST dir can't be used")
        ret = 2
    else:
        org.wayround.utils.checksum.make_dir_checksums(
            destdir,
            output_file
            )

    return ret


def destdir_filelist(buildingsite):

    ret = 0

    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    output_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.lst'
            )
        )

    try:
        os.makedirs(lists_dir)
    except:
        pass

    if not os.path.isdir(destdir):
        logging.error("DESTDIR not found")
        ret = 1
    elif not os.path.isdir(lists_dir):
        logging.error("LIST dir can't be used")
        ret = 2
    else:
        org.wayround.utils.file.list_files_recurcive(
            destdir,
            output_file
            )

    return ret

def destdir_deps_c(buildingsite):
    ret = 0
    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    lists_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.lst'
            )
        )

    deps_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.dep_c'
            )
        )

    try:
        f = open(lists_file, 'r')
    except:
        logging.exception("Can't open file list")
    else:
        try:
            file_list_txt = f.read()
            file_list = file_list_txt.splitlines()
            del(file_list_txt)

            deps = {}
            elfs = 0
            n_elfs = 0
            logging.info("Generating C deps lists")
            file_list_l = len(file_list)
            file_list_i = 1
            for i in file_list:
                file_list_i += 1
                org.wayround.utils.file.progress_write(
                    "    ({perc:6.2f}%) ELFs: {elfs}; non-ELFs: {n_elfs}".format_map(
                        {
                            'perc': 100.0 / (file_list_l / file_list_i),
                            'elfs': elfs,
                            'n_elfs': n_elfs
                            }
                        )
                    )
                filename = destdir + os.path.sep + i
                filename.replace(os.path.sep * 2, os.path.sep)
                filename = os.path.abspath(filename)
                dep = org.wayround.utils.deps_c.elf_deps(filename)
                if isinstance(dep, list):
                    elfs += 1
                    deps[i] = dep
                else:
                    n_elfs += 1

            org.wayround.utils.file.progress_write_finish()

            logging.info("ELFs: {elfs}; non-ELFs: {n_elfs}".format_map({
                'elfs': elfs,
                'n_elfs': n_elfs
                }))

            try:
                f2 = open(deps_file, 'w')
            except:
                logging.exception("Can't create file for dependencies text")
                raise
            else:
                try:
                    f2.write(pprint.pformat(deps))
                finally:
                    f2.close()

        finally:
            f.close()

    return ret

def remove_source_and_build_dirs(buildingsite):

    ret = 0

    for i in [
        org.wayround.aipsetup.buildingsite.DIR_SOURCE,
        org.wayround.aipsetup.buildingsite.DIR_BUILDING
        ]:
        dirname = os.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        if os.path.isdir(dirname):
            org.wayround.utils.file.remove_if_exists(dirname)
        else:
            logging.warning("Dir not exists: %(dirname)s" % {
                'dirname': dirname
                })

    return ret

def compress_patches_destdir_and_logs(buildingsite):

    ret = 0

    for i in [
        org.wayround.aipsetup.buildingsite.DIR_PATCHES,
        org.wayround.aipsetup.buildingsite.DIR_DESTDIR,
        org.wayround.aipsetup.buildingsite.DIR_BUILD_LOGS
        ]:
        dirname = os.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        filename = "%(dirname)s.tar.xz" % {
            'dirname': dirname
            }

        if not os.path.isdir(dirname):
            logging.warning("Dir not exists: %(dirname)s" % {
                'dirname': dirname
                })
            ret = 1
            break
        else:
            logging.info("Compressing %(i)s" % {
                'i': i
                })
            org.wayround.utils.archive.archive_tar_canonical(
                dirname,
                filename,
                'xz',
                verbose_tar=False,
                verbose_compressor=False
                )

    return ret

def compress_files_in_lists_dir(buildingsite):

    ret = 0

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    for i in ['DESTDIR.lst', 'DESTDIR.sha512', 'DESTDIR.dep_c']:

        infile = os.path.join(lists_dir, i)
        outfile = infile + '.xz'

        if org.wayround.utils.exec.process_file(
            'xz',
            infile,
            outfile,
            stderr=None,
            options=['-9', '-v', '-M', (200 * 1024 ** 2)]
            ) != 0:
            logging.error("Error compressing files in lists dir")
            ret = 1
            break

    return ret

def remove_patches_destdir_and_buildlogs_dirs(buildingsite):

    ret = 0

    for i in [
        org.wayround.aipsetup.buildingsite.DIR_PATCHES,
        org.wayround.aipsetup.buildingsite.DIR_DESTDIR,
        org.wayround.aipsetup.buildingsite.DIR_BUILD_LOGS
        ]:
        dirname = os.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        if os.path.isdir(dirname):
            org.wayround.utils.file.remove_if_exists(dirname)
        else:
            logging.warning("Dir not exists: %(dirname)s" % {
                'dirname': dirname
                })

    return ret

def remove_decompressed_files_from_lists_dir(buildingsite):

    ret = 0

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    for i in ['DESTDIR.lst', 'DESTDIR.sha512', 'DESTDIR.dep_c']:

        filename = os.path.join(lists_dir, i)

        if os.path.exists(filename):
            try:
                os.unlink(filename)
            except:
                logging.exception("Can't remove file `%(name)s'" % {
                    'name': filename
                    })
                ret = 1

    return ret

def make_checksums_for_building_site(buildingsite):

    ret = 0

    buildingsite = os.path.abspath(buildingsite)

    package_checksums = os.path.join(
        buildingsite,
        'package.sha512'
        )

    if os.path.exists(package_checksums):
        org.wayround.utils.file.remove_if_exists(package_checksums)

    try:
        tf = tempfile.mkstemp()
    except:
        logging.exception("Error creating temporary file")
        ret = 1
    else:
        f = os.fdopen(tf[0], 'w')

        if org.wayround.utils.checksum.make_dir_checksums_fo(
            buildingsite,
            f) != 0:
            logging.error("Error creating checksums for buildingsite")
            ret = 2

        f.close()
        shutil.move(tf[1], package_checksums)

    return ret


def pack_buildingsite(buildingsite):

    pi = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite, ret_on_error=None
        )

    if pi == None:
        logging.error("error getting information about package")
    else:

        pack_dir = os.path.abspath(
            os.path.join(
                buildingsite,
                '..',
                'pack'
                )
            )

        pack_file_name = os.path.join(
            pack_dir,
            "(%(pkgname)s)-(%(version)s)-%(timestamp)s-%(archinfo)s.asp" % {
                'pkgname': pi['pkg_info']['name'],
                'version': pi['pkg_nameinfo']['groups']['version'],
                'timestamp': org.wayround.utils.time.currenttime_stamp(),
                'archinfo': "%(arch)s-%(type)s-%(kernel)s-%(os)s" % {
                    'arch'  : pi['constitution']['host_arch'],
                    'type'  : pi['constitution']['host_type'],
                    'kernel': pi['constitution']['host_kenl'],
                    'os'    : pi['constitution']['host_name']
                    }
                }
            )

        if not os.path.isdir(pack_dir):
            os.makedirs(pack_dir)

        org.wayround.utils.archive.pack_dir_contents_tar(
            buildingsite,
            pack_file_name
            )

    return 0

def complete(dirname):

    ret = 0

    for i in ['destdir_checksum',
              'destdir_filelist',
              'destdir_deps_c',
              'remove_source_and_build_dirs',
              'compress_patches_destdir_and_logs',
              'compress_files_in_lists_dir',
              'remove_patches_destdir_and_buildlogs_dirs',
              'remove_decompressed_files_from_lists_dir',
              'make_checksums_for_building_site',
              'pack_buildingsite']:
        if eval("%(name)s(dirname)" % {
                'name': i
                }) != 0:
            logging.error("Error on %(name)s" % {
                'name': i
                })
            ret = 1
            break

    return ret
