
"""
Build software before packaging

This module provides functions for building package using building script (see
:mod:`buildscript<org.wayround.aipsetup.buildscript>` module for more info on
building scripts)
"""

import copy
import json
import logging
import os
import pprint
import shutil
import subprocess
import tempfile

import org.wayround.aipsetup.client_pkg
import org.wayround.aipsetup.controllers
import org.wayround.aipsetup.info
import org.wayround.utils.format.elf
import org.wayround.utils.path
import org.wayround.utils.system_type
import org.wayround.utils.tarball
import org.wayround.utils.terminal
import org.wayround.utils.time


DIR_TARBALL = '00.TARBALL'
"""
Directory for storing tarballs used in package building. contents is packed
into resulting package as it is requirements of most good licenses
"""

DIR_SOURCE = '01.SOURCE'
"""
Directory for detarred sources, which used for building package. This is not
packed into final package, as we already have original tarballs.
"""

DIR_PATCHES = '02.PATCHES'
"""
Patches stored here. packed.
"""

DIR_BUILDING = '03.BUILDING'
"""
Here package are build. not packed.
"""

DIR_DESTDIR = '04.DESTDIR'
"""
Primary root of files for package. those will be installed into target system.
"""

DIR_BUILD_LOGS = '05.BUILD_LOGS'
"""
Various building logs are stored here. Packed.
"""

DIR_LISTS = '06.LISTS'
"""
Various lists stored here. Packed.
"""

DIR_TEMP = '07.TEMP'
"""
Temporary directory used by aipsetup while building package. Throwed away.
"""


DIR_ALL = [
    DIR_TARBALL,
    DIR_SOURCE,
    DIR_PATCHES,
    DIR_BUILDING,
    DIR_DESTDIR,
    DIR_BUILD_LOGS,
    DIR_LISTS,
    DIR_TEMP
    ]
'All package directories list in proper order'

DIR_LIST = DIR_ALL
':data:`DIR_ALL` copy'

INVALID_MOVABLE_DESTDIR_ROOT_LINKS = [
    'bin',
    'sbin',
    'lib',
    'lib64'
    ]

INVALID_DESTDIR_ROOT_LINKS = [
    'mnt'
    ] + INVALID_MOVABLE_DESTDIR_ROOT_LINKS


# WARNING: this list is suspiciously similar to what in complete
#          function, but actually they must be separate

PACK_FUNCTIONS_LIST = [
    'destdir_verify_paths_correctness',
    'destdir_set_modes',
    'destdir_checksum',
    'destdir_filelist',
    'destdir_deps_bin',
    'compress_patches_destdir_and_logs',
    'compress_files_in_lists_dir',
    'make_checksums_for_building_site',
    'pack_buildingsite'
    ]
"""
aipsetup CLI related functionality
"""

FUNCTIONS_SET = frozenset(PACK_FUNCTIONS_LIST)
"""
aipsetup CLI related functionality
"""

APPLY_DESCR = """\

    It is typically used in conjunction with functions
    :func:`apply_constitution_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`
    in  this order by function :func:`apply_info`
"""


class Constitution:

    def __init__(
            self,
            host_str='i486-pc-linux-gnu',
            build_str='i486-pc-linux-gnu',
            target_str='i486-pc-linux-gnu'
            ):

        self.host = org.wayround.utils.system_type.SystemType(host_str)
        self.build = org.wayround.utils.system_type.SystemType(build_str)
        self.target = org.wayround.utils.system_type.SystemType(target_str)

        self.paths = {}

    def return_aipsetup3_compliant(self):
        return {
            'host': str(self.host),
            'build': str(self.build),
            'target': str(self.target),
            'paths': copy.copy(self.paths),
            'system_title': 'UNICORN',
            'system_version': '3.0'
            }


class BuildCtl:

    def __init__(
            self,
            buildingsite_ctl
            ):

        if not isinstance(
                buildingsite_ctl,
                BuildingSiteCtl
                ):
            raise TypeError(
                "buildingsite_ctl must be an instance of "
                "org.wayround.aipsetup.build.BuildingSiteCtl"
                )

        self.buildingsite_ctl = buildingsite_ctl
        self.path = org.wayround.utils.path.abspath(buildingsite_ctl.path)

    def complete(self, buildscript_ctl):
        """
        Run all building script commands on selected building site

        See :func:`start_building_script`
        """
        return self.start_building_script(buildscript_ctl, action=None)

    def start_building_script(self, buildscript_ctl, action=None):
        """
        Run selected action on building site using particular building script.

        :param building_site: path to building site directory

        :param action: can be None or concrete name of action in building
            script. if action name ends with + (plus) all remaining actions
            will be also started (if not error will occur)

        :rtype: 0 - if no error occurred
        """

        if not isinstance(buildscript_ctl, BuildScriptCtrl):
            raise ValueError(
                "buildscript_ctl must be of type "
                "org.wayround.aipsetup.build.BuildScriptCtrl"
                )

        building_site = org.wayround.utils.path.abspath(self.path)

        package_info = self.buildingsite_ctl.read_package_info(
            ret_on_error=None
            )

        ret = 0

        if package_info is None:
            logging.error(
                "Error getting information "
                "from building site's(`{}') `package_info.json'".format(
                    building_site
                    )
                )
            ret = 1
        else:

            script = (
                buildscript_ctl.load_buildscript(
                    package_info['pkg_info']['buildscript']
                    )
                )

            if not isinstance(script, dict):
                logging.error("Some error while loading script")
                ret = 2
            else:

                try:
                    ret = script['main'](building_site, action)
                except KeyboardInterrupt:
                    raise
                except:
                    logging.exception(
                        "Error starting `main' function in `{}'".format(
                            package_info['pkg_info']['buildscript']
                            )
                        )
                    ret = 3

                logging.info(
                    "action `{}' ended with code {}".format(action, ret)
                    )

        return ret


