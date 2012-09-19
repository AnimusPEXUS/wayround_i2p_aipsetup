
"""
Module for system related package actions

 * install_asp into system;
 * list installed;
 * find issues;
 * remove from system;
 * completely build new package from source...
 etc.
"""

import sys
import os
import os.path
import tarfile
import glob
import tempfile
import shutil
import copy
import re
import fnmatch
import logging
import functools


import org.wayround.utils.checksum
import org.wayround.utils.text
import org.wayround.utils.time
import org.wayround.utils.archive
import org.wayround.utils.log


import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.name
import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.config
import org.wayround.aipsetup.build
import org.wayround.aipsetup.pack
import org.wayround.aipsetup.sysupdates


def exported_commands():
    return {
        'install'       : package_install,
        'list'          : package_list,
        'list_asps'     : package_list_asps,
        'remove'        : package_remove,
        'complete'      : package_complete,
        'build'         : package_build,
        'find_file'     : package_find_files,
        'index'         : package_put_to_index_many
        }

def commands_order():
    return [
        'list',
        'list_asps',
        'install',
        'remove',
        'complete',
        'build',
        'index',
        'find'
        ]

def package_install(opts, args):
    """
    [-b=DIRNAME] [--force] NAME

    Install package. If -b is given - it is used as destination root
    """

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    force = '--force' in opts

    if len(args) == 0:
        logging.error("Package name required!")
        ret = 2
    else:
        name = args[0]
        ret = install_package(name, force, basedir)
        org.wayround.aipsetup.sysupdates.all_actions()

    return ret

def package_list(opts, args):
    """
    List installed packages

    [-b=DIRNAME] MASK

    -b is same as in install
    """

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    mask = '*'
    if len(args) > 0:
        mask = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if ret == 0:
        lst = list_installed_packages(mask, basedir)

        lst.sort()

        org.wayround.utils.text.columned_list_print(
            lst, fd=sys.stdout.fileno()
        )

    return ret

def package_list_asps(opts, args):
    """
    List installed package's ASPs

    [-b=DIRNAME] NAME

    -b is same as in install
    """

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    name = None

    if len(args) != 1:
        logging.error("Package name required")
    else:

        name = args[0]

        if not isinstance(basedir, str):
            logging.error("given basedir name is wrong")
            ret = 2

        else:

            logging.info("Searching ASPs for package `{}'".format(name))

            lst = list_installed_package_s_asps(name, basedir)

            lst.sort(
                reverse=True,
                key=functools.cmp_to_key(org.wayround.aipsetup.version.package_version_comparator)
                )

            for i in lst:
                print("    {}".format(i))

#            org.wayround.utils.text.columned_list_print(
#                lst, fd=sys.stdout.fileno()
#            )

    return ret


def package_remove(opts, args):
    """
    Removes package matching NAME.

    [-b=DIRNAME] [--force] NAME

    --force    force removal of packages for which info is not
               available or which is not removable
    """
    # TODO: maybe some warnings need to be included in help

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    force = '--force' in opts

    name = None
    if len(args) > 0:
        name = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if not isinstance(name, str):
        logging.error("package to remove not named!")
        ret = 3

    if ret == 0:
        ret = remove_package(name, force, basedir)

    return ret

def package_complete(opts, args):
    """
    Complete package building process: build complete; pack complete

    [DIRNAME]

    DIRNAME defaults to current dir
    """

    dirname = '.'

    if len(args) > 0:
        dirname = args[0]

    ret = complete(dirname)

    return ret

def package_build(opts, args):
    """
    Place named source files in new building site and build new package from them.

    TARBALL
    """

    sources = []

    ret = 0

    if len(args) > 0:
        sources = args

    if len(sources) == 0:
        logging.error("No source files named")
        ret = 2

    if ret == 0:
        ret = build(sources)

    return ret

def package_find_files(opts, args):
    """
    Looks for LOOKFOR in all installed packages using one of methods:

    [-b=DIRNAME] [-m=beg|re|plain|sub|fm] LOOKFOR

       sub   - (default) filename contains LOOKFOR
       re    - LOOKFOR is RegExp
       beg   - file name starts with LOOKFOR
       plain - Exact LOOKFOR match
       fm    - LOOKFOR is file mask
    """
    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    look_meth = 'sub'
    if '-m' in opts:
        look_meth = opts['-m']

    lookfor = ''
    if len(args) > 0:
        lookfor = args[0]

    ret = find_file_in_files_installed_by_asps(
        basedir, lookfor, mode=look_meth,
        mute=False,
        return_dict=False
        )

    return ret

