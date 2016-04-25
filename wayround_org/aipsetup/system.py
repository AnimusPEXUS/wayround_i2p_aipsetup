
import copy
import datetime
import fnmatch
import functools
import glob
import io
import logging
import os.path
import pprint
import re
import shutil
import shlex
import subprocess
import tarfile
import bottle


import wayround_org.utils.file
import wayround_org.utils.format.elf
import wayround_org.utils.list
import wayround_org.utils.path
import wayround_org.utils.terminal
import wayround_org.utils.system_type

import wayround_org.aipsetup.client_pkg
import wayround_org.aipsetup.package
import wayround_org.aipsetup.package_name_parser
import wayround_org.aipsetup.version

import certdata.certdata

DAEMONS_DIR = '/daemons'
MULTIHOST_DIR = '/multihost'

LOCAL_DIRS = [
    'boot',
    'dev',
    'etc',
    'home',
    'lost+found',
    'mnt',
    'proc',
    'root',
    'run',
    'sys',
    'var',
    'tmp'
    ]


class SystemCtl:

    def __init__(
            self,
            pkg_client,
            basedir='/',
            installed_pkg_dir='/var/log/packages',
            installed_pkg_dir_buildlogs='/var/log/packages/buildlogs',
            installed_pkg_dir_sums='/var/log/packages/sums',
            installed_pkg_dir_deps='/var/log/packages/deps'
            ):
        """
        :param basedir: path to root directory of target system
            (absoluted internally)
        :param host:

        following paramaters has default values only as extramesure and like
            host should always be taken from config!!!

        :param installed_pkg_dir: '/var/log/packages'
        :param installed_pkg_dir_buildlogs: '/var/log/packages/buildlogs'
        :param installed_pkg_dir_sums: '/var/log/packages/sums'
        :param installed_pkg_dir_deps: '/var/log/packages/deps'
        """

        if not isinstance(
                pkg_client,
                wayround_org.aipsetup.client_pkg.PackageServerClient
                ):

            raise ValueError(
                "pkg_client must be of type "
                "wayround_org.aipsetup.client_pkg.PackageServerClient"
                )

        self.basedir = wayround_org.utils.path.abspath(basedir)

        self._pkg_client = pkg_client

        self._installed_pkg_dir = wayround_org.utils.path.join(
            self.basedir,
            installed_pkg_dir
            )
        self._installed_pkg_dir_buildlogs = wayround_org.utils.path.join(
            self.basedir,
            installed_pkg_dir_buildlogs
            )
        self._installed_pkg_dir_sums = wayround_org.utils.path.join(
            self.basedir,
            installed_pkg_dir_sums
            )
        self._installed_pkg_dir_deps = wayround_org.utils.path.join(
            self.basedir,
            installed_pkg_dir_deps
            )

        return

    def _test_host_arch_parameters(self, host, arch):

        if host is not None and not isinstance(host, str):
            raise ValueError("if `host' not None, it must be str")

        if arch is not None and not isinstance(arch, str):
            raise ValueError("if `arch' not None, it must be str")

        if host is None and arch is not None:
            raise ValueError("if `host' is None, `arch' must be None too")

        if isinstance(host, str):
            if wayround_org.utils.system_type.parse_triplet(host) is None:
                raise bottle.HTTPError(400, "Invalid host triplet")

        if isinstance(arch, str):
            if wayround_org.utils.system_type.parse_triplet(arch) is None:
                raise bottle.HTTPError(400, "Invalid arch triplet")

        return

    def remove_package(
            self,
            name,
            force=False,
            mute=False,
            host=None,
            arch=None
            ):
        """
        Remove named package (all it's installed asps) from system.

        Before package removal, aipsetup checks whatever package removal is
        restricted. This can be overridden with ``force=True`` option.

        :param name: package name. e.g. ``gajim``, ``php`` or ``ruby``. List
            of installed package names can be retrieved with command
            ``aipsetup pkg list``

        :param force: force package removal even if it is not registered in
            info record system

        :param mute: suppress status output
        """

        ret = 0

        self._test_host_arch_parameters(host, arch)

        info = self._pkg_client.info(name)

        if not isinstance(info, dict) and not force:
            logging.error(
                "Can't find information about package `{}'".format(name)
                )

            ret = 1

        else:
            if (not force
                    and (isinstance(info, dict) and not info['removable'])):

                logging.error("Package `{}' is not removable".format(name))

                ret = 2

            else:

                lst = self.list_installed_package_s_asps(
                    name,
                    host=host,
                    arch=arch
                    )

                lst.sort(
                    reverse=True,
                    key=functools.cmp_to_key(
                        wayround_org.aipsetup.version.
                        package_version_comparator
                        )
                    )

                if not mute:
                    print("Following packages will be removed:")
                    for i in lst:
                        print("    {}".format(i))

                for i in lst:

                    name = \
                        wayround_org.aipsetup.package_name_parser.\
                        rm_ext_from_pkg_name(i)

                    if not mute:
                        logging.info("Removing package `{}'".format(name))

                    self.remove_asp(name)

        return ret

    def install_package(
            self,
            name,
            force=False,
            host=None,
            arch=None
            ):
        """
        Install package

        This method works in two modes:

            One mode, is when name is package name registered with package
            database records. In this case, aipsetup finds latest asp package
            located in package index directory and calls this(install_package)
            function with ``name == 'full path to asp'``

            Second mode, is when name is pointing on existing file. In this
            case next sequence is done:

                #. install package using :func:`install_asp`

                #. check whatever package is reducible, and if it is — reduce
                   older asps from system using :func:`reduce_asps`
        """

        self._test_host_arch_parameters(host, arch)

        ret = 0

        if os.path.isfile(name):

            host = None

            logging.info(
                "Trying to install file (package) `{}'".format(
                    wayround_org.utils.path.abspath(name)
                    )
                )

            name_parsed = \
                wayround_org.aipsetup.package_name_parser.package_name_parse(
                    name
                    )

            if not force and not isinstance(name_parsed, dict):
                logging.error("Can't parse `{}' as package name".format(name))
                ret = 1

            if ret == 0:
                info = None
                if isinstance(name_parsed, dict):
                    # FIXME: get package info from package it self
                    #        (or maybe not :-/ can't decide)
                    try:
                        info = self._pkg_client.info(
                            name_parsed['groups']['name']
                            )
                    except:
                        logging.exception("Can't get package info")

                if not isinstance(info, dict) and not force:
                    logging.error(
                        "Can't get info on package `{}' : `{}'".format(
                            name_parsed['groups']['name'], name)
                        )
                    ret = 2

            if ret == 0:
                try:
                    host = name_parsed['groups']['host']
                    arch = name_parsed['groups']['arch']
                except:
                    logging.exception("error")
                    ret = 6

            if ret == 0:
                if (not force
                        and (
                            info['deprecated']
                            or info['non_installable']
                            )
                    ):
                    logging.error(
                        "Package is deprecated({}) or"
                        " non-installable({})".format(
                            info['deprecated'],
                            info['non_installable']
                        )
                    )
                    ret = 3

            if ret == 0:
                if (not force
                        and info['only_primary_install']
                        and arch != host
                    ):
                    logging.error(
                        "Package is only_primary_install({}) but"
                        " host != arch"
                        " ({} != {})".format(
                            info['only_primary_install'],
                            host,
                            arch
                        )
                    )
                    ret = 7

            if ret == 0:

                asps = self.list_installed_package_s_asps(
                    name_parsed['groups']['name'],
                    host=host,
                    arch=arch
                    )

                ret = self.install_asp(name)

                if len(asps) == 0:
                    if ret == 0:
                        logging.info("New ASP installation finished")
                    else:
                        logging.error("Some ASP installation errors")

                else:

                    if ret != 0:
                        logging.error(
                            "Some ASP installation errors encountered,"
                            " so no updation following"
                            )
                    else:
                        if isinstance(info, dict):
                            if info['reducible']:
                                logging.info(
                                    "Reducing `{}' ASPs".format(
                                        name_parsed['groups']['name']
                                        )
                                    )
                                self.reduce_asps(
                                    name,
                                    reduce_what=asps,
                                    mute=False,
                                    host=host,
                                    arch=arch
                                    )
                                logging.info(
                                    "Reduced `{}' ASPs".format(
                                        name_parsed['groups']['name']
                                        )
                                    )

        else:
            info = self._pkg_client.info(name)

            if not isinstance(info, dict):
                logging.error("Don't know about package")
                ret = 2

            if ret == 0:

                if info['deprecated'] or info['non_installable']:
                    logging.error(
                        "Package is deprecated({}) "
                        "or non-installable({})".format(
                            info['deprecated'],
                            info['non_installable']
                            )
                    )
                    ret = 3

            if ret == 0:

                latest_full_path = self._pkg_client.get_latest_asp(
                    name,
                    host=host,
                    arch=arch,
                    out_dir=self._pkg_client.downloads_dir,
                    out_to_temp=True
                    )

                if not isinstance(latest_full_path, str):
                    logging.error("Can't get latest asp from pkg_server")
                    ret = 4

            if ret == 0:

                latest_full_path = wayround_org.utils.path.abspath(
                    latest_full_path
                    )

                ret = self.install_package(
                    latest_full_path,
                    force=False,
                    host=host,
                    arch=arch
                    )

                try:
                    os.unlink(latest_full_path)
                except:
                    logging.exception(
                        "Can't remove temporary file `{}'".format(
                            latest_full_path
                            )
                        )

        return ret

    def install_asp(
            self,
            asp_package
            ):
        """
        Install asp package pointed by ``asp_name`` path.

        See also :func:`install_package`
        """

        ret = 0

        # TODO: exceptions and sanity checks required

        tarf = None

        try:

            asp = wayround_org.aipsetup.package.ASPackage(asp_package)
            host = asp.host
            arch = asp.arch

        except:
            logging.exception("Some error")
            ret = 5

        if ret == 0:

            logging.info("Performing package checks before it's installation")
            if asp.check_package() != 0:
                logging.error("Package defective - installation failed")
                ret = 1

        if ret == 0:

            try:
                tarf = tarfile.open(asp.filename, mode='r')
            except:
                logging.exception("Can't open file `{}'".format(asp.filename))
                tarf = None
                ret = 1

        if ret == 0:

            package_name = os.path.basename(asp.filename)

            if wayround_org.aipsetup.package_name_parser.package_name_parse(
                    package_name
                    ) is None:

                logging.error(
                    "Can't parse package name `{}'".format(package_name)
                    )
                ret = 2

        if ret == 0:

            logging.info("Installing lists")

            package_name = package_name[:-4]
            for i in [
                    (
                        './06.LISTS/DESTDIR.lst.xz',
                        self._installed_pkg_dir,
                        "package's file list"
                        ),
                    (
                        './06.LISTS/DESTDIR.sha512.xz',
                        self._installed_pkg_dir_sums,
                        "package's check sums"
                        ),
                    (
                        './05.BUILD_LOGS.tar.xz',
                        self._installed_pkg_dir_buildlogs,
                        "package's buildlogs"
                        ),
                    (
                        './06.LISTS/DESTDIR.dep_c.xz',
                        self._installed_pkg_dir_deps,
                        "package's dependencies listing"
                        )
                    ]:

                logging.info(i[1])

                logs_path = i[1]

                if logs_path.startswith(os.path.sep):
                    logs_path = logs_path[1:]

                if i[0] == './05.BUILD_LOGS.tar.xz':
                    out_filename = (
                        wayround_org.utils.path.abspath(
                            wayround_org.utils.path.join(
                                i[1],
                                package_name + '.tar.xz'
                                )
                            )
                        )
                else:
                    out_filename = (
                        wayround_org.utils.path.abspath(
                            wayround_org.utils.path.join(
                                i[1],
                                package_name + '.xz'
                                )
                            )
                        )

                out_filename_dir = os.path.dirname(out_filename)

                if not os.path.exists(out_filename_dir):
                    os.makedirs(out_filename_dir)

                logging.info(
                    "Installing {} as {}".format(
                        i[2],
                        out_filename
                        )
                    )

                if wayround_org.utils.archive.tar_member_get_extract_file_to(
                        tarf,
                        i[0],
                        out_filename
                        ) != 0:

                    logging.error(
                        "Can't install asp {} as {}".format(
                            i[2],
                            out_filename
                            )
                        )

                    ret = 2
                    break

        if ret == 0:
            logging.info("Installing package's destdir")

            dd_fobj = wayround_org.utils.archive.tar_member_get_extract_file(
                tarf,
                './{}.tar.xz'.format(
                    wayround_org.aipsetup.build.DIR_DESTDIR
                    )
                )
            if not isinstance(dd_fobj, tarfile.ExFileObject):
                logging.error("Can't get package's destdir")
                ret = 4
            else:
                try:
                    tec = \
                        wayround_org.utils.archive.extract_tar_canonical_fobj(
                            dd_fobj,
                            self.basedir,
                            'xz',
                            verbose_tar=True,
                            verbose_compressor=True,
                            add_tar_options=[
                                '--no-same-owner',
                                '--no-same-permissions'
                                ]
                            )
                    if tec != 0:
                        logging.error(
                            "Package destdir decompression error."
                            " tar exit code: {}".format(
                                tec
                            )
                        )
                        ret = 5
                    else:
                        ret = 0
                        logging.info(
                            "Installed `{}'".format(package_name)
                            )
                finally:
                    dd_fobj.close()

        if ret == 0:
            logging.info(
                "Post installation file ownerships and modes fix"
                )

            files = []
            dirs = []

            installed_file_list = \
                wayround_org.utils.archive.tar_member_get_extract_file(
                    tarf,
                    './06.LISTS/DESTDIR.lst.xz'
                    )

            if not isinstance(
                    installed_file_list,
                    tarfile.ExFileObject
                    ):

                logging.error("Can't get package's file list")
                ret = 10
            else:
                try:
                    text_lst = wayround_org.utils.archive.xzcat(
                        installed_file_list,
                        convert_to_str='utf-8'
                        )

                    files = text_lst.split('\n')

                    files = sorted(
                        wayround_org.utils.list.
                        filelist_strip_remove_empty_remove_duplicated_lines(
                            files
                            )
                        )

                    dirs = set()
                    for i in files:
                        dirs.add(os.path.dirname(i))
                    dirs = sorted(dirs)

                    for i in dirs:
                        f_d_p = wayround_org.utils.path.abspath(
                            wayround_org.utils.path.join(
                                self.basedir,
                                i
                                )
                            )

                        if not os.path.islink(f_d_p):
                            if os.getuid() == 0:
                                os.chown(f_d_p, 0, 0)
                            os.chmod(f_d_p, 0o755)

                    for i in files:
                        f_f_p = wayround_org.utils.path.abspath(
                            wayround_org.utils.path.join(
                                self.basedir,
                                i
                                )
                            )

                        if not os.path.islink(f_f_p):
                            if os.getuid() == 0:
                                os.chown(f_f_p, 0, 0)
                            os.chmod(f_f_p, 0o755)
                finally:
                    installed_file_list.close()

        if ret == 0:
            logging.info("Searching post installation script")

            script_obj = \
                wayround_org.utils.archive.tar_member_get_extract_file(
                    tarf,
                    './post_install.py'
                    )

            if not isinstance(script_obj, tarfile.ExFileObject):
                logging.info(
                    "Can't get package's post installation script"
                    )

            else:
                try:
                    script_txt = script_obj.read()

                    g = {}
                    l = g
                    try:
                        exec(
                            script_txt,
                            g,
                            l
                            )
                    except:
                        logging.exception(
                            "Can't load package's post installation script"
                            )
                        ret = 7

                    else:
                        if l['main'](self.basedir) != 0:
                            logging.error(
                                "Post installation script main "
                                "function returned error"
                                )
                            ret = 8
                finally:
                    script_obj.close()

        if tarf is not None:
            tarf.close()
            tarf = None

        return ret

    def remove_asp(
            self,
            asp_name,
            only_remove_package_registration=False,
            exclude=None,
            mute=False
            ):
        """
        Removes named asp from destdir system.

        :param exclude: can be ``None`` or ``list`` of files which is NOT
            PREPENDED WITH DESTDIR

        :param only_remove_package_registration: do not actually remove files
            from system, only remove it's registration
        """

        ret = 0

        exclude = copy.copy(exclude)

        # ensure destdir correctness
        destdir = wayround_org.utils.path.abspath(self.basedir)

        lines = self.list_files_installed_by_asp(
            asp_name,
            mute=mute
            )

        if not isinstance(lines, list):
            logging.error(
                "Some errors while getting ASP's file list for `{}'".format(
                    asp_name
                    )
                )
            ret = 1
        else:

            # from this point we working with other system's files
            lines = wayround_org.utils.path.prepend_path(lines, destdir)

            lines = wayround_org.utils.path.realpaths(lines)

            logging.info("Removing `{}' files".format(asp_name))

            if not only_remove_package_registration:

                if exclude:

                    # Some files need to be excluded from removal operation

                    lines_before_ex = len(lines)

                    exclude = wayround_org.utils.path.prepend_path(
                        exclude,
                        destdir
                        )

                    exclude = wayround_org.utils.path.realpaths(exclude)

                    lines = list(set(lines) - set(exclude))

                    # Statistics about excluded files
                    lines_after_ex = len(lines)

                    if lines_before_ex != lines_after_ex:
                        logging.info(
                            "Excluded {} new files".format(
                                lines_before_ex - lines_after_ex
                                )
                            )

                logging.info("Excluding shared objects")
                shared_objects = set()
                for i in lines:
                    if os.path.isfile(i):
                        if os.path.dirname(i) in [
                                wayround_org.utils.path.join(
                                    self.basedir, 'usr', 'lib'
                                    ),
                                wayround_org.utils.path.join(
                                    self.basedir, 'usr', 'lib64'
                                    ),
                                wayround_org.utils.path.join(
                                    self.basedir, 'usr', 'lib32'
                                    ),
                                wayround_org.utils.path.join(
                                    self.basedir, 'usr', 'libx32'
                                    ),
                                ] + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multiarch', '*', 'lib'
                                        )
                                    ) + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multiarch', '*', 'lib64'
                                        )
                                    ) + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multiarch', '*', 'lib32'
                                        )
                                    ) + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multiarch', '*', 'libx32'
                                        )
                                    ) + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multihost', '*', 'lib'
                                        )
                                    ) + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multihost', '*', 'lib64'
                                        )
                                    ) + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multihost', '*', 'lib32'
                                        )
                                    ) + glob.glob(
                                    wayround_org.utils.path.join(
                                        self.basedir, 'multihost', '*', 'libx32'
                                        )
                                    ):
                            e = wayround_org.utils.format.elf.ELF(i)
                            if e.elf_type_name == 'ET_DYN':
                                shared_objects.add(i)

                if exclude:
                    shared_objects -= set(exclude)

                for i in sorted(shared_objects):
                    logging.info("   excluded: {}".format(i))

                lines = list(set(lines) - set(shared_objects))

                lines.sort(reverse=True)

                for line in lines:

                    rm_file_name = wayround_org.utils.path.abspath(
                        line
                        )

                    if (
                            (os.path.islink(rm_file_name)
                             and not os.path.exists(rm_file_name)
                             )
                            or
                            os.path.isfile(rm_file_name)
                            or
                            (os.path.isdir(rm_file_name)
                             and wayround_org.utils.file.is_dir_empty(
                                rm_file_name
                                )
                             )
                            ):
                        if not mute:
                            logging.info(
                                "   removing: {}".format(rm_file_name)
                                )

                        if (
                                os.path.isfile(rm_file_name)
                                or os.path.islink(rm_file_name)
                                ):

                            try:
                                os.unlink(rm_file_name)
                            except:
                                logging.exception(
                                    "Couldn't remove file: {}".format(
                                        rm_file_name
                                        )
                                    )

                            else:

                                rm_file_name_dir = os.path.dirname(
                                    rm_file_name
                                    )

                                if not os.path.islink(rm_file_name_dir):
                                    if wayround_org.utils.file.is_dir_empty(
                                            rm_file_name_dir
                                            ):
                                        try:
                                            os.rmdir(rm_file_name_dir)
                                        except:
                                            logging.exception(
                                                "Couldn't remove dir: {}".format(
                                                    rm_file_name_dir
                                                    )
                                                )

                        else:
                            try:
                                os.rmdir(rm_file_name)
                            except:
                                logging.exception(
                                    "Couldn't remove dir: {}".format(
                                        rm_file_name
                                        )
                                    )

            if len(shared_objects) != 0:

                logging.warning(
                    "{} shared objects of asp `{}' "
                    "was remained in system".format(
                        len(shared_objects),
                        asp_name
                        )
                    )

                for i in sorted(shared_objects):
                    logging.info("   excluded: {}".format(i))

            for i in [
                    self._installed_pkg_dir_buildlogs,
                    self._installed_pkg_dir_sums,
                    self._installed_pkg_dir_deps,
                    self._installed_pkg_dir
                    ]:

                if i == self._installed_pkg_dir_buildlogs:
                    rm_file_name = wayround_org.utils.path.abspath(
                        wayround_org.utils.path.join(
                            i,
                            asp_name + '.tar.xz'
                            )
                        )
                else:
                    rm_file_name = wayround_org.utils.path.abspath(
                        wayround_org.utils.path.join(
                            i,
                            asp_name + '.xz'
                            )
                        )

                if os.path.isfile(rm_file_name):
                    logging.info("   removing: {}".format(rm_file_name))
                    os.unlink(rm_file_name)

        return ret

    def reduce_asps(
            self,
            reduce_to,
            reduce_what=None,
            mute=False,
            host=None,
            arch=None
            ):
        """
        Reduces(removes) packages listed in ``reduce_what`` list, remaining all
        files belonging to package named in ``reduce_to`` string parameter
        """

        # TODO: make non-primary asps unable uninstall global files
        #       (i.e. /etc, /var ...)

        self._test_host_arch_parameters(host, arch)

        ret = 0

        if not isinstance(reduce_what, list):
            raise ValueError("reduce_what must be a list of strings")

        reduce_to = os.path.basename(reduce_to)

        reduce_to = (
            wayround_org.aipsetup.package_name_parser.rm_ext_from_pkg_name(
                reduce_to
                )
            )

        for i in range(len(reduce_what)):
            reduce_what[i] = os.path.basename(reduce_what[i])
            reduce_what[i] = (
                wayround_org.aipsetup.package_name_parser.rm_ext_from_pkg_name(
                    reduce_what[i]
                    )
                )

        if reduce_to in reduce_what:
            reduce_what.remove(reduce_to)

        if self.basedir != '/':
            if not mute:
                logging.info("Destdir: {}".format(self.basedir))

        fiba = self.list_files_installed_by_asp(
            reduce_to,
            mute=True
            )

        if not isinstance(fiba, list):
            logging.error(
                "Some error getting list of files installed by {}".format(
                    reduce_to
                    )
                )
            ret = 1
        else:

            for i in reduce_what:
                self.remove_asp(i, exclude=fiba)

        return ret

    def list_installed_asps(
            self,
            mute=False,
            host=None,
            arch=None,
            remove_extensions=False
            ):
        """
        on success returns list. on error - not list

        if host is False - return all asps

        if host is str and arch is str - filter both by host and arch
        """

        # TODO: this method need to return names without .xz extensions
        #       by default

        self._test_host_arch_parameters(host, arch)

        destdir = wayround_org.utils.path.abspath(self.basedir)

        listdir = wayround_org.utils.path.abspath(
            self._installed_pkg_dir
            )

        filelist = os.listdir(listdir)
        for i in range(len(filelist) - 1, -1, -1):

            if not filelist[i].endswith('.xz'):
                del filelist[i]
                continue

            j = wayround_org.utils.path.join(
                listdir,
                filelist[i]
                )

            if not os.path.isfile(j) or os.path.islink(j):
                del filelist[i]
                continue

        if host is not None:
            for i in range(len(filelist) - 1, -1, -1):
                asp = wayround_org.aipsetup.package.ASPackage(filelist[i])
                if host != asp.host:
                    del filelist[i]

        if arch is not None:
            for i in range(len(filelist) - 1, -1, -1):
                asp = wayround_org.aipsetup.package.ASPackage(filelist[i])
                if arch != asp.arch:
                    del filelist[i]

        ret = filelist

        if remove_extensions:
            for i in range(len(ret)):
                if ret[i].endswith('.xz'):
                    ret[i] = ret[i][:-3]

        ret.sort()

        return ret

    def list_installed_packages(
            self,
            mask='*',
            mute=False,
            host=None,
            arch=None
            ):

        self._test_host_arch_parameters(host, arch)

        ret = None

        asps = self.list_installed_asps(
            mute=True,
            host=host,
            arch=arch
            )

        if not isinstance(asps, list):
            logging.error("Error getting list of installed ASPs")
        else:

            lst = set()

            for i in asps:
                parsed = \
                    wayround_org.aipsetup.package_name_parser.\
                    package_name_parse(i)

                if not isinstance(parsed, dict):
                    logging.error("Couldn't parse name `{}'".format(i))
                else:
                    name = parsed['groups']['name']
                    if fnmatch.fnmatch(name, mask):
                        lst.add(name)

            lst = list(lst)

            ret = lst

        return ret

    def list_installed_package_s_asps(
            self,
            name_or_list,
            host=None,
            arch=None
            ):

        self._test_host_arch_parameters(host, arch)

        ret = {}

        return_single = False

        if isinstance(name_or_list, str):
            return_single = True
            name_or_list = [name_or_list]

        asps_list = self.list_installed_asps(
            mute=True,
            host=host,
            arch=arch
            )

        if not isinstance(asps_list, list):
            logging.error("Can't get list of installed asps")
        else:

            asps_list_parsed = {}

            for i in asps_list:
                asps_list_parsed[i] = \
                    wayround_org.aipsetup.package_name_parser.\
                    package_name_parse(i)

            for i in name_or_list:

                if not i in ret:
                    ret[i] = []

                for j in asps_list:

                    if (isinstance(asps_list_parsed[j], dict)
                            and asps_list_parsed[j]['groups']['name'] == i):

                        ret[i].append(j)

            if return_single:
                ret = ret[name_or_list[0]]

        return ret

    def list_files_installed_by_asp(
            self,
            asp_name,
            mute=True
            ):
        """
        Reads list of files installed by named asp.

        Destdir is not prependet to the list's items. Do it yourself if needed.
        """

        ret = 0

        asp_name1 = os.path.basename(asp_name)
        if asp_name != asp_name1:
            raise ValueError(
                "`asp_name' shuld be basename\n"
                "{}\n"
                " != \n"
                "{}".format(asp_name, asp_name1)
                )
        del asp_name1

        pkg_list_file = wayround_org.utils.path.abspath(
            wayround_org.utils.path.join(
                # self.basedir, # already added to self._installed_pkg_dir
                self._installed_pkg_dir,
                asp_name
                )
            )

        if not pkg_list_file.endswith('.xz'):
            pkg_list_file += '.xz'

        try:
            f = open(pkg_list_file, 'rb')
        except:
            logging.exception(
                "Can't open list file `{}'".format(pkg_list_file)
                )
            ret = 2
        else:

            pkg_file_list = wayround_org.utils.archive.xzcat(
                f,
                convert_to_str=True
                )

            f.close()

            pkg_file_list = pkg_file_list.splitlines()
            pkg_file_list = \
                wayround_org.utils.list.\
                filelist_strip_remove_empty_remove_duplicated_lines(
                    pkg_file_list
                    )

            pkg_file_list.sort()

            ret = pkg_file_list

        return ret

    def list_file_sums_installed_by_asp(
            self,
            asp_name,
            mute=True
            ):
        """
        Reads list of file checksums installed by named asp.

        Destdir is not prependet to the list's items. Do it yourself if needed.
        """

        ret = 0

        destdir = wayround_org.utils.path.abspath(self.basedir)

        list_dir = wayround_org.utils.path.abspath(
            self._installed_pkg_dir_sums
            )

        pkg_list_file = wayround_org.utils.path.join(list_dir, asp_name)

        if not pkg_list_file.endswith('.xz'):
            pkg_list_file += '.xz'

        try:
            f = open(pkg_list_file, 'rb')
        except:
            logging.warning("Can't open sum file: `{}'".format(pkg_list_file))
            ret = 2
        else:

            pkg_file_list = wayround_org.utils.archive.xzcat(
                f, convert_to_str=True
                )

            f.close()

            if not isinstance(pkg_file_list, str):
                pkg_file_list = str(pkg_file_list, 'utf-8')

            pkg_file_list = wayround_org.utils.checksum.parse_checksums_text(
                pkg_file_list
                )

            ret = pkg_file_list

        return ret

    def list_installed_packages_and_asps(self, host=None, arch=None):

        self._test_host_arch_parameters(host, arch)

        packages = self.list_installed_packages(
            mute=True,
            host=host,
            arch=arch
            )

        ret = self.list_installed_package_s_asps(
            packages,
            host=host,
            arch=arch
            )

        return ret

    def list_installed_asps_and_their_files(
            self,
            mute=True,
            host=None,
            arch=None
            ):
        """
        Returns dict with asp names as keys and list of files whey installs as
        contents
        """

        self._test_host_arch_parameters(host, arch)

        ret = dict()

        lst = self.list_installed_asps(
            mute=mute,
            host=host,
            arch=arch
            )

        lst_c = len(lst)

        lst_i = 0

        if not mute:
            logging.info("Loading file lists of all ASPs")

        for i in lst:
            ret[i] = self.list_files_installed_by_asp(
                i,
                mute=mute
                )

            lst_i += 1

            if not mute:
                wayround_org.utils.terminal.progress_write(
                    "    {} of {} ({:.2f}%)".format(
                        lst_i,
                        lst_c,
                        100.0 / (lst_c / lst_i)
                        )
                    )

        if not mute:
            wayround_org.utils.terminal.progress_write_finish()

        return ret

    def list_installed_asps_and_their_sums(
            self,
            mute=True,
            host=None,
            arch=None
            ):
        """
        Returns dict with asp names as keys and list of files whey installs as
        contents
        """

        self._test_host_arch_parameters(host, arch)

        ret = dict()

        lst = self.list_installed_asps(
            mute=mute,
            host=host,
            arch=arch
            )

        lst_c = len(lst)

        lst_i = 0

        if not mute:
            logging.info("Getting precalculated file check sums of all asps ")

        for i in lst:

            ret[i] = self.list_file_sums_installed_by_asp(i, mute)

            lst_i += 1

            if not mute:
                wayround_org.utils.terminal.progress_write(
                    "    {} of {} ({:.2f}%)".format(
                        lst_i,
                        lst_c,
                        100.0 / (lst_c / lst_i)
                        )
                    )

        if not mute:
            wayround_org.utils.terminal.progress_write_finish()

        return ret

    def latest_installed_package_s_asp(
            self,
            name,
            host=None,
            arch=None
            ):

        # TODO: attention to this function is required

        self._test_host_arch_parameters(host, arch)

        ret = None

        lst = self.list_installed_package_s_asps(
            name,
            host=host,
            arch=arch
            )

        if len(lst) > 0:
            latest = max(
                lst,
                key=functools.cmp_to_key(
                    wayround_org.aipsetup.version.package_version_comparator
                    )
                )

            ret = latest

        return ret

    def find_file_in_files_installed_by_asps(
            self,
            instr,
            mode=None,
            mute=False,
            sub_mute=True,
            predefined_asp_tree=None,
            host=None,
            arch=None
            ):
        """
        instr can be a single query or list of queries.

        :param mode: see in :func:`find_file_in_files_installed_by_asp`
        :param sub_mute: passed to :func:`find_file_in_files_installed_by_asp`

        :param predefined_asp_tree: if this parameter passed, use it instead
            of automatically creating it with
            list_installed_asps_and_their_files()
        """

        self._test_host_arch_parameters(host, arch)

        ret = dict()

        if predefined_asp_tree is None:
            predefined_asp_tree = \
                self.list_installed_asps_and_their_files(
                    mute=mute,
                    host=host,
                    arch=arch
                    )
        else:
            if not isinstance(predefined_asp_tree, dict):
                raise ValueError("`predefined_asp_tree' must be dict or None")

        lst = sorted(predefined_asp_tree.keys())

        lst_l = len(lst)
        lst_i = 0

        for pkgname in lst:

            if pkgname.endswith('.xz'):
                pkgname = pkgname[:-3]

            predefined_file_list = None
            if predefined_asp_tree:
                predefined_file_list = predefined_asp_tree[pkgname + '.xz']

            found = self.find_file_in_files_installed_by_asp(
                pkgname, instr=instr,
                mode=mode,
                mute=sub_mute,
                predefined_file_list=predefined_file_list
                )

            if len(found) != 0:
                ret[pkgname] = found

            if not mute:

                lst_i += 1

                perc = 0
                if lst_i == 0:
                    perc = 0.0
                else:
                    perc = 100.0 / (float(lst_l) / float(lst_i))

                wayround_org.utils.terminal.progress_write(
                    "    {:6.2f}% (found {} packages) ({})".format(
                        perc,
                        len(ret.keys()),
                        pkgname
                        )
                    )

        if not mute:
            wayround_org.utils.terminal.progress_write_finish()

        return ret

    def find_file_in_files_installed_by_asp(
            self,
            pkgname,
            instr,
            mode=None,
            mute=False,
            predefined_file_list=None
            ):
        """
        instr can be a single query or list of queries.

        ===== ======================================
        name  meaning
        ===== ======================================
        re    instr is or list of regular expresions
        plain instr is or list of plain texts
        sub   instr is or list of substrings
        beg   instr is or list of beginnings
        fm    instr is or list of file masks
        end   instr is or list of endings
        ===== ======================================

        :param instr: data which function must look for
        :param mode: mode inf which function must operate:
        :param predefined_file_list: use existing file list instead of
            creating own
        :param pkgname: take file list from this asp package
        """

        ret = 0

        if not isinstance(instr, list):
            instr = [instr]

        if mode is None:
            mode = 'sub'

        if not mode in ['re', 'plain', 'sub', 'beg', 'fm', 'end']:
            logging.error("wrong mode")
            ret = 1
        else:

            if not pkgname.endswith('.xz'):
                pkgname += '.xz'

            pkg_file_list = []
            if predefined_file_list:
                pkg_file_list = predefined_file_list
            else:
                pkg_file_list = self.list_files_installed_by_asp(
                    pkgname
                    )

            if not isinstance(pkg_file_list, list):
                logging.error("Can't get list of files")
                ret = 2
            else:

                pkg_file_list.sort()

                out_list = set()
                for i in pkg_file_list:
                    if mode == 're':
                        for j in instr:
                            if re.match(j, i) is not None:
                                out_list.add(i)

                    elif mode == 'plain':
                        for j in instr:
                            if j == i:
                                out_list.add(i)

                    elif mode == 'sub':
                        for j in instr:
                            if i.find(j) != -1:
                                out_list.add(i)

                    elif mode == 'beg':
                        for j in instr:
                            if i.startswith(j):
                                out_list.add(i)

                    elif mode == 'end':
                        for j in instr:
                            if i.endswith(j):
                                out_list.add(i)

                    elif mode == 'fm':
                        for j in instr:
                            if fnmatch.fnmatch(i, j):
                                out_list.add(i)

                out_list = sorted(out_list)

                ret = out_list

        return ret

    def make_asp_deps(self, asp_name, mute=True):
        """
        generates dependencies listing for named asp and places it under
        /destdir/var/log/packages/deps

        returns ``0`` if all okay
        """
        # TODO: is it deprecated method?
        # NOTE: added exception. if it not causes problems for long - remove
        #       this method (22 jun 2015)
        raise Exception("deprecated")
        ret = None

        destdir = wayround_org.utils.path.abspath(self.basedir)

        deps = self.get_asp_dependencies(asp_name, mute)

        deps_dir = self._installed_pkg_dir_deps

        file_name = wayround_org.utils.path.join(
            deps_dir, asp_name
            )

        if not file_name.endswith('.xz'):
            file_name += '.xz'

        if not os.path.isdir(deps_dir):

            os.makedirs(deps_dir)

        else:
            vf = io.BytesIO()

            try:
                vf.write(bytes(pprint.pformat(deps), 'utf-8'))
                vf.seek(0)
                f = open(file_name, 'wb')

                try:
                    ret = wayround_org.utils.archive.canonical_compressor(
                        'xz',
                        vf,
                        f,
                        verbose=False,
                        options=['-9'],
                        close_output_on_eof=False
                        )

                finally:
                    f.close()
            finally:
                vf.close()
                del vf

        return ret

    def load_asp_deps(self, asp_name, mute=True):
        """
        Result: dict. keys - file paths; values - lists of file basenames
        """

        ret = None

        destdir = wayround_org.utils.path.abspath(self.basedir)

        dire = self._installed_pkg_dir_deps

        file_name = wayround_org.utils.path.join(
            dire, asp_name
            )

        if not file_name.endswith('.xz'):
            file_name += '.xz'

        if not os.path.isfile(file_name):
            if not mute:
                logging.error("File not found: {}".format(file_name))
            ret = 1
        else:
            f = open(file_name, 'rb')
            try:
                txt = wayround_org.utils.archive.xzcat(f, convert_to_str=True)
            except:
                raise
            else:
                try:
                    # TODO: eval usage is incorrect
                    ret = eval(txt, {}, {})
                except:
                    ret = None

            finally:
                f.close()

        return ret

    def find_old_packages(
            self,
            age=2592000,
            mute=True,
            host=None,
            arch=None
            ):

        # 2592000 = (60 * 60 * 24 * 30)  # 30 days

        self._test_host_arch_parameters(host, arch)

        ret = []

        asps = self.list_installed_asps(
            mute=mute,
            host=host,
            arch=arch
            )

        for i in asps:

            parsed_name = \
                wayround_org.aipsetup.package_name_parser.package_name_parse(
                    i
                    )

            if not parsed_name:
                logging.warning("Can't parse package name `{}'".format(i))
            else:

                package_date = \
                    wayround_org.aipsetup.package_name_parser.parse_timestamp(
                        parsed_name['groups']['timestamp']
                        )

                if not package_date:
                    logging.error(
                        "Can't parse timestamp {} in {}".format(
                            parsed_name['groups']['timestamp'],
                            i
                            )
                        )
                else:

                    if (datetime.datetime.now() - package_date
                            > datetime.timedelta(seconds=age)):

                        ret.append(i)

        return ret

    def check_list_of_installed_packages_and_asps_auto(
            self,
            host=None,
            arch=None
            ):

        self._test_host_arch_parameters(host, arch)

        content = self.list_installed_packages_and_asps(
            host=host,
            arch=arch
            )

        ret = self.check_list_of_installed_packages_and_asps(
            content,
            host=host,
            arch=arch
            )

        return ret

    def check_list_of_installed_packages_and_asps(
            self,
            in_dict,
            host=None,
            arch=None
            ):

        self._test_host_arch_parameters(host, arch)

        ret = 0

        keys = sorted(in_dict.keys())

        errors = 0

        for i in keys:

            if len(in_dict[i]) > 1:

                errors += 1
                ret = 1

                logging.warning(
                    "Package with too many ASPs found `{}'".format(i)
                    )

                in_dict[i].sort()

                for j in in_dict[i]:

                    print("       {}".format(j))

        if errors > 0:
            logging.warning("Total erroneous packages: {}".format(errors))

        return ret

    def check_elfs_readiness(self, mute=False, host=None, arch=None):

        self._test_host_arch_parameters(host, arch)

        paths = self.elf_paths(
            host=host,
            arch=arch
            )
        elfs = find_all_elf_files(
            paths,
            verbose=True,
            host=host,
            arch=arch
            )

        elfs = sorted(wayround_org.utils.path.realpaths(elfs))

        elfs_c = len(elfs)
        elfs_i = 0

        for i in elfs:
            elfs_i += 1

            if not mute:
                logging.info(
                    "({} of {}) Trying to read file {}".format(
                        elfs_i, elfs_c, i
                        )
                    )

            wayround_org.utils.format.elf.ELF(i)

        return 0

    def load_asp_deps_all(self, mute=True, host=None, arch=None):
        """
        Returns dict: keys - asp names; values - dicts returned by
                      load_asp_deps()
        """

        self._test_host_arch_parameters(host, arch)

        ret = {}

        installed_asp_names = self.list_installed_asps(
            mute=mute,
            host=host,
            arch=arch
            )

        for i in installed_asp_names:

            asp_name = i
            if asp_name.endswith('.asp'):
                asp_name = asp_name[':-4']

            res = self.load_asp_deps(
                asp_name=asp_name,
                mute=mute
                )

            if isinstance(res, dict):
                ret[asp_name] = res
            else:
                logging.error(
                    "Error loading deps list for: {}".format(asp_name)
                    )

        return ret

    def get_asps_depending_on_asp(
            self,
            asp_name,
            mute=False,
            host=None,
            arch=None
            ):

        ret = 0

        destdir = wayround_org.utils.path.abspath(self.basedir)

        print("host: {}, arch: {}".format(host, arch))

        asp_name_latest = None

        package_name_parsed = \
            wayround_org.aipsetup.package_name_parser.package_name_parse(
                asp_name
                )
        package_name = None

        if not isinstance(package_name_parsed, dict):
            if not mute:
                logging.error("Can't parse package name {}".format(asp_name))

            ret = 0
        else:
            package_name = package_name_parsed['groups']['name']

            if not mute:
                logging.info(
                    "Looking for latest installed asp of package {}".format(
                        package_name
                        )
                    )

            asp_name_latest = (
                self.latest_installed_package_s_asp(
                    package_name,
                    host=host,
                    arch=arch
                    )
                )

            if not mute:
                logging.info("Latest asp is {}".format(asp_name_latest))

            asp_name_latest_files = []

            if asp_name_latest:

                if asp_name_latest == asp_name:
                    if not mute:
                        logging.info("Selected asp is latest")
                else:

                    if not mute:
                        logging.info("Loading it's file list")

                    asp_name_latest_files = (
                        self.list_files_installed_by_asp(
                            asp_name_latest
                            )
                        )

                    asp_name_latest_files = \
                        wayround_org.utils.path.prepend_path(
                            asp_name_latest_files, destdir
                            )

                    asp_name_latest_files = wayround_org.utils.path.realpaths(
                        asp_name_latest_files
                        )

                    asp_name_latest_files2 = []
                    for i in asp_name_latest_files:
                        if os.path.isfile(i):
                            asp_name_latest_files2.append(i)

                    asp_name_latest_files = asp_name_latest_files2

                    del(asp_name_latest_files2)

                    asp_name_latest_files2 = []

                    for i in range(len(asp_name_latest_files)):

                        e = wayround_org.utils.format.elf.ELF(
                            asp_name_latest_files[i]
                            )
                        if e.is_elf:
                            asp_name_latest_files2.append(
                                asp_name_latest_files[i]
                                )

                    asp_name_latest_files = asp_name_latest_files2

                    del(asp_name_latest_files2)

            if not mute:
                logging.info("Loading file list of {}".format(asp_name))

            asp_name_files = (
                self.list_files_installed_by_asp(
                    asp_name, mute=mute
                    )
                )

            asp_name_files = wayround_org.utils.path.prepend_path(
                asp_name_files, destdir
                )

            asp_name_files = wayround_org.utils.path.realpaths(
                asp_name_files
                )

            asp_name_files2 = []
            for i in asp_name_files:
                if os.path.isfile(i):
                    asp_name_files2.append(i)

            asp_name_files = asp_name_files2

            del(asp_name_files2)

            asp_name_files2 = []

            for i in range(len(asp_name_files)):

                e = wayround_org.utils.format.elf.ELF(asp_name_files[i])
                if e.is_elf:
                    asp_name_files2.append(asp_name_files[i])

            asp_name_files = asp_name_files2

            del(asp_name_files2)

            if len(asp_name_latest_files) != 0:
                if not mute:
                    logging.info(
                        "Excluding latest asp files from selected asp files"
                        )

                asp_name_files = list(
                    set(asp_name_files) - set(asp_name_latest_files)
                    )

            if not mute:
                logging.info("Getting list of all asps installed in system")

            installed_asp_names = self.list_installed_asps(
                mute=mute,
                host=host,
                arch=arch
                )

            deps_list = dict()

            if not mute:
                logging.info("setting list of asps depending on asp")

            installed_asp_names_c = len(installed_asp_names)
            installed_asp_names_i = 0

            last_found = None

            for i in set(installed_asp_names):

                if not i in deps_list:

                    files_list = (
                        self.list_files_installed_by_asp(
                            i,
                            mute=True
                            )
                        )

                    files_list = wayround_org.utils.path.prepend_path(
                        files_list,
                        destdir
                        )

                    files_list = wayround_org.utils.path.realpaths(
                        files_list
                        )

                    files_list2 = []
                    for files_list_item in files_list:
                        if os.path.isfile(files_list_item):
                            files_list2.append(files_list_item)

                    files_list = files_list2

                    del(files_list2)

                    files_list = \
                        list(set(files_list) - set(asp_name_latest_files))

                    i_deps = self.get_asp_dependencies(
                        i,
                        mute=True,
                        predefined_asp_name_files=files_list
                        )

                    if not isinstance(i_deps, dict):
                        if not mute:
                            logging.error(
                                "Couldn't get {} dependencies".format(
                                    i
                                    )
                                )
                        ret = 1
                    else:
                        for j in i_deps:

                            for k in asp_name_files:
                                if k.endswith(j):
                                    if not i in deps_list:
                                        deps_list[i] = set()

                                    deps_list[i].add(k)
                                    last_found = \
                                        "{} (depends on file {})".format(
                                            i,
                                            os.path.basename(k)
                                            )

                if ret != 0:
                    break

                installed_asp_names_i += 1

                if not mute:
                    wayround_org.utils.terminal.progress_write(
                        "    {} of {} ({:.2f}%) "
                        "found: {}; last found: {}".format(
                            installed_asp_names_i,
                            installed_asp_names_c,
                            100.0 / (
                                installed_asp_names_c / installed_asp_names_i
                                ),
                            len(deps_list),
                            last_found
                            )
                        )

            if not mute:
                print('')

            if ret == 0:
                ret = deps_list

        return ret

    def get_asps_asp_depends_on(
            self,
            asp_name,
            mute=False,
            host=None,
            arch=None
            ):
        """
        Returns list on success
        """
        # TODO: optimizations required

        self._test_host_arch_parameters(host, arch)

        ret = 0

        elfs_installed_by_asp_name_deps = self.get_asp_dependencies(
            asp_name,
            mute=mute
            )

        if not isinstance(elfs_installed_by_asp_name_deps, dict):
            if not mute:
                logging.error(
                    "Couldn't get {} dependencies".format(
                        asp_name
                        )
                    )
            ret = 1

        else:

            if not mute:
                logging.info("summarizing elf deps")

            all_deps = set()

            for i in set(elfs_installed_by_asp_name_deps.keys()):
                all_deps |= set(elfs_installed_by_asp_name_deps[i])

            if not mute:
                logging.info("Getting list of files installed by all asps")

            all_asps_and_files = (
                self.list_installed_asps_and_their_files(
                    mute=mute,
                    host=host,
                    arch=arch
                    )
                )

            required_asps = set()

            if not mute:
                logging.info("setting list of required asps. final action.")

            for i in set(all_asps_and_files.keys()):

                for j in all_asps_and_files[i]:

                    for k in all_deps:

                        if j.endswith(k):
                            required_asps.add(i)

            ret = list(required_asps)

        return ret

    def get_asp_dependencies(
            self,
            asp_name,
            mute=False,
            predefined_asp_name_files=None,
            force=False
            ):
        """
        Build dependency list for each elf in asp

        On success returns ``dict``, in which each key is file name not
        prepended with destdir
        """

        ret = 0

        destdir = wayround_org.utils.path.abspath(self.basedir)

        if not force:
            ret = self.load_asp_deps(asp_name, mute)

        if not isinstance(ret, dict):

            if not mute:
                logging.warning(
                    "asp requiring deps list regeneration: {}".format(asp_name)
                    )

            ret = 0

            if not mute:
                logging.info(
                    "Getting list of files installed by {}".format(asp_name)
                    )

            asp_name_files = list()
            if predefined_asp_name_files:
                asp_name_files = list(predefined_asp_name_files)
            else:
                asp_name_files = (
                    self.list_files_installed_by_asp(
                        asp_name,
                        mute=mute
                        )
                    )

                if not isinstance(asp_name_files, list):
                    if not mute:
                        logging.error(
                            "Can't get list of files installed by {}".format(
                                asp_name
                                )
                            )
                    ret = 1
                else:

                    asp_name_files = wayround_org.utils.path.prepend_path(
                        asp_name_files,
                        destdir
                        )

                    asp_name_files = wayround_org.utils.path.realpaths(
                        asp_name_files
                        )

                    asp_name_files2 = []
                    for i in asp_name_files:
                        if os.path.isfile(i):
                            asp_name_files2.append(i)

                    asp_name_files = asp_name_files2

                    del(asp_name_files2)

            if not isinstance(asp_name_files, list):
                if not mute:
                    logging.error(
                        "Can't get list of files installed by {}".format(
                            asp_name
                            )
                        )
                ret = 1
            else:

                if not mute:
                    logging.info("{} files".format(len(asp_name_files)))

                if not mute:
                    logging.info(
                        "getting list of elf files from files installed by asp"
                        )

                asp_name_elfs = set()
                for i in asp_name_files:

                    e = wayround_org.utils.format.elf.ELF(i)
                    if e.is_elf:
                        asp_name_elfs.add(os.path.realpath(i))

                asp_name_elf_deps = {}

                if not mute:
                    logging.info("getting elf deps")

                for i in asp_name_elfs:

                    i_normal = i

                    if i_normal.startswith(destdir):
                        i_normal = i_normal[len(destdir):]

                        if not i_normal.startswith(os.path.sep):
                            i_normal = os.path.sep + i_normal

                    if not i_normal in asp_name_elf_deps:
                        asp_name_elf_deps[i_normal] = set()

                    e = wayround_org.utils.format.elf.ELF(i_normal)
                    i_libs_list = e.needed_libs_list

                    if isinstance(i_libs_list, (list, set)):
                        asp_name_elf_deps[i_normal] |= set(
                            i_libs_list
                            )

                for i in list(asp_name_elf_deps.keys()):
                    asp_name_elf_deps[i] = list(asp_name_elf_deps[i])

                ret = asp_name_elf_deps

        return ret

    def find_system_garbage(
            self,
            prepared_all_files=None,
            mute=True,
            only_lib=False,
            host=None,
            arch=None
            ):
        """
        Searches files not installed by any of ASPs in system

        If prepared_all_files == None, then
        prepared_all_files = self.list_installed_asps_and_their_files()

        Dirs excluded from search are:
        /boot, /etc, /var, /run, /proc, /sys, /home, /root, /tmp

        only_lib - search only for library garbage (/multiarch/*/lib*)
        """

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        self._test_host_arch_parameters(host, arch)

        if not mute:
            if self.basedir != '/':
                logging.info("Working with base dir: {}".format(self.basedir))

        if prepared_all_files is None:
            prepared_all_files = self.list_installed_asps_and_their_files(
                mute=mute,
                host=host,
                arch=arch
                )

        lst = []

        if not only_lib:

            lst = wayround_org.utils.file.files_recurcive_list(
                self.basedir,
                exclude_paths=LOCAL_DIRS,
                mute=mute,
                sort=True
                )

        else:

            # TODO: /usr/lib must be calculated, - not constant

            lst = wayround_org.utils.file.files_recurcive_list(
                wayround_org.utils.path.join(
                    self.basedir,
                    'multihost',
                    host,
                    'lib'
                    ),
                mute=mute,
                sort=True,
                maxdepth=1
                )

            lst2 = wayround_org.utils.file.files_recurcive_list(
                wayround_org.utils.path.join(
                    self.basedir,
                    'multihost',
                    host,
                    'lib64'
                    ),
                mute=mute,
                sort=True,
                maxdepth=1
                )

            if isinstance(lst2, list):
                lst += lst2
            del lst2

        lst = sorted(
            wayround_org.utils.path.unprepend_path(
                lst,
                self.basedir
                )
            )

        result = []

        if not mute:
            logging.info("Generating list of not installed files")

        ii = 0
        len_list = len(lst)
        lf = None
        size = 0
        s = 0
        for i in range(len_list):

            lst_i = lst[i]

            found = False

            for j in list(prepared_all_files.keys()):

                if lst_i in prepared_all_files[j]:
                    found = True
                    break

            if not found:
                result.append(lst_i)

                fsn = wayround_org.utils.path.join(self.basedir, lst_i)

                if (os.path.isfile(fsn) and
                        not os.path.islink(fsn) and
                        fsn == wayround_org.utils.path.realpath(fsn)):
                    fs = os.stat(fsn)

                    size += fs.st_size

                    if size != 0:
                        s = '{:.3f}'.format(size / 1024 / 1024)

                lf = lst_i

                wayround_org.utils.terminal.progress_write(
                    "    found: {}".format(lf),
                    new_line=True
                    )
            ii += 1

            wayround_org.utils.terminal.progress_write(
                "    {} of {} ({:.2f}%) found:"
                " {} size: {} MiB position: {}".format(
                    ii,
                    len_list,
                    100 / (float(len_list) / ii),
                    len(result),
                    s,
                    lst_i
                    )
                )

        wayround_org.utils.terminal.progress_write_finish()

        ret = result

        return ret

    def find_so_problems_in_system(
            self,
            verbose=False,
            host=None,
            arch=None
            ):
        """
        Look for dependency problems in current system
        """

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        if not isinstance(arch, str):
            raise TypeError("`arch' must be str")

        so_files, elf_files = self.find_system_so_and_elf_files(
            verbose,
            host=host,
            arch=arch
            )

        reqs = find_so_problems_by_given_so_and_elfs(
            so_files,
            elf_files,
            verbose
            )

        return reqs

    def build_dependency_tree(self, verbose=False, host=None, arch=None):
        """
        Look for dependency problems in current system
        """

        # TODO: rework to help text required

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        if not isinstance(arch, str):
            raise TypeError("`arch' must be str")

        elf_files = self.find_system_elf_files(
            verbose=verbose,
            host=host,
            arch=arch
            )

        reqs = build_binary_dependency_tree_for_given_elf_files(
            elf_files,
            verbose
            )

        return reqs

    def library_paths(self, host=None):
        """
        arch - parameter currently ignored
        """

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        ret = []

        ret.append(
            wayround_org.utils.path.join('/multihost', host, 'lib')
            )
        ret.append(
            wayround_org.utils.path.join('/multihost', host, 'lib64'))

        ret = wayround_org.utils.path.prepend_path(ret, self.basedir)
        ret = wayround_org.utils.path.realpaths(ret)
        ret = list(set(ret))

        return ret

    def elf_paths(self, host=None, arch=None):

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        if not isinstance(arch, str):
            raise TypeError("`arch' must be str")

        ret = []

        ret.append(
            wayround_org.utils.path.join(
                '/multihost',
                host,
                'multiarch',
                arch,
                'bin'
                )
            )

        ret.append(
            wayround_org.utils.path.join(
                '/multihost',
                host,
                'multiarch',
                arch,
                'sbin'
                )
            )

        ret += self.library_paths(host=host)

        ret = wayround_org.utils.path.prepend_path(ret, self.basedir)
        ret = wayround_org.utils.path.realpaths(ret)
        ret = list(set(ret))

        return ret

    def find_system_so_and_elf_files(
            self,
            verbose=False,
            host=None,
            arch=None
            ):
        """
        Find All system Shared Object Files and all ELF files real paths.
        """

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        if not isinstance(arch, str):
            raise TypeError("`arch' must be str")

        so_files = self.find_system_so_files(
            verbose=verbose,
            host=host
            )

        elf_files = self.find_system_elf_files(
            verbose=verbose,
            host=host,
            arch=arch
            )

        return (so_files, elf_files)

    def find_system_so_files(self, verbose=False, host=None):

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        paths = self.library_paths(host=host)
        if verbose:
            logging.info("Searching so files in paths: {}".format(paths))

        return find_all_so_files(paths, verbose=verbose)

    def find_system_elf_files(self, verbose=False, host=None, arch=None):

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        if not isinstance(arch, str):
            raise TypeError("`arch' must be str")

        paths = self.elf_paths(
            host=host,
            arch=arch
            )
        if verbose:
            logging.info("Searching elf files in paths: {}".format(paths))

        return find_all_elf_files(paths, verbose=verbose)

    def create_directory_tree(self):

        ret = 0

        for i in [
                '/boot',
                '/daemons',
                '/dev',
                '/etc',
                '/home',
                '/media',
                '/multihost',
                '/mnt',
                '/opt',
                '/proc',
                '/root',
                '/run',
                '/sys',
                '/tmp',
                '/var/mail'
                ]:

            joined = wayround_org.utils.path.join(self.basedir, i)

            if not os.path.isdir(joined):
                print("creating: {}".format(joined))
                os.makedirs(joined, exist_ok=True)

        for i in [
                self._installed_pkg_dir,
                self._installed_pkg_dir_buildlogs,
                self._installed_pkg_dir_sums,
                self._installed_pkg_dir_deps
                ]:

            joined = wayround_org.utils.path.join(i)

            if not os.path.isdir(joined):
                print("creating: {}".format(joined))
                os.makedirs(joined, exist_ok=True)

        for i in [
                'bin', 'sbin', 'lib', 'lib64'
                ]:

            joined = wayround_org.utils.path.join(self.basedir, i)

            if not os.path.exists(joined) and not os.path.islink(joined):

                try:
                    # not error: not 'multihost' - 'usr'
                    os.symlink('usr/{}'.format(i), joined)
                except:
                    logging.exception(
                        "Can't create link usr/{} -- continuing".format(joined)
                        )
                    ret = 1

        jusr = wayround_org.utils.path.join(self.basedir, 'usr')
        if not os.path.exists(jusr) and not os.path.islink(jusr):
            try:
                os.symlink('multihost/_primary', jusr)
            except:
                logging.exception("Can't create link /usr -- continuing")
                ret = 1

        for i in ['x86_64-pc-linux-gnu']:

            host_dir = wayround_org.utils.path.join(
                self.basedir,
                'multihost',
                i
                )

            usr_link_name = wayround_org.utils.path.join(
                host_dir,
                'usr'
                )

            multihost_link_name = wayround_org.utils.path.join(
                host_dir,
                'multihost'
                )

            os.symlink('.', usr_link_name)
            os.symlink('/multihost', multihost_link_name)

        return ret

    def gen_locale(self, host=None):

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        ret = 0

        for i in [
                wayround_org.utils.path.join(
                    self.basedir,
                    'multihost',
                    host,
                    'lib'
                    ),
                wayround_org.utils.path.join(
                    self.basedir,
                    'multihost',
                    host,
                    'lib64'
                    ),
                ]:

            target_dir = wayround_org.utils.path.join(
                i,
                'locale'
                )

            os.makedirs(target_dir, exist_ok=True)

            if os.path.isdir(target_dir):

                locale_dir = wayround_org.utils.path.join(
                    target_dir, 'en_US.UTF-8'
                    )

                rel_locale_dir = wayround_org.utils.path.relpath(
                    locale_dir, self.basedir
                    )

                if os.path.exists(locale_dir):
                    shutil.rmtree(locale_dir)

                logging.info(
                    "creating locale for dir: {}".format(
                        target_dir
                        )
                    )
                cmd = ['chroot', self.basedir,

                       'localedef',
                       '-f', 'UTF-8',
                       '-i', 'en_US',
                       rel_locale_dir
                       ]
                logging.info(
                    " command: {}".format(
                        ' '.join(cmd)
                        )
                    )

                p = subprocess.Popen(
                    cmd
                    )

                ret = p.wait()

        return ret

    def find_asps_requireing_sos_not_installed_by_asps(
            self,
            mute=True,
            host=None,
            arch=None
            ):
        """
        Return: dict. keys - asp names; values - lists of tuples
        """

        self._test_host_arch_parameters(host, arch)

        all_deps = self.load_asp_deps_all(
            mute=mute,
            host=host
            )

        all_installed_files = self.list_installed_asps_and_their_files(
            mute=mute,
            host=host
            )

        logging.info("Compacting for greater performance..")
        all_installed_files2 = dict()

        for i in all_installed_files.keys():
            all_installed_files2[i] = \
                wayround_org.utils.path.bases(all_installed_files[i])

        all_installed_files = all_installed_files2

        del all_installed_files2
        logging.info("Ready")
        logging.info("Searching..")

        ret = {}

        all_deps_keys = list(all_deps.keys())
        all_deps_keys_l = len(all_deps_keys)
        i = 0

        for ad_aspname in all_deps_keys:

            for ad_aspname_elf_name in all_deps[ad_aspname].keys():

                for ad_aspname_elf_name_depname \
                        in all_deps[ad_aspname][ad_aspname_elf_name]:

                    found = False

                    for aif_asp_name in all_installed_files.keys():

                        if ad_aspname_elf_name_depname \
                                in all_installed_files[aif_asp_name]:

                            found = True
                            break

                    if not found:

                        if not ad_aspname in ret:
                            ret[ad_aspname] = []

                        lst2 = ret[ad_aspname]

                        x = (ad_aspname_elf_name,
                             ad_aspname_elf_name_depname)

                        lst2.append(x)
                        if not mute:
                            wayround_org.utils.terminal.progress_write(
                                "Added: {}\n".format(x)
                                )
                            wayround_org.utils.terminal.progress_write(
                                "Searching.. {} of {} ({:5.2f}% ready)".format(
                                    i,
                                    all_deps_keys_l,
                                    100.0 / (all_deps_keys_l / i)
                                    )
                                )

            i += 1
            if not mute:
                wayround_org.utils.terminal.progress_write(
                    "Searching.. {} of {} ({:5.2f}% ready)".format(
                        i,
                        all_deps_keys_l,
                        100.0 / (all_deps_keys_l / i)
                        )
                    )

        if not mute:
            wayround_org.utils.terminal.progress_write_finish()

        return ret

    def find_libtool_la_with_problems(
            self,
            mute=True,
            host=None
            ):

        # NOTE: here is no arch parameter. it's not needed here

        # FIXME: attention to paths required

        if not isinstance(host, str):
            raise TypeError("`host' must be str")

        la_with_problems = dict()

        mask = wayround_org.utils.path.join(
            self.basedir,
            'multihost',
            host,
            'lib*',
            '*.la'
            )

        if not mute:
            logging.info("Looking for `{}'".format(mask))

        la_files = glob.glob(mask)
        la_files_len = len(la_files)

        if not mute:
            logging.info("    found {} file(s)".format(la_files_len))

        if not mute:
            logging.info("Analising..")

        la_files_len_i = 0

        for i in la_files:

            if not i in la_with_problems:
                la_with_problems[i] = dict(
                    so=set(),
                    la=set(),
                    dir=list(),
                    read_error=False
                    )

            p = subprocess.Popen(
                [
                    'bash',
                    '-c',
                    '. {} ; echo $dependency_libs'.format(shlex.quote(i))
                    ],
                stdout=subprocess.PIPE
                )

            if p.wait() != 0:
                la_with_problems[i]['read_error'] = True

            else:

                res = str(p.communicate()[0], 'utf-8').splitlines()[0]

                sp_res = shlex.split(res)

                search_dirs = set(
                    [
                        wayround_org.utils.path.join(
                            '/multihost', host, 'lib'
                            ),
                        wayround_org.utils.path.join(
                            '/multihost', host, 'lib64'
                            ),
                        ]
                    )

                for j in sp_res:

                    # dir_ = la_with_problems[i]['dir']

                    if j.startswith('-L'):

                        wj = j[2:]

                        if (not wj.startswith(
                                wayround_org.utils.path.join(
                                    '/multihost', host, 'lib'
                                    )
                                )
                                or not os.path.isdir(
                                wayround_org.utils.path.join(
                                    self.basedir,
                                    wj)
                                )
                                ):

                            # TODO: do we need it?
                            # NOTE: possible some strange results.
                            #       for some reasons .la files can contain
                            #       paths to directories in whiche they were
                            #       built
                            # dir_.append(wj)

                            pass

                        else:

                            search_dirs.add(wj)

                for j in sp_res:

                    so = la_with_problems[i]['so']
                    la = la_with_problems[i]['la']

                    if j.startswith('-l'):

                        wj = j[2:]

                        found = False

                        for k in search_dirs:

                            for l in ['so', 'a']:
                                if os.path.isfile(
                                        wayround_org.utils.path.join(
                                            self.basedir,
                                            k,
                                            'lib{}.{}'.format(wj, l)
                                            )
                                        ):

                                    found = True
                                    break

                            if found:
                                break

                        if not found:
                            so.add(wj)

                    elif j.endswith('.la'):

                        if not os.path.isfile(
                                wayround_org.utils.path.join(self.basedir, j)
                                ):
                            la.add(j)

                    else:
                        Exception("Unknown case")

            if (len(la_with_problems[i]['so']) == 0
                    and len(la_with_problems[i]['la']) == 0
                    and len(la_with_problems[i]['dir']) == 0
                    and la_with_problems[i]['read_error'] == False):
                del la_with_problems[i]

            la_files_len_i += 1
            if not mute:
                wayround_org.utils.terminal.progress_write(
                    '    {} of {} ({:5.2f}%)'.format(
                        la_files_len_i,
                        la_files_len,
                        100 / (la_files_len / la_files_len_i)
                        )
                    )

        if not mute:
            wayround_org.utils.terminal.progress_write_finish()

        return la_with_problems


