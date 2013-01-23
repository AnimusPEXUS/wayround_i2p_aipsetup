
"""
Module for initiating building site

Later is required for farther package building.
"""

import os
import logging
import shutil
import json

import org.wayround.utils.path


import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.name


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


def _getDIR_x(path, _x='TARBALL'):
    '''
    Returns absolute path to DIR_{_x}

    note: this method is generated dinamicly
    '''

    ret = org.wayround.utils.path.abspath(
        os.path.join(
            path,
            eval('DIR_{}'.format(_x)))
        )

    return ret


def getDIR_TARBALL   (path): return _getDIR_x(path, 'TARBALL')
def getDIR_SOURCE    (path): return _getDIR_x(path, 'SOURCE')
def getDIR_PATCHES   (path): return _getDIR_x(path, 'PATCHES')
def getDIR_BUILDING  (path): return _getDIR_x(path, 'BUILDING')
def getDIR_DESTDIR   (path): return _getDIR_x(path, 'DESTDIR')
def getDIR_BUILD_LOGS(path): return _getDIR_x(path, 'BUILD_LOGS')
def getDIR_LISTS     (path): return _getDIR_x(path, 'LISTS')
def getDIR_TEMP      (path): return _getDIR_x(path, 'TEMP')


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

def cli_name():
    """
    aipsetup CLI interface part
    """
    return 'bsite'


def exported_commands():
    """
    aipsetup CLI interface part
    """
    return {
        'init': buildingsite_init,
        'apply': buildingsite_apply_info
        }

def commands_order():
    """
    aipsetup CLI interface part
    """
    return [
        'init',
        'apply'
        ]


def buildingsite_init(opts, args):
    """
    Initiate new building site dir

    [DIRNAME]

    One optional argument is dir in which initiation need to be done.
    Default is current dir
    """

    init_dir = '.'

    if len(args) > 0:
        init_dir = args[0]

    files = None
    if len(args) > 1:
        files = args[1:]

    ret = init(path=init_dir, files=files)

    return ret

def buildingsite_apply_info(opts, args):
    """
    Apply info to building dir

    [DIRNAME [FILENAME]]
    """

    dirname = '.'
    file = None

    if len(args) > 0:
        dirname = args[0]

    if len(args) > 1:
        file = args[1]

    ret = apply_info(dirname, file)

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

def init(path='build', files=None):
    """
    Initiates building site path for farther package build.

    Files in named directory are not deleted if it is already exists.

    :rtype: returns 0 if no errors
    """

    ret = 0

    path = org.wayround.utils.path.abspath(path)

    logging.info("Initiating building site `{}'".format(path))

    logging.info("Checking dir name safety")

    if isWdDirRestricted(path):
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
                t_dir = getDIR_TARBALL(path)

                for i in files:
                    logging.info("Copying file {}".format(i))
                    shutil.copy(i, t_dir)

                apply_info(path, files[0])

    else:
        logging.error("Init error")

    return ret


def read_package_info(path, ret_on_error=None):

    """
    Reads package info applied to building site

    :rtype: ``ret_on_error`` parameter contents on error (``None`` by default)
    """

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
            raise

        else:
            txt = f.read()
            f.close()

            try:
                ret = json.loads(txt)
            except:
                logging.error("Error in `{}'".format(pi_filename))
                ret = ret_on_error
                raise

    return ret

def write_package_info(path, info):
    """
    Writes given info to given building site

    Raises exceptions in case of errors
    """

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

def set_pkg_main_tarball(dirname, filename):
    """
    Set main package tarball in case there are many of them.
    """

    r = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, {}
        )

    r['pkg_tarball'] = dict(name=filename)

    org.wayround.aipsetup.buildingsite.write_package_info(
        dirname, r
        )

    return 0

def get_pkg_main_tarball(dirname):
    """
    Get main package tarball in case there are many of them.
    """

    ret = ''

    r = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, {}
        )

    if 'pkg_tarball' in r and 'name' in r['pkg_tarball']:
        ret = r['pkg_tarball']['name']

    return ret

APPLY_DESCR = """\

    It is typically used in conjunction with functions
    :func:`apply_constitution_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`,
    :func:`apply_pkg_info_on_buildingsite`
    in  this order by function :func:`apply_info`
"""


def apply_pkg_nameinfo_on_buildingsite(dirname, filename):

    """
    Applies package name parsing result on building site package info
    """

    ret = 0

    package_info = read_package_info(dirname, ret_on_error={})

    package_info['pkg_nameinfo'] = None

    base = os.path.basename(filename)

    parse_result = org.wayround.aipsetup.name.source_name_parse(
        base,
        modify_info_file=False
        )

    if not isinstance(parse_result, dict):
        logging.error("Can't correctly parse file name")
        ret = 1
    else:
        package_info['pkg_nameinfo'] = parse_result

        write_package_info(dirname, package_info)

        ret = 0

    return ret

apply_pkg_nameinfo_on_buildingsite.__doc__ += APPLY_DESCR



def apply_constitution_on_buildingsite(dirname):
    """
    Applies constitution on building site package info
    """

    ret = 0

    package_info = read_package_info(dirname, ret_on_error={})

    const = org.wayround.aipsetup.constitution.read_constitution()

    if const == None:

        ret = 1

    else:

        package_info['constitution'] = const

        write_package_info(dirname, package_info)

        ret = 0

    return ret

apply_constitution_on_buildingsite.__doc__ += APPLY_DESCR


def apply_pkg_info_on_buildingsite(dirname):

    """
    Applies package information on building site package info
    """

    ret = 0

    package_info = read_package_info(dirname, ret_on_error={})

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

        info = org.wayround.aipsetup.pkginfo.get_info_rec_by_tarball_filename(
            package_info['pkg_nameinfo']['name']
            )

        if not isinstance(info, dict):
            logging.error("Can't read info from DB")
            package_info['pkg_info'] = {}
            ret = 4

        else:

            package_info['pkg_info'] = info

            write_package_info(dirname, package_info)

            ret = 0

    return ret

apply_pkg_info_on_buildingsite.__doc__ += APPLY_DESCR


def apply_info(dirname='.', src_file_name=None):
    """
    Apply package information to building site
    """

    dirname = org.wayround.utils.path.abspath(dirname)

    ret = 0

    tar_dir = getDIR_TARBALL(dirname)

    if not isinstance(src_file_name, str):
        tar_files = os.listdir(tar_dir)

        if len(tar_files) != 1:
            logging.error("Can't decide which tarball to use")
            ret = 15
        else:
            src_file_name = tar_files[0]

    if ret == 0:

        if read_package_info(dirname, None) == None:
            logging.info(
                "Applying new package info to dir `{}'".format(
                    org.wayround.utils.path.abspath(
                        dirname
                        )
                    )
                )
            write_package_info(dirname, {})

        if apply_pkg_nameinfo_on_buildingsite(
                dirname, src_file_name
                ) != 0:
            ret = 1
        elif apply_constitution_on_buildingsite(dirname) != 0:
            ret = 2
        elif apply_pkg_info_on_buildingsite(dirname) != 0:
            ret = 3

    return ret

apply_info.__doc__ += APPLY_DESCR
