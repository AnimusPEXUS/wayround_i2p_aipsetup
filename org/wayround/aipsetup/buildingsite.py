
"""
Module for initiating building site, which required to farver package build.
"""

import os
import sys
import inspect
import copy
import pprint
import logging

import org.wayround.aipsetup.info
import org.wayround.aipsetup.constitution
import org.wayround.aipsetup.name
import org.wayround.aipsetup.config


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

        logging.info("Create all subdirs")
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

        else:
            txt = f.read()
            f.close()

            g = {}
            l = {}

            try:
                ret = eval(txt, g, l)
            except:
                logging.exception("error in `{}'".format(pi_filename))
                ret = ret_on_error

    return ret

def write_package_info(directory, info):

    pi_filename = os.path.join(directory, 'package_info.py')

    f = None

    try:
        f = open(pi_filename, 'w')
    except:
        logging.exception("can't open `%(file)s' for writing" % {
            'file': pi_filename
            })
    else:
        try:
            txt = ''
            try:
                txt = pprint.pformat(info)
            except:
                logging.exception("can't represent data for package info")
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

    d = read_package_info(dirname, ret_on_error={})

    d['pkg_nameinfo'] = None

    base = os.path.basename(filename)

    parse_result = org.wayround.aipsetup.name.source_name_parse(
        base,
        modify_info_file=False
        )

    if parse_result == None:
        logging.error("Can't correctly parse file name")
        ret = 1
    else:
        d['pkg_nameinfo'] = parse_result

        write_package_info(dirname, d)

        ret = 0

    return ret



def apply_constitution_on_buildingsite(dirname):

    ret = 0

    d = read_package_info(dirname, ret_on_error={})

    const = org.wayround.aipsetup.constitution.read_constitution()

    if const == None:

        ret = 1

    else:

        d['constitution'] = const

        write_package_info(dirname, d)

        ret = 0

    return ret


def apply_pkg_info_on_buildingsite(dirname):

    ret = 0

    d = read_package_info(dirname, ret_on_error={})

    if not isinstance(d, dict) \
            or not 'pkg_nameinfo' in d \
            or not isinstance(d['pkg_nameinfo'], dict) \
            or not 'groups' in d['pkg_nameinfo'] \
            or not isinstance(d['pkg_nameinfo']['groups'], dict) \
            or not 'name' in d['pkg_nameinfo']['groups'] \
            or not isinstance(d['pkg_nameinfo']['groups']['name'],
                              str):


        logging.error("info undetermined")
        d['pkg_info'] = {}
        ret = 1

    else:
        infoname = d['pkg_nameinfo']['groups']['name']

        info_filename = os.path.join(
            org.wayround.aipsetup.config.config['info'],
            '{}.xml'.format(infoname)
            )

        logging.info("Reading info file `%(name)s'" % {
            'name': info_filename
            })
        info = org.wayround.aipsetup.info.read_from_file(info_filename)
        if not isinstance(info, dict):
            logging.error("Can't read info from %(filename)s" % {
                'filename': info_filename
                })
            d['pkg_info'] = {}
            ret = 2
        else:

            d['pkg_info'] = info
            # print repr(info)

            write_package_info(dirname, d)

            ret = 0

    return ret


def apply_pkg_buildinfo_on_buildingsite(dirname):

    ret = 0

    pi = read_package_info(dirname, ret_on_error={})

    if not isinstance(pi, dict) \
            or not 'pkg_info' in pi \
            or not isinstance(pi['pkg_info'], dict) \
            or not 'buildinfo' in pi['pkg_info'] \
            or not isinstance(pi['pkg_info']['buildinfo'], str):
        logging.error("buildinfo undetermined")
        pi['pkg_buildinfo'] = {}
        ret = 1

    else:

        buildinfo_filename = os.path.join(
            org.wayround.aipsetup.config.config['buildinfo'], '%(name)s.py' % {
                'name': pi['pkg_info']['buildinfo']
                }
            )

        if not os.path.exists(buildinfo_filename) \
                or not os.path.isfile(buildinfo_filename):
            logging.error("Can't find buildinfo Python script `%(name)s'" % {
                'name': buildinfo_filename
                })
            ret = 2

        else:

            g = {}
            l = {}

            try:
                exec(compile(open(buildinfo_filename).read(), buildinfo_filename, 'exec'), g, l)
            except:
                logging.exception("Can't load buildinfo Python script `%(name)s'" % {
                    'name': buildinfo_filename
                    })
                ret = 3

            else:

                if not 'build_info' in l \
                        or not inspect.isfunction(l['build_info']):

                    logging.error("Named module doesn't have 'build_info' function")
                    ret = 4

                else:

                    try:
                        l['build_info'](copy.copy(org.wayround.aipsetup.config.config), pi)
                    except:
                        logging.exception("Error while calling for build_info() from `{}'".format(buildinfo_filename))
                        pi['pkg_buildinfo'] = {}
                        ret = 5

                    else:

                        write_package_info(dirname, pi)

                        ret = 0

    return ret


def apply_info(dirname='.', source_filename=None):

    ret = 0

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