def package_put_to_index_many(opts, args):
    """
    Put package to repository and add it to index
    """

    ret = 0

    files = []
    if len(args) > 0:
        files = args[:]

    if len(files) == 0:
        logging.error("Filenames required")
        ret = 2
    else:
        ret = put_files_to_index(files)

    return ret


def check_package(asp_name, mute=False):
    """
    Check package for errors
    """
    ret = 0

    asp_name = os.path.abspath(asp_name)

    if not asp_name.endswith('.asp'):
        if not mute:
            logging.error("Wrong file extension `%(name)s'" % {
                'name': asp_name
                })
        ret = 3
    else:
        try:
            tarf = tarfile.open(asp_name, mode='r')
        except:
            logging.exception("Can't open file `%(name)s'" % {
                'name': asp_name
                })
            ret = 1
        else:
            try:
                f = org.wayround.utils.archive.tar_member_get_extract_file(
                    tarf,
                    './package.sha512'
                    )
                if not isinstance(f, tarfile.ExFileObject):
                    logging.error("Can't get checksums from package file")
                    ret = 2
                else:
                    sums_txt = f.read()
                    f.close()
                    sums = org.wayround.utils.checksum.parse_checksums_text(
                        sums_txt
                        )
                    del(sums_txt)

                    sums2 = {}
                    for i in sums:
                        sums2['.' + i] = sums[i]
                    sums = sums2
                    del(sums2)

                    tar_members = tarf.getmembers()

                    check_list = ['./04.DESTDIR.tar.xz', './05.BUILD_LOGS.tar.xz',
                                  './package_info.json', './02.PATCHES.tar.xz']

                    for i in ['./00.TARBALL', './06.LISTS']:
                        for j in tar_members:
                            if ((j.name.startswith(i) \
                                and j.name != i)):
                                check_list.append(j.name)

                    check_list.sort()

                    error_found = False

                    for i in check_list:
                        cresult = ''
                        if not i in sums \
                            or tarobj_check_member_sum(tarf, sums, i) == False:
                            error_found = True
                            cresult = "FAIL"
                        else:
                            cresult = "OK"

                        if not mute:
                            print("       %(name)s - %(result)s" % {
                                'name': i,
                                'result': cresult
                                })

                    if error_found:
                        logging.error("Error was found while checking package")
                        ret = 3
                    else:
                        ret = 0
            finally:
                tarf.close()

    return ret

def check_package_aipsetup2(filename):

    ret = 0

    filename = os.path.abspath(filename)
    if not filename.endswith('.tar.xz'):
        ret = 1
    else:
        filename_sha512 = filename + '.sha512'
        filename_md5 = filename + '.md5'

        if (not os.path.isfile(filename)
            or not os.path.isfile(filename_sha512)
            or not os.path.isfile(filename_md5)
            ):
            ret = 2
        else:

            bn = os.path.basename(filename)
            dbn = './' + bn

            sha512 = org.wayround.utils.checksum.make_file_checksum(
                filename, 'sha512'
                )

            md5 = org.wayround.utils.checksum.make_file_checksum(
                filename, 'md5'
                )

            sha512s = org.wayround.utils.checksum.parse_checksums_file_text(
                filename_sha512
                )

            md5s = org.wayround.utils.checksum.parse_checksums_file_text(
                filename_md5
                )

            if not isinstance(sha512, str):
                ret = 3
            elif not isinstance(md5, str):
                ret = 4
            elif not isinstance(sha512s, dict):
                ret = 5
            elif not isinstance(md5s, dict):
                ret = 6
            elif not dbn in sha512s:
                ret = 7
            elif not dbn in md5s:
                ret = 8
            elif not sha512s[dbn] == sha512:
                ret = 9
            elif not md5s[dbn] == md5:
                ret = 10
            else:
                ret = 0

    return ret


