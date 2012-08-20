
"""
Module for initiating building site, which required to farver package build.
"""

import os
#import inspect
import pprint
import logging

import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.name
#import org.wayround.aipsetup.config
import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.buildinfo


DIR_TARBALL = '00.TARBALL'
DIR_SOURCE = '01.SOURCE'
DIR_PATCHES = '02.PATCHES'
DIR_BUILDING = '03.BUILDING'
DIR_DESTDIR = '04.DESTDIR'
DIR_BUILD_LOGS = '05.BUILD_LOGS'
DIR_LISTS = '06.LISTS'

def _getDir_x(directory, _x='TARBALL'):
    '''
    Returns absolute path to DIR_{_x}

    note: this method is generated dinamicly
    '''
    return os.path.abspath(
        os.path.join(
            directory,
            eval('DIR_{}'.format(_x)))
        )

def getDIR_TARBALL   (directory): return _getDir_x(directory, 'TARBALL')
def getDIR_SOURCE    (directory): return _getDir_x(directory, 'SOURCE')
def getDIR_PATCHES   (directory): return _getDir_x(directory, 'PATCHES')
def getDIR_BUILDING  (directory): return _getDir_x(directory, 'BUILDING')
def getDIR_DESTDIR   (directory): return _getDir_x(directory, 'DESTDIR')
def getDIR_BUILD_LOGS(directory): return _getDir_x(directory, 'BUILD_LOGS')
def getDIR_LISTS     (directory): return _getDir_x(directory, 'LISTS')


DIR_ALL = [
    DIR_TARBALL,
    DIR_SOURCE,
    DIR_PATCHES,
    DIR_BUILDING,
    DIR_DESTDIR,
    DIR_BUILD_LOGS,
    DIR_LISTS
    ]
'All package directories list in proper order'

DIR_LIST = DIR_ALL
'DIR_ALL copy'


def exported_commands():
    return {
        'init': buildingsite_init,
        'apply_info': buildingsite_apply_info
        }