class PackCtl:

    def __init__(
            self,
            buildingsite_ctl
            ):

        if not isinstance(
                buildingsite_ctl,
                BuildingSiteCtl
                ):
            raise TypeError(
                "buildingsite_ctl must be an instance of "
                "org.wayround.aipsetup.build.BuildingSiteCtl"
                )

        self.buildingsite_ctl = buildingsite_ctl
        self.path = org.wayround.utils.path.abspath(buildingsite_ctl.path)

    def destdir_verify_paths_correctness(self):
        """
        Check for forbidden files in destdir

        Files ``['bin', 'sbin', 'lib', 'lib64', 'mnt']`` are forbidden to be in
        DESTDIR root. This is a rule for aipsetup based distributions. Except
        is special cases, when this function is avoided.
        """

        ret = 0

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        try:
            os.makedirs(destdir + os.path.sep + 'usr')
        except:
            pass


        for i in INVALID_MOVABLE_DESTDIR_ROOT_LINKS:

            p1 = destdir + os.path.sep + i

            if os.path.islink(p1) or os.path.exists(p1):

                org.wayround.utils.file.copytree(
                    p1,
                    destdir + os.path.sep + 'usr' + os.path.sep + i,
                    dst_must_be_empty=False
                    )
                #shutil.copytree(p1, destdir + os.path.sep + 'usr')
                shutil.rmtree(p1)

        for i in INVALID_DESTDIR_ROOT_LINKS:

            p1 = destdir + os.path.sep + i

            if os.path.islink(p1) or os.path.exists(p1):
                logging.error(
                    "Forbidden path: {}".format(
                        org.wayround.utils.path.relpath(p1, self.path)
                        )
                    )
                ret = 1

        return ret

    def destdir_set_modes(self):
        """
        Ensure all files (and dirs) in DESTDIR have ``0o755`` mode.

        If You interested in defferent modes for files after package
        installation, read about post_install.py (script, which need to be
        placed in package and will be executed after package installation)

        .. TODO: link to info about post_install.py
        """

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        ret = 0

        try:
            for dirpath, dirnames, filenames in os.walk(destdir):
                filenames.sort()
                dirnames.sort()
                dirpath = org.wayround.utils.path.abspath(dirpath)

                for i in dirnames:
                    f = org.wayround.utils.path.join(dirpath, i)
                    if not os.path.islink(f):
                        os.chmod(f, mode=0o755)

                for i in filenames:
                    f = org.wayround.utils.path.join(dirpath, i)
                    if not os.path.islink(f):
                        os.chmod(f, mode=0o755)

        except:
            logging.exception("Modes change exception")
            ret = 1

        return ret

    def destdir_checksum(self):
        """
        Create checksums for DESTDIR contents
        """

        ret = 0

        logging.info("Creating checksums")

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

        output_file = org.wayround.utils.path.abspath(
            org.wayround.utils.path.join(
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
            ret = org.wayround.utils.checksum.make_dir_checksums(
                destdir,
                output_file,
                destdir
                )

        return ret

    def destdir_filelist(self):
        """
        Create file list for DESTDIR contents
        """

        ret = 0

        logging.info("Creating file lists")

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

        output_file = org.wayround.utils.path.abspath(
            os.path.join(
                lists_dir,
                'DESTDIR.lst'
                )
            )

        if not os.path.isdir(destdir):
            try:
                os.makedirs(lists_dir)
            except:
                logging.error("Can't create dir: {}".format(destdir))

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

    def destdir_deps_bin(self):
        """
        Create dependency tree listing for ELFs in DESTDIR
        """

        ret = 0
        logging.info("Generating C deps lists")

        destdir = self.buildingsite_ctl.getDIR_DESTDIR()

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

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
                    filename = org.wayround.utils.path.abspath(
                        org.wayround.utils.path.join(destdir, i)
                        )

                    if os.path.isfile(filename) and os.path.exists(filename):

                        try:
                            elf = org.wayround.utils.format.elf.ELF(filename)
                        except:
                            logging.exception(
                                "Error parsing file: `{}'".format(filename)
                                )
                            n_elfs += 1
                        else:

                            dep = elf.needed_libs_list

                            if isinstance(dep, list):
                                elfs += 1
                                deps[i] = dep
                            else:
                                n_elfs += 1
                    else:
                        n_elfs += 1

                    file_list_i += 1

                    org.wayround.utils.terminal.progress_write(
                        "    ({perc:.2f}%) ELFs: {elfs}; non-ELFs: {n_elfs}".
                        format_map(
                            {
                                'perc':
                                (100 /
                                 (float(file_list_l) / file_list_i)),
                                    'elfs': elfs,
                                    'n_elfs': n_elfs
                                }
                            )
                        )

                org.wayround.utils.terminal.progress_write_finish()

                logging.info("ELFs: {elfs}; non-ELFs: {n_elfs}".format_map({
                    'elfs': elfs,
                    'n_elfs': n_elfs
                    }))

                try:
                    f2 = open(deps_file, 'w')
                except:
                    logging.exception("Can't create file of dependencies list")
                    raise
                else:
                    try:
                        f2.write(pprint.pformat(deps))
                    finally:
                        f2.close()

            finally:
                f.close()

        return ret

    def remove_source_and_build_dirs(self):

        ret = 0

        logging.info(
            "Removing {} and {}".format(
                DIR_SOURCE,
                DIR_BUILDING
                )
            )

        for i in [
                DIR_SOURCE,
                DIR_BUILDING
                ]:
            dirname = org.wayround.utils.path.abspath(
                os.path.join(
                    self.path,
                    i
                    )
                )
            if os.path.isdir(dirname):
                org.wayround.utils.file.remove_if_exists(dirname)
            else:
                logging.warning("Dir not exists: {}".format(dirname))

        return ret

    def compress_patches_destdir_and_logs(self):

        ret = 0

        logging.info(
            "Compressing {}, {} and {}".format(
                DIR_PATCHES,
                DIR_DESTDIR,
                DIR_BUILD_LOGS
                )
            )

        for i in [
                DIR_PATCHES,
                DIR_DESTDIR,
                DIR_BUILD_LOGS
                ]:
            dirname = org.wayround.utils.path.abspath(
                os.path.join(
                    self.path,
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

    def compress_files_in_lists_dir(self):

        ret = 0

        logging.info("Compressing files in lists dir")

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

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

    def remove_patches_destdir_buildlogs_and_temp_dirs(self):

        ret = 0

        logging.info(
            "Removing {}, {}, {} and {}".format(
                DIR_PATCHES,
                DIR_DESTDIR,
                DIR_BUILD_LOGS,
                DIR_TEMP
                )
            )

        for i in [
                DIR_PATCHES,
                DIR_DESTDIR,
                DIR_BUILD_LOGS,
                DIR_TEMP
                ]:
            dirname = org.wayround.utils.path.abspath(
                os.path.join(
                    self.path,
                    i
                    )
                )
            if os.path.isdir(dirname):
                org.wayround.utils.file.remove_if_exists(dirname)
            else:
                logging.warning("Dir not exists: {}".format(dirname))

        return ret

    def remove_decompressed_files_from_lists_dir(self):

        ret = 0

        logging.info("Removing garbage from lists dir")

        lists_dir = self.buildingsite_ctl.getDIR_LISTS()

        for i in ['DESTDIR.lst', 'DESTDIR.sha512', 'DESTDIR.dep_c']:

            filename = os.path.join(lists_dir, i)

            if os.path.exists(filename):
                try:
                    os.unlink(filename)
                except:
                    logging.exception(
                        "Can't remove file `{}'".format(filename)
                        )
                    ret = 1

        return ret

    def make_checksums_for_building_site(self):

        ret = 0

        logging.info("Making checksums for buildingsite files")

        buildingsite = org.wayround.utils.path.abspath(self.path)

        package_checksums = os.path.join(
            buildingsite,
            'package.sha512'
            )

        list_to_checksum = self.get_list_of_items_to_pack()

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
                check_summs2[
                    '/' + org.wayround.utils.path.relpath(i, buildingsite)
                    ] = check_summs[i]

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

    def pack_buildingsite(self):
        """
        Create new package from building site and place it under ../pack
        deirectory
        """

        ret = 0

        buildingsite = org.wayround.utils.path.abspath(self.path)

        logging.info("Creating package")

        package_info = self.buildingsite_ctl.read_package_info(
            ret_on_error=None
            )

        if package_info is None:
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
                "({pkgname})-({version})-({status})-"
                "({timestamp})-({hostinfo}).asp".format_map(
                    {
                        'pkgname': package_info['pkg_info']['name'],
                        'version':
                            package_info['pkg_nameinfo']['groups']['version'],
                        'status':
                            package_info['pkg_nameinfo']['groups']['status'],
                        'timestamp':
                            org.wayround.utils.time.currenttime_stamp(),
                        'hostinfo': package_info['constitution']['host'],
                        }
                    )
                )

            logging.info("Package will be saved as: {}".format(pack_file_name))

            if not os.path.isdir(pack_dir):
                os.makedirs(pack_dir)

            list_to_tar = self.get_list_of_items_to_pack()

            list_to_tar2 = []

            for i in list_to_tar:
                list_to_tar2.append(
                    './' + org.wayround.utils.path.relpath(i, buildingsite)
                    )

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

        return ret

    def complete(self):
        """
        Do all specter of pack operations on building site
        """

        ret = 0

        for i in [
                'destdir_verify_paths_correctness',
                'destdir_set_modes',
                'destdir_checksum',
                'destdir_filelist',
                'destdir_deps_bin',
                'compress_patches_destdir_and_logs',
                'compress_files_in_lists_dir',
                'make_checksums_for_building_site',
                'pack_buildingsite'
                ]:

            if eval("self.{}()".format(i)) != 0:
                logging.error("Error on {}".format(i))
                ret = 1
                break

        return ret

    def get_list_of_items_to_pack(self):

        building_site = org.wayround.utils.path.abspath(self.path)

        ret = []

        ret.append(
            org.wayround.utils.path.join(
                building_site,
                DIR_DESTDIR + '.tar.xz'
                )
            )

        ret.append(
            org.wayround.utils.path.join(
                building_site,
                DIR_PATCHES + '.tar.xz'
                )
            )

        ret.append(
            org.wayround.utils.path.join(
                building_site,
                DIR_BUILD_LOGS + '.tar.xz'
                )
            )

        ret.append(
            org.wayround.utils.path.join(
                building_site,
                'package_info.json'
                )
            )

        ret.append(
            org.wayround.utils.path.join(
                building_site,
                'package.sha512'
                )
            )

        post_install_script = org.wayround.utils.path.join(
            building_site, 'post_install.py'
            )

        if os.path.isfile(post_install_script):
            ret.append(post_install_script)

        tarballs = os.listdir(
            self.buildingsite_ctl.getDIR_TARBALL()
            )

        for i in tarballs:
            ret.append(
                org.wayround.utils.path.join(
                    building_site,
                    DIR_TARBALL, i
                    )
                )

        lists = os.listdir(
            self.buildingsite_ctl.getDIR_LISTS()
            )

        for i in lists:
            if i.endswith('.xz'):
                ret.append(
                    org.wayround.utils.path.join(
                        building_site,
                        DIR_LISTS, i
                        )
                    )

        return ret


class BuildingSiteCtl:

    def __init__(self, path):
        self.path = org.wayround.utils.path.abspath(path)

    def getDIR_TARBALL(self):
        return getDIR_TARBALL(self.path)

    def getDIR_SOURCE(self):
        return getDIR_SOURCE(self.path)

    def getDIR_PATCHES(self):
        return getDIR_PATCHES(self.path)

    def getDIR_BUILDING(self):
        return getDIR_BUILDING(self.path)

    def getDIR_DESTDIR(self):
        return getDIR_DESTDIR(self.path)

    def getDIR_BUILD_LOGS(self):
        return getDIR_BUILD_LOGS(self.path)

    def getDIR_LISTS(self):
        return getDIR_LISTS(self.path)

    def getDIR_TEMP(self):
        return getDIR_TEMP(self.path)

    def isWdDirRestricted(self):
        return isWdDirRestricted(self.path)

    def init(self, files=None):
        """
        Initiates building site path for farther package build.

        Files in named directory are not deleted if it is already exists.

        :rtype: returns 0 if no errors
        """

        ret = 0

        path = org.wayround.utils.path.abspath(self.path)

        logging.info("Initiating building site `{}'".format(path))

        logging.info("Checking dir name safety")

        if self.isWdDirRestricted():
            logging.error(
                "`{}' is restricted working dir -- won't init".format(path)
                )
            ret = -1

        # if exists and not derictory - not continue
        if ret == 0:

            if ((os.path.exists(path))
                    and not os.path.isdir(path)):
                logging.error(
                    "File already exists and it is not a building site"
                    )
                ret = -2

        if ret == 0:

            if not os.path.exists(path):
                logging.info("Building site not exists - creating")
                os.mkdir(path)

            logging.info("Creating required subdirs")
            for i in DIR_ALL:
                a = org.wayround.utils.path.abspath(os.path.join(path, i))

                if not os.path.exists(a):
                    resh = 'creating'
                elif not os.path.isdir(a):
                    resh = 'not a dir!'
                elif os.path.islink(a):
                    resh = 'is a link!'
                else:
                    resh = 'exists'

                print("       {dirname} - {resh}".format_map({
                    'dirname': i,
                    'resh': resh
                    })
                    )

                if os.path.exists(a):
                    pass
                else:
                    os.makedirs(a)

        if ret == 0:
            logging.info("Init complete")

            if isinstance(files, list):

                if len(files) > 0:
                    t_dir = self.getDIR_TARBALL()

                    for i in files:
                        logging.info("Copying file {}".format(i))
                        shutil.copy(i, t_dir)

        else:
            logging.error("Init error")

        return ret

    def read_package_info(self, ret_on_error=None):
        """
        Reads package info applied to building site

        :rtype: ``ret_on_error`` parameter contents on error (``None`` by
            default)
        """

        path = org.wayround.utils.path.abspath(self.path)

        logging.debug(
            "Trying to read package info in building site `{}'".format(path)
            )

        ret = ret_on_error

        pi_filename = os.path.join(path, 'package_info.json')

        if not os.path.isfile(pi_filename):
            logging.error("`{}' not found".format(pi_filename))
        else:
            txt = ''
            f = None
            try:
                f = open(pi_filename, 'r')

            except:
                logging.exception("Can't open `{}'".format(pi_filename))

            else:
                txt = f.read()
                f.close()

                try:
                    ret = json.loads(txt)
                except:
                    logging.exception("Error in `{}'".format(pi_filename))

        return ret

    def write_package_info(self, info):
        """
        Writes given info to given building site

        Raises exceptions in case of errors
        """

        path = org.wayround.utils.path.abspath(self.path)

        ret = 0

        package_information_filename = os.path.join(path, 'package_info.json')

        f = None

        try:
            f = open(package_information_filename, 'w')
        except:
            raise Exception(
                "Can't open `{}' for writing".format(
                    package_information_filename
                    )
                )
        else:
            try:
                txt = ''
                try:
                    txt = json.dumps(
                        info,
                        allow_nan=False,
                        indent=2,
                        sort_keys=True
                        )
                except:
                    raise ValueError("Can't represent data for package info")
                else:
                    f.write(txt)

            finally:
                f.close()

        return ret

    def set_pkg_main_tarball(self, filename):
        """
        Set main package tarball in case there are many of them.
        """

        r = self.read_package_info({})

        r['pkg_tarball'] = dict(name=filename)

        self.write_package_info(r)

        return 0

    def get_pkg_main_tarball(self):
        """
        Get main package tarball in case there are many of them.
        """

        ret = ''

        r = self.read_package_info({})

        if 'pkg_tarball' in r and 'name' in r['pkg_tarball']:
            ret = r['pkg_tarball']['name']

        return ret

    def apply_pkg_nameinfo_on_buildingsite(self, filename):
        """
        Applies package name parsing result on building site package info
        """

        ret = 0

        package_info = self.read_package_info(ret_on_error={})

        package_info['pkg_nameinfo'] = None

        base = os.path.basename(filename)

        parse_result = \
            org.wayround.utils.tarball.parse_tarball_name(base)

        if not isinstance(parse_result, dict):
            logging.error("Can't correctly parse file name")
            ret = 1
        else:
            package_info['pkg_nameinfo'] = parse_result

            self.write_package_info(package_info)

            ret = 0

        return ret

    apply_pkg_nameinfo_on_buildingsite.__doc__ += APPLY_DESCR

    def apply_constitution_on_buildingsite(self, const):
        """
        Applies constitution on building site package info
        """

        if not isinstance(const, Constitution):
            raise ValueError(
                "const must be of type "
                "org.wayround.aipsetup.build.Constitution"
                )

        ret = 0

        package_info = self.read_package_info(ret_on_error={})

        const = const.return_aipsetup3_compliant()

        if const is None:
            ret = 1

        else:
            package_info['constitution'] = const
            self.write_package_info(package_info)

        return ret

    apply_constitution_on_buildingsite.__doc__ += APPLY_DESCR

    def apply_pkg_info_on_buildingsite(self, pkg_client):
        """
        Applies package information on building site package info
        """

        if not isinstance(
                pkg_client,
                org.wayround.aipsetup.client_pkg.PackageServerClient
                ):
            raise TypeError(
                "pkg_client must be of type "
                "org.wayround.aipsetup.client_pkg.PackageServerClient"
                )

        ret = 0

        package_info = self.read_package_info(ret_on_error={})

        if (
                not isinstance(package_info, dict)
                or 'pkg_nameinfo' not in package_info
                or not isinstance(package_info['pkg_nameinfo'], dict)
                or 'groups' not in package_info['pkg_nameinfo']
                or not isinstance(package_info['pkg_nameinfo']['groups'], dict)
                or 'name' not in package_info['pkg_nameinfo']['groups']
                or not isinstance(
                    package_info['pkg_nameinfo']['groups']['name'], str
                    )
                ):

            logging.error(
                "package_info['pkg_nameinfo']['groups'] undetermined"
                )
            package_info['pkg_info'] = {}
            ret = 1

        else:

            logging.debug("Getting info from index DB")

            n_b_n = pkg_client.name_by_name(
                package_info['pkg_nameinfo']['name']
                )

            if len(n_b_n) != 1:
                logging.error(
                    "Can't select between package names: {}".format(n_b_n))
                ret = 5

            else:

                info = pkg_client.info(n_b_n[0])

                if not isinstance(info, dict):
                    logging.error("Can't read info from DB")
                    package_info['pkg_info'] = {}
                    ret = 4

                else:

                    package_info['pkg_info'] = info

                    self.write_package_info(package_info)

                    ret = 0

        return ret

    apply_pkg_info_on_buildingsite.__doc__ += APPLY_DESCR

    def apply_info(self, pkg_client, const, src_file_name=None):
        """
        Apply package information to building site
        """

        if not isinstance(const, Constitution):
            raise ValueError(
                "const must be of type "
                "org.wayround.aipsetup.build.Constitution"
                )

        if not isinstance(
                pkg_client,
                org.wayround.aipsetup.client_pkg.PackageServerClient
                ):
            raise TypeError(
                "pkg_client must be of type "
                "org.wayround.aipsetup.client_pkg.PackageServerClient"
                )

        path = org.wayround.utils.path.abspath(self.path)

        ret = 0

        tar_dir = self.getDIR_TARBALL()

        if not isinstance(src_file_name, str):
            tar_files = os.listdir(tar_dir)

            if len(tar_files) != 1:
                logging.error("Can't decide which tarball to use")
                ret = 15
            else:
                src_file_name = tar_files[0]

        if ret == 0:

            if self.read_package_info(None) is None:
                logging.info(
                    "Applying new package info to dir `{}'".format(
                        org.wayround.utils.path.abspath(
                            path
                            )
                        )
                    )

                self.write_package_info({})

            if self.apply_pkg_nameinfo_on_buildingsite(
                    src_file_name
                    ) != 0:
                ret = 1
            elif self.apply_constitution_on_buildingsite(const) != 0:
                ret = 2
            elif self.apply_pkg_info_on_buildingsite(pkg_client) != 0:
                ret = 3

        return ret

    apply_info.__doc__ += APPLY_DESCR

    def _complete_info_correctness_check(self, buildscript_ctl):

        ret = 0

        r = self.read_package_info({})

        scr_name = ''

        try:
            scr_name = r['pkg_info']['buildscript']
        except:
            scr_name = ''

        if (
                scr_name == ''
                or
                not isinstance(
                    buildscript_ctl.load_buildscript(
                        scr_name
                        ),
                    dict
                    )
                ):
            ret = 1

        return ret

    def complete(
            self,
            build_ctl,
            pack_ctl,
            buildscript_ctl,
            pkg_client,
            main_src_file=None,
            const=None,
            remove_buildingsite_after_success=False,
            ):
        """
        Applies package information on building site, does building and
        packaging and optionally deletes building site after everything is
        done.

        :param main_src_file: used with function
            :func:`buildingsite.apply_info
            <org.wayround.aipsetup.buildingsite.apply_info>`
        """

        if not isinstance(const, Constitution):
            raise ValueError(
                "const must be of type "
                "org.wayround.aipsetup.build.Constitution"
                )

        if not isinstance(build_ctl, BuildCtl):
            raise ValueError(
                "build_ctl must be of type "
                "org.wayround.aipsetup.build.BuildCtl"
                )

        if not isinstance(pack_ctl, PackCtl):
            raise ValueError(
                "pack_ctl must be of type org.wayround.aipsetup.build.PackCtl"
                )

        if not isinstance(buildscript_ctl, BuildScriptCtrl):
            raise ValueError(
                "buildscript_ctl must be of type "
                "org.wayround.aipsetup.build.BuildScriptCtrl"
                )

        if not isinstance(
                pkg_client,
                org.wayround.aipsetup.client_pkg.PackageServerClient
                ):
            raise TypeError(
                "pkg_client must be of type "
                "org.wayround.aipsetup.client_pkg.PackageServerClient"
                )

        rp = org.wayround.utils.path.relpath(self.path, os.getcwd())

        logging.info(
            "+++++++++++ Starting Complete build under `{}' +++++++++++".
            format(rp)
            )

        building_site = org.wayround.utils.path.abspath(self.path)

        ret = 0

        if (self._complete_info_correctness_check(buildscript_ctl) != 0
                or isinstance(main_src_file, str)):

            logging.warning(
                "buildscript information not available "
                "(or new main tarball file forced)"
                )

            if self.apply_info(pkg_client, const, main_src_file) != 0:
                logging.error("Can't apply build information to site")
                ret = 15

        if ret == 0:
            if self._complete_info_correctness_check(buildscript_ctl) != 0:

                logging.error(
                    "`{}' has wrong build script name".format(main_src_file)
                    )
                ret = 16

        if ret == 0:

            log = org.wayround.utils.log.Log(
                self.getDIR_BUILD_LOGS(),
                'buildingsite complete'
                )
            log.info("Buildingsite processes started")
            log.warning("Closing this log now, cause it can't work farther")
            log.stop()

            if build_ctl.complete(buildscript_ctl) != 0:
                logging.error("Error on building stage")
                ret = 1
            elif pack_ctl.complete() != 0:
                logging.error("Error on packaging stage")
                ret = 2

        if ret == 0:
            if remove_buildingsite_after_success:
                logging.info("Removing buildingsite after successful build")
                try:
                    shutil.rmtree(building_site)
                except:
                    logging.exception(
                        "Could not remove `{}'".format(building_site)
                        )

        logging.info(
            "+++++++++++ Finished Complete build under `{}' +++++++++++".
            format(rp)
            )

        return ret


class BuildScriptCtrl:

    def __init__(self, dirname):

        self.dirname = dirname

    def load_buildscript(self, name):
        """
        Loads building script with exec function and returns it's global
        dictionary. ``None`` is returned in case of error.
        """

        ret = None

        buildscript_filename = org.wayround.utils.path.abspath(
            os.path.join(
                self.dirname,
                '{}.py'.format(name)
                )
            )

        if not os.path.isfile(buildscript_filename):
            logging.error(
                "Can't find building script `{}'".format(buildscript_filename)
                )
            ret = 1

        else:

            txt = ''
            try:
                f = open(buildscript_filename, 'r')
            except:
                logging.exception(
                    "Can't read file `{}'".format(buildscript_filename)
                    )
                ret = 2
            else:
                txt = f.read()
                f.close()

                globals_dict = {}
                locals_dict = globals_dict

                try:
                    exec(
                        compile(
                            txt,
                            buildscript_filename,
                            'exec'
                            ),
                        globals_dict,
                        locals_dict
                        )

                except:
                    logging.exception(
                        "Can't load building script `{}'".format(
                            buildscript_filename
                            )
                        )
                    ret = 3

                else:

                    try:
                        ret = globals_dict
                    except:
                        logging.exception(
                            "Error while calling "
                            "for build_script() from `{}'".format(
                                buildscript_filename
                                )
                            )
                        ret = 5

                    else:
                        logging.info(
                            "Loaded building script: `{}'".format(
                                buildscript_filename
                                )
                            )

        return ret


def getDIR_x(path, _x='TARBALL'):
    '''
    Returns absolute path to DIR_{_x}
    '''

    ret = org.wayround.utils.path.abspath(
        org.wayround.utils.path.join(
            path,
            eval('DIR_{}'.format(_x)))
        )

    return ret


def getDIR_TARBALL(path):
    return getDIR_x(path, 'TARBALL')


def getDIR_SOURCE(path):
    return getDIR_x(path, 'SOURCE')


def getDIR_PATCHES(path):
    return getDIR_x(path, 'PATCHES')


def getDIR_BUILDING(path):
    return getDIR_x(path, 'BUILDING')


def getDIR_DESTDIR(path):
    return getDIR_x(path, 'DESTDIR')


def getDIR_BUILD_LOGS(path):
    return getDIR_x(path, 'BUILD_LOGS')


def getDIR_LISTS(path):
    return getDIR_x(path, 'LISTS')


def getDIR_TEMP(path):
    return getDIR_x(path, 'TEMP')


def build_script_wrap(buildingsite, desired_actions, action, help_text):
    """
    Used by building scripts for parsing action command

    :param buildingsite: path to building site
    :param desired_actions: list of possible actions
    :param action: action selected by building script user
    :param help_text: if action == 'help', help_text is text to show before
        list of available actions
    :rtype: ``int`` if error. ``tuple`` (package_info, actions), where
        ``package_info`` is package info readen from building site package info
        file, ``actions`` - list of actions, needed to be run by building
        script
    """

    bs = BuildingSiteCtl(buildingsite)

    pkg_info = bs.read_package_info()

    ret = 0

    if not isinstance(pkg_info, dict):
        logging.error("Can't read package info")
        ret = 1
    else:

        actions = copy.copy(desired_actions)

        if action == 'help':
            print(help_text)
            print("")
            print("Available actions: {}".format(actions))
            ret = 2
        else:

            r = build_actions_selector(
                actions,
                action
                )

            if not isinstance(r, tuple):
                logging.error("Wrong command 1")
                ret = 2
            else:

                actions, action = r

                if action is not None and not isinstance(action, str):
                    logging.error("Wrong command 2")
                    ret = 3
                else:

                    if not isinstance(actions, list):
                        logging.error("Wrong command 3")
                        ret = 3

                    else:

                        ret = (pkg_info, actions)

    return ret


def build_actions_selector(actions, action):
    """
    Used by :func:`build_script_wrap` to build it's valid return action list

    :rtype: ``None`` if error. tuple (actions, action), where ``action = None``
        if ``action == 'complete'``. If ``action == 'help'``, both values
        returned without changes. If action is one of actions, ``actions =
        [action]``. If action is one of actions and action ends with + sign,
        ``actions = actions[(action position):]``
    """

    ret = None

    actions = copy.copy(actions)

    if action == 'complete':
        action = None

    # action == None - indicates all actions! equals to 'complete'
    if action in [None, 'help']:
        ret = (actions, action)

    else:

        continued_action = True

        if isinstance(action, str) and action.endswith('+'):

            continued_action = True
            action = action[:-1]

        else:
            continued_action = False

        # if not action available - return error
        if action not in actions:

            ret = 2

        else:

            action_pos = actions.index(action)

            if continued_action:
                actions = actions[action_pos:]
            else:
                actions = [actions[action_pos]]

            ret = (actions, action)

    return ret


def isWdDirRestricted(path):
    """
    This function is a routine to check supplied path is it suitable to be a
    building site.

    List of forbidden path beginnings::

        [
        '/bin', '/boot' , '/daemons',
        '/dev', '/etc', '/lib', '/proc',
        '/sbin', '/sys',
        '/usr'
        ]

    This dirs ar directly forbidden, but subdirs are allowed::

        ['/opt', '/var', '/']

    :param path: path to directory
    :rtype: ``True`` if restricted. ``False`` if not restricted.
    """

    ret = False

    dirs_begining_with = [
        '/bin', '/boot', '/daemons',
        '/dev', '/etc', '/lib', '/proc',
        '/sbin', '/sys',
        '/usr'
        ]

    exec_dirs = ['/opt', '/var', '/']

    dir_str_abs = org.wayround.utils.path.abspath(path)

    for i in dirs_begining_with:
        if dir_str_abs.startswith(i):
            ret = True
            break

    if not ret:
        for i in exec_dirs:
            if i == dir_str_abs:
                ret = True
                break
    return ret


def build(
        config,
        source_files,
        buildingsites_dir,
        remove_buildingsite_after_success=False,
        const=None
        ):
    """
    Gathering function for all package building process

    Uses :func:`org.wayround.aipsetup.buildingsite.init` to create building
    site. Farther process controlled by :func:`complete`.

    :param source_files: tarball name or list of them.
    """

    # TODO: remove config parameter or move this function to commands modules
    # NOTE: (for TODO above) can't decide where to put this function: it's not
    #       a command nor it's a basic build mechanizm. let's leave it here

    if not isinstance(const, Constitution):
        raise ValueError(
            "system_type must be of type "
            "org.wayround.aipsetup.build.Constitution"
            ", not `{}'".format(const)
            )

    ret = 0

    par_res = org.wayround.utils.tarball.parse_tarball_name(
        source_files[0],
        mute=True
        )

    if not isinstance(par_res, dict):
        logging.error("Can't parse source file name")
        ret = 1
    else:

        if not os.path.isdir(buildingsites_dir):
            try:
                os.makedirs(buildingsites_dir)
            except:
                logging.error(
                    "Can't create directory: {}".format(buildingsites_dir)
                    )

        if not os.path.isdir(buildingsites_dir):
            logging.error("Directory not exists: {}".format(buildingsites_dir))
            ret = 7

        else:

            pkg_client = \
                org.wayround.aipsetup.controllers.pkg_client_by_config(config)

            pkg_name = pkg_client.name_by_name(source_files[0])

            if pkg_name is None:
                logging.error(
                    "Can't determine package name."
                    " Is server running?".format(
                        source_files[0],
                        pkg_name
                        )
                    )
                ret = 10

            if ret == 0:
                if len(pkg_name) != 1:
                    logging.error("""\
Can't select between those package names (for {})
(please, fix package names to not make collisions):
   {}
""".format(
                        source_files[0],
                        pkg_name
                        )
                        )
                    ret = 4
                else:
                    pkg_name = pkg_name[0]

            if ret == 0:

                package_info = pkg_client.info(pkg_name)

                if not package_info:
                    logging.error(
                        "Can't get package "
                        "information for tarball `{}'".format(
                            source_files[0]
                            )
                        )
                    ret = 2
                else:

                    tmp_dir_prefix = \
                        "{name}-{version}-{status}-{timestamp}-".format_map(
                            {
                                'name': package_info['name'],
                                'version': par_res['groups']['version'],
                                'status': par_res['groups']['status'],
                                'timestamp':
                                    org.wayround.utils.time.currenttime_stamp()
                                }
                            )

                    build_site_dir = tempfile.mkdtemp(
                        prefix=tmp_dir_prefix,
                        dir=buildingsites_dir
                        )

                    bs = org.wayround.aipsetup.controllers.bsite_ctl_new(
                        build_site_dir
                        )

                    if bs.init(source_files) != 0:
                        logging.error("Error initiating temporary dir")
                        ret = 3
                    else:

                        build_ctl = \
                            org.wayround.aipsetup.controllers.build_ctl_new(bs)

                        pack_ctl = \
                            org.wayround.aipsetup.controllers.pack_ctl_new(bs)

                        buildscript_ctl = \
                            org.wayround.aipsetup.controllers.\
                            bscript_ctl_by_config(config)

                        if bs.complete(
                                build_ctl,
                                pack_ctl,
                                buildscript_ctl,
                                pkg_client,
                                source_files[0],
                                const=const,
                                remove_buildingsite_after_success=(
                                    remove_buildingsite_after_success
                                    )
                                ) != 0:

                            logging.error("Package building failed")
                            ret = 5

                        else:
                            logging.info(
                                "Complete package building ended with no error"
                                )
                            ret = 0

    return ret