def remove_package(name, force=False, destdir='/', mute=False):
    ret = 0

    db = org.wayround.aipsetup.pkgindex.PackageDatabase()
    info = db.package_info_record_to_dict(name)
    del db

    if not isinstance(info, dict) and not force:
        logging.error("Can't find information about package `{}'".format(name))

        ret = 1

    else:
        if not force and (isinstance(info, dict) and not info['removable']):
            logging.error("Package `{}' is not removable".format(name))

            ret = 2

        else:

            lst = list_installed_package_s_asps(
                name, destdir
                )

            lst.sort(
                reverse=True,
                key=functools.cmp_to_key(org.wayround.aipsetup.version.package_version_comparator)
                )

            if not mute:
                print("Following packages will be removed:")
                for i in lst:
                    print("    {}".format(i))

            for i in lst:

                name = (
                    org.wayround.aipsetup.name.remove_extension_from_valid_package_name(i)
                    )

                if not mute:
                    logging.info("Removing package `{}'".format(name))
                remove_asp(name, destdir)

    return ret

def install_package(name, force=False, destdir='/'):

    ret = 0

    if os.path.isfile(name):
        name_parsed = org.wayround.aipsetup.name.package_name_parse(
            name, mute=True
            )

        if not force and not isinstance(name_parsed, dict):
            logging.error("Can't parse `{}' as package name".format(name))
            ret = 1
        else:

            info = None
            if not force and isinstance(name_parsed, dict):
                info = org.wayround.aipsetup.pkgindex.get_package_info(
                    name_parsed['groups']['name']
                    )

            if not isinstance(info, dict) and not force:
                logging.error(
                    "Can't get info on package `{}' : `{}'".format(
                        name_parsed['groups']['name'], name)
                        )
                ret = 2
            else:

                asps = list_installed_package_s_asps(
                    name_parsed['groups']['name'], destdir
                    )

                ret = install_asp(name, destdir)

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
                        if info['reducible']:
                            logging.info("Reducing `{}' ASPs".format(name_parsed['groups']['name']))
                            reduce_asps(name, asps, destdir)

    else:
        info = org.wayround.aipsetup.pkgindex.get_package_info(name)

        if not isinstance(info, dict):
            logging.error("Don't know about package")

    return ret

def update_package(name, force=False, destdir='/'):
    # TODO: do or del
    pass

def tarobj_check_member_sum(tarobj, sums, member_name):
    ret = True
    fobj = org.wayround.utils.archive.tar_member_get_extract_file(
        tarobj,
        member_name
        )
    if not isinstance(fobj, tarfile.ExFileObject):
        ret = False
    else:
        summ = org.wayround.utils.checksum.make_fileobj_checksum(fobj)
        if summ == sums[member_name]:
            ret = True
        else:
            ret = False
        fobj.close()
    return ret


def install_asp(asp_name, destdir='/'):

    ret = 0

    destdir = os.path.abspath(destdir)

    logging.info("Performing package checks before it's installation")
    if check_package(asp_name) != 0:
        logging.error("Package defective - installation failed")
        ret = 1
    else:
        try:
            tarf = tarfile.open(asp_name, mode='r')
        except:
            logging.exception("Can't open file `{}'".format(asp_name))
            ret = 1
        else:

            package_name = asp_name[:-4]

            for i in [
                (
                     './06.LISTS/DESTDIR.lst.xz',
                     'installed_pkg_dir',
                     "package's file list"
                     ),
                (
                     './06.LISTS/DESTDIR.sha512.xz',
                     'installed_pkg_dir_sums',
                     "package's check sums"
                     ),
                (
                     './05.BUILD_LOGS.tar.xz',
                     'installed_pkg_dir_buildlogs',
                     "package's buildlogs"
                     )
                ]:

                logging.info("Installing %(what)s" % {
                    'what': i[2]
                    })

                logs_path = ''
                if org.wayround.aipsetup.config.config[i[1]][0] == '/':
                    logs_path = org.wayround.aipsetup.config.config[i[1]][1:]
                else:
                    logs_path = org.wayround.aipsetup.config.config[i[1]]

                out_filename = \
                    os.path.abspath(
                        os.path.join(
                            destdir,
                            logs_path,
                            package_name + '.xz'
                            )
                        )

                out_filename_dir = os.path.dirname(out_filename)

                if not os.path.exists(out_filename_dir):
                    os.makedirs(out_filename_dir)

                if org.wayround.utils.archive.tar_member_get_extract_file_to(
                        tarf,
                        i[0],
                        out_filename
                        ) != 0 :
                    logging.error("Can't install_asp %(what)s as %(outname)s" % {
                        'what': i[2],
                        'outname': out_filename
                        })
                    ret = 2
                    break

            if ret == 0:
                logging.info("Installing package's destdir")

                dd_fobj = org.wayround.utils.archive.\
                    tar_member_get_extract_file(
                        tarf, './04.DESTDIR.tar.xz'
                        )
                if not isinstance(dd_fobj, tarfile.ExFileObject):
                    logging.error("Can't get package's destdir")
                    ret = 4
                else:
                    tec = org.wayround.utils.archive.extract_tar_canonical_fobj(
                            dd_fobj,
                            destdir,
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
                            "Package destdir decompression error:"
                            " tar exit code: {}".format(
                                tec
                            )
                        )
                        ret = 5
                    else:
                        ret = 0
                        logging.info("Installation look like complete :-)")
                    dd_fobj.close()

            tarf.close()

    return ret