def commands_order():
    return [
        'init',
        'apply_info'
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

    ret = init(directory=init_dir)

    return ret

def buildingsite_apply_info(opts, args):
    """
    Apply info to building dir

    [-d=DIRNAME] SOURCE_FILE_NAME
    """
    ret = 0

    if len(args) != 1:
        logging.error("tarball name to analyze not specified")
        ret = 1
    else:

        name = args[0]

        dirname = '.'

        if '-d' in opts:
            dirname = opts['-d']

        ret = apply_info(dirname, source_filename=name)

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

def init(directory='build'):
    """
    Initiates building site dir for farcer package build
    """

    ret = 0

    directory = os.path.abspath(directory)

    logging.info("Initiating building site `{}'".format(directory))

    logging.info("Checking dir name safety")

    if isWdDirRestricted(directory):
        logging.error(
            "`{}' is restricted working dir -- won't init".format(directory)
            )
        ret = -1


    # if exists and not derictory - not continue
    if ret == 0:

        if ((os.path.exists(directory))
            and not os.path.isdir(directory)):
            logging.error("File already exists and it is not a directory")
            ret = -2

    if ret == 0:

        if not os.path.exists(directory):
            logging.info("Building site not exists - creating")
            os.mkdir(directory)

        logging.info("Creating required subdirs")
        for i in DIR_ALL:
            a = os.path.abspath(os.path.join(directory, i))

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
    else:
        logging.error("Init error")

    return ret


def read_package_info(directory, ret_on_error=None):

    logging.debug("Trying to read package info in building site `{}'".format(directory))

    ret = ret_on_error

    pi_filename = os.path.join(directory, 'package_info.py')

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

            g = {}
            l = {}

            try:
                ret = eval(txt, g, l)

            except:
                logging.exception("Error in `{}'".format(pi_filename))
                ret = ret_on_error
                raise

    return ret

def write_package_info(directory, info):

    pi_filename = os.path.join(directory, 'package_info.py')

    f = None

    try:
        f = open(pi_filename, 'w')
    except:
        logging.exception("Can't open `%(file)s' for writing" % {
            'file': pi_filename
            })
        raise
    else:
        try:
            txt = ''
            try:
                txt = pprint.pformat(info)
            except:
                logging.exception("Can't represent data for package info")
                raise
            else:

                f.write("""\
#!/usr/bin/python
# -*- coding: utf-8 -*-

{text}
""".format(text=txt))

        finally:
            f.close()


    return


def apply_pkg_nameinfo_on_buildingsite(dirname, filename):

    ret = 0

    package_info = read_package_info(dirname, ret_on_error={})

    package_info['pkg_nameinfo'] = None

    base = os.path.basename(filename)

    parse_result = org.wayround.aipsetup.name.source_name_parse(
        base,
        modify_info_file=False
        )

    if parse_result == None:
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

    if not isinstance(package_info, dict) \
            or not 'pkg_nameinfo' in package_info \
            or not isinstance(package_info['pkg_nameinfo'], dict) \
            or not 'groups' in package_info['pkg_nameinfo'] \
            or not isinstance(package_info['pkg_nameinfo']['groups'], dict) \
            or not 'name' in package_info['pkg_nameinfo']['groups'] \
            or not isinstance(package_info['pkg_nameinfo']['groups']['name'],
                              str):

        logging.error("package_info['pkg_nameinfo']['groups'] undetermined")
        package_info['pkg_info'] = {}
        ret = 1

    else:

        logging.debug("Getting info from index DB")

        res = org.wayround.aipsetup.pkgindex.find_package_info_by_basename_and_version(
            package_info['pkg_nameinfo']['groups']['name'],
            package_info['pkg_nameinfo']['groups']['version']
            )

        offerings = list(res.keys())
        if len(offerings) == 0:
            logging.error(
                "Can't find acceptable basename=>version_re package info offering in package index"
                )
            ret = 2
        elif len(offerings) > 1:
            logging.error(
                "To many acceptable basename=>version_re offerings in package index:\n{}".format(res)
                )
            ret = 3
        else:

            info = res[offerings[0]]

            if not isinstance(info, dict):
                logging.error("Can't read info from DB")
                package_info['pkg_info'] = {}
                ret = 4

            else:

                package_info['pkg_info'] = info

                write_package_info(dirname, package_info)

                ret = 0

    return ret


def apply_pkg_buildinfo_on_buildingsite(dirname):

    ret = 0

    package_info = read_package_info(dirname, ret_on_error={})


    if not isinstance(package_info, dict) \
            or not 'pkg_info' in package_info \
            or not isinstance(package_info['pkg_info'], dict) \
            or not 'buildinfo' in package_info['pkg_info'] \
            or not isinstance(package_info['pkg_info']['buildinfo'], str):
        logging.error("package_info['pkg_info']['buildinfo'] undetermined")
        package_info['pkg_buildinfo'] = {}
        ret = 1

    else:

        if package_info['pkg_info']['buildinfo'] == '' or package_info['pkg_info']['buildinfo'].isspace():
            logging.error(
                "package_info['pkg_info']['buildinfo'] is empty or space.\n" +
                "    probably you need to edit `{}' and update indexing".format(
                    package_info['pkg_info']['name'] + '.xml')
                )
            ret = 2
        else:

            buildinfo = org.wayround.aipsetup.buildinfo.load_buildinfo(
                package_info['pkg_info']['buildinfo']
                )

            if not isinstance(buildinfo, dict):
                logging.error(
                    "Error loading buildinfo `{}'".format(
                        package_info['pkg_info']['buildinfo']
                        )
                    )
                ret = 3
            else:

                package_info['pkg_buildinfo'] = buildinfo
                write_package_info(dirname, package_info)

    return ret


def apply_info(dirname='.', source_filename=None):

    ret = 0

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
            dirname, source_filename
            ) != 0:
        ret = 1
    elif apply_constitution_on_buildingsite(dirname) != 0:
        ret = 2
    elif apply_pkg_info_on_buildingsite(dirname) != 0:
        ret = 3
    elif apply_pkg_buildinfo_on_buildingsite(dirname) != 0:
        ret = 4

    return ret