def find_all_so_files(paths, verbose=False):
    """
    Get all shared object files in named dirs (real paths returned)
    """

    so_files = []

    for i in paths:
        so_files += find_so_files(i, verbose)

    so_files = wayround_org.utils.path.realpaths(so_files)

    so_files = list(set(so_files))

    return so_files


def find_so_files(directory, verbose=False):
    """
    Get all shared object files in named dir (real paths returned)
    """

    ret = set()

    if not os.path.isdir(directory):
        logging.error("Directory not exists `{}'".format(directory))
        ret = set()
    else:

        files = os.listdir(directory)

        files = wayround_org.utils.path.prepend_path(files, directory)
        files = wayround_org.utils.path.realpaths(files)
        files = filter_so_files(files, verbose=verbose)
        ret = files

    if verbose:
        wayround_org.utils.terminal.progress_write_finish()

    ret = list(ret)

    return ret


def find_all_elf_files(paths, verbose=False):
    """
    Get all elf files in named dirs (real paths returned)
    """

    elf_files = []

    for i in paths:
        elf_files += find_elf_files(i, verbose)

    elf_files = wayround_org.utils.path.realpaths(elf_files)

    elf_files = list(set(elf_files))

    return elf_files


def find_elf_files(directory, verbose=False):
    """
    Get all elf files in named dir (real paths returned)
    """

    ret = set()

    if not os.path.isdir(directory):
        logging.error("Directory not exists `{}'".format(directory))
        ret = set()
    else:

        files = os.listdir(directory)

        files = wayround_org.utils.path.prepend_path(files, directory)
        files = wayround_org.utils.path.realpaths(files)
        files = filter_elf_files(files, verbose=verbose)
        ret = files

    if verbose:
        wayround_org.utils.terminal.progress_write_finish()

    ret = list(ret)

    return ret