def remove_asp(
        asp_name,
        destdir='/',
        only_remove_package_registration=False,
        exclude=None,
        mute=False
        ):

    ret = 0

    destdir = os.path.abspath(destdir)

    lines = list_files_installed_by_asp(destdir, asp_name, mute)

    logging.info("Removing {} files".format(asp_name))

    if not isinstance(lines, list):
        logging.error(
            "Some errors while getting ASP's file list for `{}'".format(
                asp_name
                )
            )
        ret = 1
    else:

        if not only_remove_package_registration:

            lines_before_ex = len(lines)
            if exclude:
                lines = list(set(lines) - set(exclude))
            lines_after_ex = len(lines)

            if lines_before_ex != lines_after_ex:
                logging.info(
                    "Excluded {} files".format(
                        lines_before_ex - lines_after_ex
                        )
                    )

            lines.sort(reverse=True)

            for line in lines:

                rm_file_name = os.path.abspath(
                    destdir + os.path.sep + line
                    )
                if os.path.islink(rm_file_name) or os.path.isfile(rm_file_name):
                    if not mute:
                        logging.info("   removing: {}".format(rm_file_name))
                    try:
                        os.unlink(rm_file_name)
                    except:
                        logging.exception(
                            "Couldn't remove file: {}".format(rm_file_name)
                            )

        for i in [
            'installed_pkg_dir_buildlogs',
            'installed_pkg_dir_sums',
            'installed_pkg_dir'
            ]:
            rm_file_name = os.path.abspath(
                destdir + os.path.sep +
                org.wayround.aipsetup.config.config[i] + os.path.sep +
                asp_name + '.xz'
                )
            if os.path.isfile(rm_file_name):
                logging.info("   removing: %(name)s" % {
                    'name': rm_file_name
                    })
                os.unlink(rm_file_name)
    return ret

def reduce_asps(reduce_to, reduce_what=None, destdir='/', mute=False):

    if not isinstance(reduce_what, list):
        raise ValueError("reduce_what must be a list of strings")

    reduce_to = os.path.basename(reduce_to)
    reduce_to = (
        org.wayround.aipsetup.name.remove_extension_from_valid_package_name(reduce_to)
        )

    for i in range(len(reduce_what)):
        reduce_what[i] = os.path.basename(reduce_what[i])
        reduce_what[i] = (
            org.wayround.aipsetup.name.remove_extension_from_valid_package_name(
                reduce_what[i]
                )
            )

    if reduce_to in reduce_what:
        reduce_what.remove(reduce_to)

    if destdir != '/':
        if not mute:
            logging.info("Destdir: {}".format(destdir))

    reduce_to_lst = set(list_files_installed_by_asp(destdir, reduce_to))

    for i in reduce_what:
        remove_asp(
            i,
            destdir,
#            only_remove_package_registration=True,
            exclude=reduce_to_lst
            )

    return 0


def list_installed_asps(destdir='/', mute=False):
    destdir = os.path.abspath(destdir)

    listdir = os.path.abspath(destdir + org.wayround.aipsetup.config.config['installed_pkg_dir'])
    filelist = glob.glob(os.path.join(listdir, '*.xz'))

    ret = 0

    if not os.path.isdir(listdir):
        logging.error("not a dir %(dir)s" % {
            'dir': listdir
            })
        ret = 1
    else:

        bases = []
        for each in filelist:
            bases.append(os.path.basename(each))

        for i in ['sums', 'buildlogs', '.', '..']:
            if i in bases:
                bases.remove(i)

        ret = bases

    return ret


def list_installed_packages(mask='*', destdir='/', mute=False):

    ret = None

    asps = list_installed_asps(destdir, True)

    if not isinstance(asps, list):
        logging.error("Error getting list of installed ASPs")
    else:
        lst = set()
        for i in asps:
            parsed = org.wayround.aipsetup.name.package_name_parse(i, mute=True)

            if not isinstance(parsed, dict):
                logging.error("Couldn't parse name `{}'".format(i))
            else:
                name = parsed['groups']['name']
                if fnmatch.fnmatch(name, mask):
                    lst.add(name)

        lst = list(lst)
        lst.sort()

        ret = lst

    return ret

