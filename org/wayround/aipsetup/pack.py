
"""
Set of commands to perform package creation sequence

This module creates checksums, removes garbage, packs file and all
other preparations and actions needed to build final package
"""

import os.path
import pprint
import logging
import subprocess

import org.wayround.aipsetup.buildingsite

import org.wayround.utils.time
import org.wayround.utils.checksum
import org.wayround.utils.archive
import org.wayround.utils.deps_c
import org.wayround.utils.path


# NOTE: this list is suspiciously similar to what in complete
# function, but actually they must be separate

FUNCTIONS_LIST = [
    'destdir_verify_paths_correctness',
    'destdir_set_modes',
    'destdir_checksum',
    'destdir_filelist',
    'destdir_deps_c',
#    'remove_source_and_build_dirs',
    'compress_patches_destdir_and_logs',
    'compress_files_in_lists_dir',
#    'remove_patches_destdir_buildlogs_and_temp_dirs',
#    'remove_decompressed_files_from_lists_dir',
    'make_checksums_for_building_site',
    'pack_buildingsite'
    ]

FUNCTIONS_SET = frozenset(FUNCTIONS_LIST)

def help_texts(name):

    ret = None

    if name == 'destdir_verify_paths_correctness':
        ret = """
Ensure new package creates with bin, sbin, lib and lib64 symlinked into
usr
"""
    elif name == 'destdir_set_modes':
        ret = """
Ensure files and dirs have correct modes
"""

    elif name == 'destdir_checksum':
        ret = """
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
Removes source dir and build dir (one of cleanups
stages)
"""

    elif name == 'compress_patches_destdir_and_logs':
        ret = """\
Compress patches, distribution and logs.
"""

    elif name == 'compress_files_in_lists_dir':
        ret = """\
Compress files found in lists dir
"""

    elif name == 'remove_patches_destdir_buildlogs_and_temp_dirs':
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

def cli_name():
    return 'pk'

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

def destdir_verify_paths_correctness(buildingsite):

    # TODO: Maybe this function need to be rewriten to be more
    #       flexible

    ret = 0

    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

    # TODO: change constants to constitution values instances
    for i in [
        'bin',
        'lib',
        'sbin',
        'lib64',
        'mnt'
        ]:

        p1 = destdir + os.path.sep + i

        if os.path.islink(p1) or os.path.exists(p1):
            logging.error(
                "Forbidden path: {}".format(
                    org.wayround.utils.path.relpath(p1, buildingsite)
                    )
                )
            ret = 1

    # if ret == 0:
    #     for i in [
    #         'bin',
    #         'lib',
    #         'sbin',
    #         'lib64'
    #         ]:

    #         p1 = destdir + os.path.sep + i

    #         os.symlink('usr'+os.path.sep+i, p1)

    return ret

def destdir_set_modes(buildingsite):

    buildingsite = org.wayround.utils.path.abspath(buildingsite)

    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)
    ret = 0

    try:
        for dirpath, dirnames, filenames in os.walk(destdir):
            filenames.sort()
            dirnames.sort()
            dirpath = org.wayround.utils.path.abspath(dirpath)

            for i in dirnames:
                f = os.path.join(dirpath, i)
                if not os.path.islink(f):
                    os.chmod(f, mode=0o755)

            for i in filenames:
                f = os.path.join(dirpath, i)
                if not os.path.islink(f):
                    os.chmod(f, mode=0o755)

    except:
        logging.exception("Modes change exception")
        ret = 1

    return ret