def filter_so_files(files, verbose=False):
    """
    Filter shared object (.so) files

    Accepts list of file names. Retrns list of files, each of which has
    basenames contains '.so', can be readen/parsed as ELF file and is of type
    'ET_DYN'.

    Resulted file list lines is returned in same order, in same formats, but
    without filtered out incorrect lines.
    """

    ret = set()

    files_c = len(files)

    count = 0
    sos = 0

    for i in files:

        if os.path.isfile(i):
            if os.path.basename(i).find('.so') != -1:
                elf = wayround_org.utils.format.elf.ELF(i)
                if (
                        elf.is_elf
                        and elf.elf_type_name == 'ET_DYN'
                        ):
                    ret.add(i)
                    sos += 1

        count += 1

        if verbose:
            wayround_org.utils.terminal.progress_write(
                "Looking for .so files: {} of {} files (sos: {})".format(
                    count,
                    files_c,
                    sos
                    )
                )

    return list(ret)


def filter_elf_files(files, verbose=False):
    """
    Filter ELF files

    Accepts list of file names. Retrns list of files, each of which can be
    readen/parsed as ELF file and is of type.

    Resulted file list lines is returned in same order, in same formats, but
    without filtered out incorrect lines.
    """

    ret = set()

    files_c = len(files)

    count = 0
    elfs = 0

    for i in files:

        if os.path.isfile(i):
            elf = wayround_org.utils.format.elf.ELF(i)

            if elf.is_elf:
                ret.add(i)
                elfs += 1

        count += 1

        if verbose:
            wayround_org.utils.terminal.progress_write(
                "Looking for elf files: {} of {} files (elfs: {})".format(
                    count,
                    files_c,
                    elfs
                    )
                )

    return list(ret)


