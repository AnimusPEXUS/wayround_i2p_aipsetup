
"""
Module for initiating building site

Later is required for farther package building.
"""

import os
import logging
import shutil
import json

import org.wayround.utils.path
import org.wayround.utils.tarball_name_parser


DIR_TARBALL = '00.TARBALL'
"""
Directory for storing tarballs used in package building. contents is packed into
resulting package as it is requirements of most good licenses
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
        '/bin', '/boot' , '/daemons',
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

APPLY_DESCR = """\

    It is typically used in conjunction with functions
    :func:`apply_constitution_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`
    in  this order by function :func:`apply_info`
"""

class BuildingSite:

    def __init__(self, path):
        self.path = org.wayround.utils.path.abspath(path)

    def _getDIR_x(self, _x='TARBALL'):
        '''
        Returns absolute path to DIR_{_x}

        note: this method is generated dinamicly
        '''

        ret = org.wayround.utils.path.abspath(
            os.path.join(
                self.path,
                eval('DIR_{}'.format(_x)))
            )

        return ret


    def getDIR_TARBALL   (self): return self._getDIR_x('TARBALL')
    def getDIR_SOURCE    (self): return self._getDIR_x('SOURCE')
    def getDIR_PATCHES   (self): return self._getDIR_x('PATCHES')
    def getDIR_BUILDING  (self): return self._getDIR_x('BUILDING')
    def getDIR_DESTDIR   (self): return self._getDIR_x('DESTDIR')
    def getDIR_BUILD_LOGS(self): return self._getDIR_x('BUILD_LOGS')
    def getDIR_LISTS     (self): return self._getDIR_x('LISTS')
    def getDIR_TEMP      (self): return self._getDIR_x('TEMP')

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
                logging.error("File already exists and it is not a building site")
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

                    self.apply_info(files[0])

        else:
            logging.error("Init error")

        return ret


    def read_package_info(self, ret_on_error=None):

        """
        Reads package info applied to building site

        :rtype: ``ret_on_error`` parameter contents on error (``None`` by default)
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
                "Can't open `{}' for writing".format(package_information_filename)
                )
        else:
            try:
                txt = ''
                try:
                    txt = json.dumps(info, allow_nan=True, indent=2, sort_keys=True)
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

        parse_result = org.wayround.utils.tarball_name_parser.parse_tarball_name(
            base,
            modify_info_file=False
            )

        if not isinstance(parse_result, dict):
            logging.error("Can't correctly parse file name")
            ret = 1
        else:
            package_info['pkg_nameinfo'] = parse_result

            self.write_package_info(package_info)

            ret = 0

        return ret

    apply_pkg_nameinfo_on_buildingsite.__doc__ += APPLY_DESCR

    def apply_constitution_on_buildingsite(self):
        """
        Applies constitution on building site package info
        """
        ret = 0

        package_info = self.read_package_info(ret_on_error={})

        const = org.wayround.aipsetup.constitution.read_constitution()

        if const == None:
            ret = 1

        else:
            package_info['constitution'] = const
            self.write_package_info(package_info)

        return ret

    apply_constitution_on_buildingsite.__doc__ += APPLY_DESCR


    def apply_pkg_info_on_buildingsite(self):

        """
        Applies package information on building site package info
        """

        ret = 0

        package_info = self.read_package_info(ret_on_error={})

        if (
            not isinstance(package_info, dict)
            or not 'pkg_nameinfo' in package_info
            or not isinstance(package_info['pkg_nameinfo'], dict)
            or not 'groups' in package_info['pkg_nameinfo']
            or not isinstance(package_info['pkg_nameinfo']['groups'], dict)
            or not 'name' in package_info['pkg_nameinfo']['groups']
            or not isinstance(package_info['pkg_nameinfo']['groups']['name'], str)
            ):

            logging.error("package_info['pkg_nameinfo']['groups'] undetermined")
            package_info['pkg_info'] = {}
            ret = 1

        else:

            logging.debug("Getting info from index DB")

            info = self.info_controller.get_info_rec_by_tarball_filename(
                package_info['pkg_nameinfo']['name']
                )

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


    def apply_info(self, src_file_name=None):
        """
        Apply package information to building site
        """

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

            if self.read_package_info(None) == None:
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
#            elif self.apply_constitution_on_buildingsite() != 0:
#                ret = 2
            elif self.apply_pkg_info_on_buildingsite() != 0:
                ret = 3

        return ret

    apply_info.__doc__ += APPLY_DESCR

    def _complete_info_correctness_check(self):

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
                org.wayround.aipsetup.buildscript.load_buildscript(
                    scr_name
                    ),
                dict
                )
            ):
            ret = 1

        return ret

    def complete(
        self,
        main_src_file=None,
        remove_buildingsite_after_success=False
        ):

        """
        Applies package information on building site, does building and packaging
        and optionally deletes building site after everything is done.

        :param main_src_file: used with function
            :func:`buildingsite.apply_info <org.wayround.aipsetup.buildingsite.apply_info>`
        """

        rp = org.wayround.utils.path.relpath(self.path, os.getcwd())

        logging.info(
            "+++++++++++ Starting Complete build in `{}' +++++++++++".format(rp)
            )

        building_site = org.wayround.utils.path.abspath(building_site)

        ret = 0

        if (_complete_info_correctness_check(building_site) != 0
            or
            isinstance(main_src_file, str)
            ):

            logging.warning(
                "buildscript information not available "
                "(or new main tarball file forced)"
                )

            if org.wayround.aipsetup.buildingsite.apply_info(
                building_site,
                main_src_file
                ) != 0 :
                logging.error("Can't apply build information to site")
                ret = 15

        if ret == 0:
            if _complete_info_correctness_check(building_site) != 0:

                logging.error(
                    "`{}' has wrong build script name".format(main_src_file)
                    )
                ret = 16

        if ret == 0:

            log = org.wayround.utils.log.Log(
                org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site),
                'buildingsite complete'
                )
            log.info("Buildingsite processes started")
            log.warning("Closing this log now, cause it can't work farther")
            log.stop()

            if org.wayround.aipsetup.build.complete(building_site) != 0:
                logging.error("Error on building stage")
                ret = 1
            elif org.wayround.aipsetup.pack.complete(building_site) != 0:
                logging.error("Error on packaging stage")
                ret = 2

        if ret == 0:
            if remove_buildingsite_after_success:
                logging.info("Removing buildingsite after successful build")
                try:
                    shutil.rmtree(building_site)
                except:
                    logging.exception("Could not remove `{}'".format(building_site))

        logging.info(
            "+++++++++++ Finished Complete build in `{}' +++++++++++".format(rp)
            )

        return ret