def destdir_checksum(buildingsite):

    ret = 0

    logging.info("Creating checksums")

    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    output_file = org.wayround.utils.path.abspath(
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

    logging.info("Creating file lists")

    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    output_file = org.wayround.utils.path.abspath(
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
        lst = org.wayround.utils.file.files_recurcive_list(destdir)

        lst2 = []
        for i in lst:
            lst2.append('/' + org.wayround.utils.path.relpath(i, destdir))

        lst = lst2

        del lst2

        lst.sort()

        try:
            f = open(output_file, 'w')
        except:
            logging.exception("Can't rewrite file {}".format(output_file))
            ret = 3
        else:

            f.write('\n'.join(lst) + '\n')
            f.close()

    return ret

def destdir_deps_c(buildingsite):
    ret = 0
    logging.info("Generating C deps lists")

    destdir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    lists_file = org.wayround.utils.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.lst'
            )
        )

    deps_file = org.wayround.utils.path.abspath(
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
            file_list_i = 0
            file_list_l = len(file_list)
            for i in file_list:
                filename = destdir + os.path.sep + i
                filename.replace(os.path.sep * 2, os.path.sep)
                filename = org.wayround.utils.path.abspath(filename)

                if os.path.isfile(filename) and os.path.exists(filename):

                    dep = org.wayround.utils.deps_c.elf_deps(filename)

                    if isinstance(dep, list):
                        elfs += 1
                        deps[i] = dep
                    else:
                        n_elfs += 1
                else:
                    n_elfs += 1

                file_list_i += 1

                org.wayround.utils.file.progress_write(
                    "    ({perc:6.2f}%) ELFs: {elfs}; non-ELFs: {n_elfs}".format_map(
                        {
                            'perc': 100.0 / (float(file_list_l) / float(file_list_i)),
                            'elfs': elfs,
                            'n_elfs': n_elfs
                            }
                        )
                    )

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

    logging.info(
        "Removing {} and {}".format(
            org.wayround.aipsetup.buildingsite.DIR_SOURCE,
            org.wayround.aipsetup.buildingsite.DIR_BUILDING
            )
        )

    for i in [
        org.wayround.aipsetup.buildingsite.DIR_SOURCE,
        org.wayround.aipsetup.buildingsite.DIR_BUILDING
        ]:
        dirname = org.wayround.utils.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        if os.path.isdir(dirname):
            org.wayround.utils.file.remove_if_exists(dirname)
        else:
            logging.warning("Dir not exists: {}".format(dirname))

    return ret

def compress_patches_destdir_and_logs(buildingsite):

    ret = 0

    logging.info(
        "Compressing {}, {} and {}".format(
            org.wayround.aipsetup.buildingsite.DIR_PATCHES,
            org.wayround.aipsetup.buildingsite.DIR_DESTDIR,
            org.wayround.aipsetup.buildingsite.DIR_BUILD_LOGS
            )
        )

    for i in [
        org.wayround.aipsetup.buildingsite.DIR_PATCHES,
        org.wayround.aipsetup.buildingsite.DIR_DESTDIR,
        org.wayround.aipsetup.buildingsite.DIR_BUILD_LOGS
        ]:
        dirname = org.wayround.utils.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        filename = "{}.tar.xz".format(dirname)

        if not os.path.isdir(dirname):
            logging.warning("Dir not exists: {}".format(dirname))
            ret = 1
            break
        else:
            size = org.wayround.utils.file.get_file_size(dirname)
            logging.info(
                "Compressing {} (size: {} B ~= {:4.2f} MiB)".format(
                    i,
                    size,
                    float(size) / 1024 / 1024
                    )
                )

            org.wayround.utils.archive.archive_tar_canonical(
                dirname,
                filename,
                'xz',
                verbose_tar=False,
                verbose_compressor=True
                )

    return ret

def compress_files_in_lists_dir(buildingsite):

    ret = 0

    logging.info("Compressing files in lists dir")

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

def remove_patches_destdir_buildlogs_and_temp_dirs(buildingsite):

    ret = 0

    logging.info(
        "Removing {}, {}, {} and {}".format(
            org.wayround.aipsetup.buildingsite.DIR_PATCHES,
            org.wayround.aipsetup.buildingsite.DIR_DESTDIR,
            org.wayround.aipsetup.buildingsite.DIR_BUILD_LOGS,
            org.wayround.aipsetup.buildingsite.DIR_TEMP
            )
        )

    for i in [
        org.wayround.aipsetup.buildingsite.DIR_PATCHES,
        org.wayround.aipsetup.buildingsite.DIR_DESTDIR,
        org.wayround.aipsetup.buildingsite.DIR_BUILD_LOGS,
        org.wayround.aipsetup.buildingsite.DIR_TEMP
        ]:
        dirname = org.wayround.utils.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        if os.path.isdir(dirname):
            org.wayround.utils.file.remove_if_exists(dirname)
        else:
            logging.warning("Dir not exists: {}".format(dirname))

    return ret

def remove_decompressed_files_from_lists_dir(buildingsite):

    ret = 0

    logging.info("Removing garbage from lists dir")

    lists_dir = org.wayround.aipsetup.buildingsite.getDIR_LISTS(buildingsite)

    for i in ['DESTDIR.lst', 'DESTDIR.sha512', 'DESTDIR.dep_c']:

        filename = os.path.join(lists_dir, i)

        if os.path.exists(filename):
            try:
                os.unlink(filename)
            except:
                logging.exception("Can't remove file `{}'".format(filename))
                ret = 1

    return ret

def make_checksums_for_building_site(buildingsite):

    ret = 0

    logging.info("Making checksums for buildingsite files")

    buildingsite = org.wayround.utils.path.abspath(buildingsite)

    package_checksums = os.path.join(
        buildingsite,
        'package.sha512'
        )

    list_to_checksum = get_list_of_items_to_pack(
            buildingsite
            )

    if package_checksums in list_to_checksum:
        list_to_checksum.remove(package_checksums)

    for i in list_to_checksum:
        if os.path.islink(i) or not os.path.isfile(i):
            logging.error(
                "Not exists or not a normal file: {}".format(
                    org.wayround.utils.path.relpath(i, buildingsite)
                    )
                )
            ret = 10

    if ret == 0:

        check_summs = org.wayround.utils.checksum.checksums_by_list(
            list_to_checksum, method='sha512'
            )

        check_summs2 = {}
        paths = list(check_summs.keys())

        for i in paths:
            check_summs2['/' + org.wayround.utils.path.relpath(i, buildingsite)] = check_summs[i]

        check_summs = check_summs2

        del check_summs2

        f = open(package_checksums, 'w')
        f.write(
            org.wayround.utils.checksum.render_checksum_dict_to_txt(
                check_summs,
                sort=True
                )
            )
        f.close()

    return ret


def pack_buildingsite(buildingsite):

    ret = 0

    buildingsite = org.wayround.utils.path.abspath(buildingsite)

    logging.info("Creating package")

    package_info = org.wayround.aipsetup.buildingsite.read_package_info(
        buildingsite, ret_on_error=None
        )

    if package_info == None:
        logging.error("error getting information about package")
        ret = 1
    else:

        pack_dir = org.wayround.utils.path.abspath(
            os.path.join(
                buildingsite,
                '..',
                'pack'
                )
            )

        pack_file_name = os.path.join(
            pack_dir,
            "({pkgname})-({version})-({status})-({timestamp})-({hostinfo}).asp".format_map(
                {
                    'pkgname': package_info['pkg_info']['name'],
                    'version': package_info['pkg_nameinfo']['groups']['version'],
                    'status': package_info['pkg_nameinfo']['groups']['status'],
                    'timestamp': org.wayround.utils.time.currenttime_stamp(),
                    'hostinfo': package_info['constitution']['host'],
                    }
                )
            )

        logging.info("Package will be saved as: {}".format(pack_file_name))

        if not os.path.isdir(pack_dir):
            os.makedirs(pack_dir)

        list_to_tar = get_list_of_items_to_pack(
                buildingsite
                )

        list_to_tar2 = []

        for i in list_to_tar:
            list_to_tar2.append('./' + org.wayround.utils.path.relpath(i, buildingsite))

        list_to_tar = list_to_tar2

        del list_to_tar2

        list_to_tar.sort()

        try:
            ret = subprocess.Popen(
                ['tar', '-vcf', pack_file_name] + list_to_tar,
                cwd=buildingsite
                ).wait()
        except:
            logging.exception("Error tarring package")
            ret = 30
        else:
            logging.info("ASP package creation complete")
            ret = 0

        # else:

        #     ret = org.wayround.aipsetup.package.put_file_to_index(
        #         pack_file_name
        #         )

    return ret

def complete(dirname):

    ret = 0

    for i in [
        'destdir_verify_paths_correctness',
        'destdir_set_modes',
        'destdir_checksum',
        'destdir_filelist',
        'destdir_deps_c',
#        'remove_source_and_build_dirs',
        'compress_patches_destdir_and_logs',
        'compress_files_in_lists_dir',
#        'remove_patches_destdir_buildlogs_and_temp_dirs',
#        'remove_decompressed_files_from_lists_dir',
        'make_checksums_for_building_site',
        'pack_buildingsite'
        ]:

        if eval("{}(dirname)".format(i)) != 0:
            logging.error("Error on {}".format(i))
            ret = 1
            break

    return ret

def get_list_of_items_to_pack(building_site):

    building_site = org.wayround.utils.path.abspath(building_site)

    ret = []

    ret.append(building_site + os.path.sep + DIR_DESTDIR + '.tar.xz')
    ret.append(building_site + os.path.sep + DIR_PATCHES + '.tar.xz')
    ret.append(building_site + os.path.sep + DIR_BUILD_LOGS + '.tar.xz')

    ret.append(building_site + os.path.sep + 'package_info.json')
    ret.append(building_site + os.path.sep + 'package.sha512')

    post_install_script = building_site + os.path.sep + 'post_install.py'
    if os.path.isfile(post_install_script):
        ret.append(post_install_script)

    tarballs = os.listdir(getDIR_TARBALL(building_site))

    for i in tarballs:
        ret.append(building_site + os.path.sep + DIR_TARBALL + os.path.sep + i)


    lists = os.listdir(getDIR_LISTS(building_site))

    for i in lists:
        if i.endswith('.xz'):
            ret.append(building_site + os.path.sep + DIR_LISTS + os.path.sep + i)

    return ret