def build_binary_dependency_tree_for_given_elf_files(
        elf_files, verbose=False
        ):
    """
    Build dependency tree by given so and elf lists
    """

    # TODO: complete this function

    if not isinstance(elf_files, list):
        raise TypeError("elf_files must be list")

    if verbose:
        elf_files.sort()

    if verbose:
        logging.info("Building dependency tree")

    deps = {}

    elf_files_c = len(elf_files)
    elf_files_i = 0

    for i in elf_files:

        e = wayround_org.utils.format.elf.ELF(i)

        libs_elf_linked_to = e.needed_libs_list

        if not isinstance(libs_elf_linked_to, list):
            logging.error(
                "Can't get dependency list for file: `{}'".format(i)
                )
        else:
            if not i in deps:
                deps[i] = list()
            deps[i] = libs_elf_linked_to

        elf_files_i += 1

        if verbose:
            wayround_org.utils.terminal.progress_write(
                "Progress: {} ELF files of {}".format(
                    elf_files_i,
                    elf_files_c
                    )
                )

    if verbose:
        wayround_org.utils.terminal.progress_write_finish()

    return deps


def find_so_problems_by_given_so_and_elfs(
        so_files, elf_files, verbose=False
        ):
    """
    Look for dependency problems in current system.

    This function works with basenames of so_files and with elf_files lines,
    which points on files which can be parsed as ELFs.

    returns dict with keys pointing on the ELFs and lists of missing .so files
    in them.
    """

    if not isinstance(so_files, list):
        raise TypeError("so_files must be list")

    if not isinstance(elf_files, list):
        raise TypeError("elf_files must be list")

    so_files = wayround_org.utils.path.bases(so_files)

    if verbose:
        so_files.sort()
        elf_files.sort()

    if verbose:
        logging.info("Looking for problems")

    reqs = {}

    elf_files_c = len(elf_files)
    elf_files_i = 0

    for i in elf_files:

        e = wayround_org.utils.format.elf.ELF(i)

        libs_elf_linked_to = e.needed_libs_list

        if not isinstance(libs_elf_linked_to, list):
            logging.error(
                "Can't get libs_elf_linked_to list for file: `{}'".format(i)
                )
        else:
            for j in libs_elf_linked_to:
                if not j in so_files:
                    if not j in reqs:
                        reqs[j] = list()
                    reqs[j].append(i)

        elf_files_i += 1

        if verbose:
            wayround_org.utils.terminal.progress_write(
                "Checked dependencies: {} of {} ({} missing found)".format(
                    elf_files_i,
                    elf_files_c,
                    len(reqs.keys())
                    )
                )

    if verbose:
        wayround_org.utils.terminal.progress_write_finish()
        logging.info("Libraries missing: {}".format(len(reqs.keys())))

    return reqs


def convert_certdata_txt_for_system(filename):
    output = []
    res = certdata.certdata.read_certdata_txt(filename)
    handy = certdata.certdata.handy_conversions(res)

    for i in handy:

        res = None
        pr = None
        if 'CKA_VALUE' in i:
            p = subprocess.Popen(
                ['openssl', 'x509', '-inform', 'DER', '-text', '-fingerprint'],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL
            )

            res = p.communicate(i['CKA_VALUE'])[0]
            pr = p.returncode

        if pr == 0:
            output.append(res)

    return b'\n\n'.join(output)
