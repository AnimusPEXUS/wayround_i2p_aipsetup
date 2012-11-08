
"""
Module for initiating building site, which required to farver package build.
"""

import os
import logging
import shutil
import json


import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.name


DIR_TARBALL = '00.TARBALL'
DIR_SOURCE = '01.SOURCE'
DIR_PATCHES = '02.PATCHES'
DIR_BUILDING = '03.BUILDING'
DIR_DESTDIR = '04.DESTDIR'
DIR_BUILD_LOGS = '05.BUILD_LOGS'
DIR_LISTS = '06.LISTS'
DIR_TEMP = '07.TEMP'


def _getDIR_x(directory, _x='TARBALL'):
    '''
    Returns absolute path to DIR_{_x}

    note: this method is generated dinamicly
    '''

    ret = os.path.abspath(
        os.path.join(
            directory,
            eval('DIR_{}'.format(_x)))
        )

    while r'//' in ret:
        ret = ret.replace(r'//', '/')

    return ret


def getDIR_TARBALL   (directory): return _getDIR_x(directory, 'TARBALL')
def getDIR_SOURCE    (directory): return _getDIR_x(directory, 'SOURCE')
def getDIR_PATCHES   (directory): return _getDIR_x(directory, 'PATCHES')
def getDIR_BUILDING  (directory): return _getDIR_x(directory, 'BUILDING')
def getDIR_DESTDIR   (directory): return _getDIR_x(directory, 'DESTDIR')
def getDIR_BUILD_LOGS(directory): return _getDIR_x(directory, 'BUILD_LOGS')
def getDIR_LISTS     (directory): return _getDIR_x(directory, 'LISTS')
def getDIR_TEMP      (directory): return _getDIR_x(directory, 'TEMP')


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
'DIR_ALL copy'


def exported_commands():
    return {
        'init': buildingsite_init,
        'apply': buildingsite_apply_info
        }

def commands_order():
    return [
        'init',
        'apply'
        ]

def cli_name():
    return 'bsi'


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

    ret = init(buildingsite=init_dir, files=files)

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

def get_list_of_items_to_pack(building_site):

    building_site = os.path.abspath(building_site)

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

def isWdDirRestricted(directory):
    """
    This function is a routine to check supplied dir is it suitable
    to be a working dir
    """

    ret = False

    dirs_begining_with = [
        '/bin', '/boot' , '/daemons',
        '/dev', '/etc', '/lib', '/proc',
        '/sbin', '/sys',
        '/usr'
    ]

    exec_dirs = ['/opt', '/var', '/']

    dir_str_abs = os.path.abspath(directory)

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

def init(buildingsite='build', files=None):
    """
    Initiates building site dir for farcer package build
    """

    ret = 0

    buildingsite = os.path.abspath(buildingsite)

    logging.info("Initiating building site `{}'".format(buildingsite))

    logging.info("Checking dir name safety")

    if isWdDirRestricted(buildingsite):
        logging.error(
            "`{}' is restricted working dir -- won't init".format(buildingsite)
            )
        ret = -1


    # if exists and not derictory - not continue
    if ret == 0:

        if ((os.path.exists(buildingsite))
            and not os.path.isdir(buildingsite)):
            logging.error("File already exists and it is not a buildingsite")
            ret = -2

    if ret == 0:

        if not os.path.exists(buildingsite):
            logging.info("Building site not exists - creating")
            os.mkdir(buildingsite)

        logging.info("Creating required subdirs")
        for i in DIR_ALL:
            a = os.path.abspath(os.path.join(buildingsite, i))

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
                t_dir = getDIR_TARBALL(buildingsite)

                for i in files:
                    logging.info("Copying file {}".format(i))
                    shutil.copy(i, t_dir)

                apply_info(buildingsite, files[0])

    else:
        logging.error("Init error")

    return ret


def read_package_info(directory, ret_on_error=None):

    logging.debug(
        "Trying to read package info in building site `{}'".format(directory)
        )

    ret = ret_on_error

    pi_filename = os.path.join(directory, 'package_info.json')

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

def write_package_info(directory, info):

    pi_filename = os.path.join(directory, 'package_info.json')

    f = None

    try:
        f = open(pi_filename, 'w')
    except:
        logging.error(
            "Can't open `{}' for writing".format(pi_filename)
            )
        raise
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

    return

def set_pkg_main_tarball(dirname, filename):

    r = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, {}
        )
    r['pkg_tarball'] = dict(name=filename)

    org.wayround.aipsetup.buildingsite.write_package_info(
        dirname, r
        )

    return 0

def get_pkg_main_tarball(dirname):

    ret = ''

    r = org.wayround.aipsetup.buildingsite.read_package_info(
        dirname, {}
        )

    if 'pkg_tarball' in r and 'name' in r['pkg_tarball']:
        ret = r['pkg_tarball']['name']

    return ret

def apply_pkg_nameinfo_on_buildingsite(dirname, filename):

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



def apply_constitution_on_buildingsite(dirname):

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


def apply_pkg_info_on_buildingsite(dirname):

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


def apply_info(dirname='.', src_file_name=None):

    dirname = os.path.abspath(dirname)

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
                    os.path.abspath(
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
    #    elif apply_pkg_buildscript_on_buildingsite(dirname) != 0:
    #        ret = 4

    return ret