def list_installed_package_s_asps(name, destdir='/'):

    ret = 0

    lst = list_installed_asps(destdir=destdir, mute=True)

    lst2 = set()

    for i in lst:
        name_parsed = (
            org.wayround.aipsetup.name.package_name_parse(
                i,
                mute=True
                )
            )

        if (isinstance(name_parsed, dict)
            and name_parsed['groups']['name'] == name):

            lst2.add(i)

    lst = list(lst2)

    del lst2

    ret = lst

    return ret

def list_files_installed_by_asp(
        destdir, asp_name, mute=True
        ):
    ret = 0

    destdir = os.path.abspath(destdir)

    list_dir = os.path.abspath(
        destdir + os.path.sep + org.wayround.aipsetup.config.config['installed_pkg_dir']
        )

    pkg_list_file = os.path.join(list_dir, asp_name)

    if not pkg_list_file.endswith('.xz'):
        pkg_list_file += '.xz'

    try:
        f = open(pkg_list_file, 'rb')
    except:
        logging.exception("Can't open list file")
        ret = 2
    else:

        pkg_file_list = org.wayround.utils.archive.xzcat(
            f, convert_to_str=True
            )

        f.close()

        pkg_file_list = pkg_file_list.splitlines()
        pkg_file_list = (
            org.wayround.utils.list.list_strip_remove_empty_remove_duplicated_lines(pkg_file_list)
            )


        pkg_file_list.sort()

        ret = copy.copy(pkg_file_list)

    return ret


# TODO: build [TARBALL1] [TARBALL2] .. [TARBALLn]
def build(source_files):
    ret = 0

    par_res = org.wayround.aipsetup.name.source_name_parse(source_files[0])

    if par_res == None:
        logging.error("Can't parse source file name")
        ret = 1
    else:

        try:
            os.makedirs(org.wayround.aipsetup.config.config['buildingsites'])
        except:
            pass

        package_info = org.wayround.aipsetup.pkgindex.find_package_info_by_basename_and_version(
            par_res['groups']['name'], par_res['groups']['version']
            )

        if package_info == {}:
            logging.error(
                "Can't find package information for package with basename `{}'".format(
                    par_res['groups']['name']
                    )
                )
            ret = 2
        else:

            tmp_dir_prefix = "{name}-{version}-{status}-{timestamp}-".format_map(
                {
                    'name': package_info[list(package_info.keys())[0]]['name'],
                    'version': par_res['groups']['version'],
                    'status': par_res['groups']['status'],
                    'timestamp': org.wayround.utils.time.currenttime_stamp()
                    }
                )

            build_site_dir = tempfile.mkdtemp(
                prefix=tmp_dir_prefix,
                dir=org.wayround.aipsetup.config.config['buildingsites']
                )
            build_site_dir = os.path.abspath(build_site_dir)

            if org.wayround.aipsetup.buildingsite.init(build_site_dir) != 0:
                logging.error("Error initiating temporary dir")
                ret = 3
            else:
                if source_files != None and isinstance(source_files, list):

                    logging.info("Copying sources...")

                    for source_file in source_files:

                        logging.info("    %(name)s" % {
                            'name': source_file
                            })

                        if (os.path.isfile(source_file)
                            and not os.path.islink(source_file)):

                            try:
                                shutil.copy(
                                    source_file, os.path.join(
                                        build_site_dir,
                                        org.wayround.aipsetup.buildingsite.DIR_TARBALL
                                        )
                                    )
                            except:
                                logging.exception("Couldn't copy source file")
                                ret = 4

                        else:

                            logging.error("file %(file)s - not dir and not file. skipping copy" % {
                                'file': source_file
                                })

                    if ret != 0:
                        logging.error("Exception while copying one of source files")

                if org.wayround.aipsetup.buildingsite.apply_info(
                    build_site_dir, source_files[0]
                    ) == 0:

                    if complete(build_site_dir) != 0:
                        logging.error("Package building failed")
                        ret = 5

    return ret

def complete(building_site):

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(building_site), 'buildingsite complete'
        )
    log.info("Buildingsite processes started")
    log.warning("Closing this log now, cause it can't work farther")
    log.stop()

    ret = 0

    if org.wayround.aipsetup.build.complete(building_site) != 0:
        logging.error("Error on building stage")
        ret = 1
    elif org.wayround.aipsetup.pack.complete(building_site) != 0:
        logging.error("Error on packaging stage")
        ret = 2

    return ret

def find_file_in_files_installed_by_asps(
    destdir, instr, mode=None, mute=False,
    return_dict=True
    ):

    ret = 0

    lst = list_installed_asps(
        destdir=destdir,
        mute=True
        )
    if not isinstance(lst, list):
        logging.error("Error getting installed packages list")
        ret = 1
    else:
        lst.sort()

        ret_dict = dict()

        for pkgname in lst:
            if pkgname.endswith('.xz'):
                pkgname = pkgname[:-3]

            found = find_file_in_files_installed_by_asp(
                destdir, pkgname, instr=instr,
                mode=mode,
                mute=True
                )

            if len(found) != 0:
                ret_dict[pkgname] = found

        if not mute:
            rd_keys = list(ret_dict.keys())
            if len(rd_keys) == 0:
                logging.info("Not found")
            else:
                logging.info("Found %(num)d packages with `%(inc)s'" % {
                    'num': len(rd_keys),
                    'inc': instr
                    })

                print("")
                rd_keys.sort()

                for i in rd_keys:
                    print("\t%(name)s:" % {
                        'name': i
                        })

                    pp_lst = ret_dict[i]
                    pp_lst.sort()

                    for j in pp_lst:
                        print("\t\t%(name)s" % {
                            'name': j
                            })

                    print("")

        if return_dict:
            ret = ret_dict

    return ret

def find_file_in_files_installed_by_asp(
    destdir, pkgname, instr, mode=None, mute=False
    ):

    ret = 0

    destdir = os.path.abspath(destdir)

    if not isinstance(instr, list):
        instr = [instr]

    if mode == None:
        mode = 'sub'

    if not mode in ['re', 'plain', 'sub', 'beg', 'fm']:
        logging.error("wrong mode")
        ret = 1
    else:

        if not pkgname.endswith('.xz'):
            pkgname += '.xz'

        pkg_file_list = list_files_installed_by_asp(
            destdir, pkgname
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
                        if re.match(j, i) != None:
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

                elif mode == 'fm':
                    for j in instr:
                        if fnmatch.fnmatch(i, j):
                            out_list.add(i)

            out_list = list(out_list)
            out_list.sort()

            ret = copy.copy(out_list)

    return ret


def put_files_to_index(files):

    for i in files:
        if os.path.exists(i):
            put_file_to_index(i)

    return 0

def _put_files_to_index(files, pkg_name, subdir):

    ret = 0

    repository_path = org.wayround.aipsetup.config.config['repository']


    for file in files:

        full_path = os.path.abspath(
            repository_path + os.path.sep + subdir
            )

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        logging.info("moving {}\n       to {}".format(file, full_path))
        shutil.move(file, full_path)

    return ret

def put_file_to_index(filename):
    ret = 0

    logging.info("Processing file `{}'".format(filename))

    if os.path.isdir(filename) or os.path.islink(filename):
        logging.error(
            "Wrong file type `{}'".format(filename)
            )
        ret = 10
    else:

        if check_package_aipsetup2(filename) == 0:

            parsed = org.wayround.aipsetup.name.package_name_parse(filename)

            if not isinstance(parsed, dict):
                logging.error(
                    "Can't parse file name {}".format(
                        os.path.basename(filename)
                        )
                    )
            else:
                file = os.path.abspath(filename)

                files = [
                    file,
                    file + '.sha512',
                    file + '.md5'
                    ]

                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    parsed['groups']['name']
                    ) + os.path.sep + 'aipsetup2'

                _put_files_to_index(files, parsed['groups']['name'], path)

        elif check_package(filename, mute=True) == 0:
            parsed = org.wayround.aipsetup.name.package_name_parse(filename)

            if not isinstance(parsed, dict):
                logging.error(
                    "Can't parse file name {}".format(
                        os.path.basename(filename)
                        )
                    )
            else:
                file = os.path.abspath(filename)

                files = [
                    file
                    ]

                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    parsed['groups']['name']
                    ) + os.path.sep + 'pack'

                _put_files_to_index(files, parsed['groups']['name'], path)

        else:

            logging.error("Don't know what to do with `{}'".format(filename))

    return ret
