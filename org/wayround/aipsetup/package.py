

"""
Module for UNIX system related package actions

 * install_asp into system;
 * list installed;
 * find issues;
 * remove from system;
 * completely build new package from source...
 etc.
"""

import copy
import fnmatch
import functools
import glob
import logging
import os.path
import re
import shutil
import sys
import tarfile
import tempfile


import org.wayround.utils.archive
import org.wayround.utils.checksum
import org.wayround.utils.deps_c
import org.wayround.utils.file
import org.wayround.utils.format.elf
import org.wayround.utils.format.elf_enum
import org.wayround.utils.log
import org.wayround.utils.opts
import org.wayround.utils.path
import org.wayround.utils.text
import org.wayround.utils.time


import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.config
import org.wayround.aipsetup.name
import org.wayround.aipsetup.pack
import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.pkginfo
import org.wayround.aipsetup.sysupdates


ROOT_LINKS = [
    os.path.sep + 'bin',
    os.path.sep + 'sbin',
    os.path.sep + 'lib',
    os.path.sep + 'lib64'
    ]

def cli_name():
    return 'pkg'


def exported_commands():
    return {
        'check'         : package_check_package,
        'install'       : package_install,
        'list'          : package_list,
        'list_asps'     : package_list_asps,
        'remove'        : package_remove,
        'complete'      : package_complete,
        'build'         : package_build,
        'find'          : package_find_files,
        'index'         : package_put_to_index_many,
        'so_problems'   : package_find_so_problems
        }

def commands_order():
    return [
        'check',
        'list',
        'list_asps',
        'install',
        'remove',
        'complete',
        'build',
        'index',
        'find',
        'so_problems'
        ]

def package_install(opts, args):
    """
    Install package(s)

    [-b=DIRNAME] [--force] NAMES

    If -b is given - it is used as destination root
    """

    ret = org.wayround.utils.opts.is_wrong_opts(
        opts,
        ['-b', '--force']
        )

    if ret == 0:

        basedir = '/'
        if '-b' in opts:
            basedir = opts['-b']

        force = '--force' in opts

        if len(args) == 0:
            logging.error("Package name(s) required!")
            ret = 2
        else:
            names = args

            for name in names:
                ret = install_package(
                    name, force, basedir
                    )
                if ret != 0:
                    logging.error("Some package's installation error -- see above")
                    break

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
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    )
                )

            for i in lst:
                print("    {}".format(i))

    return ret


def package_remove(opts, args):
    """
    Removes package matching NAME.

    [-b=DIRNAME] [--force] NAME

    --force    force removal of packages for which info is not
               available or which is not removable
    """

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

    [DIRNAME] [TARBALL]

    [DIRNAME1] [DIRNAME2] [DIRNAMEn]

    This command has two modes of work:

       1. Working with single dir, which is pointed or not pointed by
          first parameter. In this mode, a tarball can be passed,
          which name will be used to apply new package info to pointed
          dir. By default DIRNAME is `.' (current dir)

       2. Working with multiple dirs. In this mode, tarball can't be
          passed.

    options:

    -d - remove buildingsite on success
    """

    dirname = '.'
    file = None

    r_bds = '-d' in opts


    ret = 0

    args_l = len(args)

    if args_l == 0:

        dirname = '.'
        file = None

        ret = complete(
            dirname, file, remove_buildingsite_after_success=r_bds
            )

    elif args_l == 1:

        if os.path.isdir(args[0]):

            dirname = args[0]
            file = None

        elif os.path.isfile(args[0]):

            dirname = '.'
            file = args[0]

        else:

            logging.error("{} not a dir and not a file".format())
            ret = 2

        if ret == 0:

            ret = complete(
                dirname, file, remove_buildingsite_after_success=r_bds
                )

    elif args_l == 2:

        if os.path.isdir(args[0]) and os.path.isfile(args[1]):

            dirname = args[0]
            file = args[1]

            ret = complete(
                dirname, file, remove_buildingsite_after_success=r_bds
                )

        elif os.path.isdir(args[0]) and os.path.isdir(args[1]):

            file = None
            ret = 0
            for i in args[:2]:
                if complete(i, file, remove_buildingsite_after_success=r_bds) != 0:
                    ret += 1

        else:
            logging.error("Wrong arguments")


    elif args_l > 2:

        file = None

        ret = 0
        for i in args[2:]:
            if complete(i, file, remove_buildingsite_after_success=r_bds) != 0:
                ret += 1

    else:
        raise Exception("Programming error")

    return ret

def package_build(opts, args):
    """
    Place named source files in new building site and build new
    package from them.

    [-o] TARBALL[, TARBALL[, TARBALL[, TARBALL...]]]

    -o 	    treat all tarballs as for one build.
    -d      remove buildingsite on success

    """

    r_bds = '-d' in opts

    sources = []

    multiple_packages = not '-o' in opts

    ret = 0

    org.wayround.aipsetup.config.config['buildingsites'] = (
        os.getcwd()
        )

    if len(args) > 0:
        sources = args

    if len(sources) == 0:
        logging.error("No source files named")
        ret = 2

    if ret == 0:

        if multiple_packages:
            sources.sort()
            for i in sources:
                build([i], remove_buildingsite_after_success=r_bds)
            ret = 0
        else:
            ret = build(sources, remove_buildingsite_after_success=r_bds)

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
        basedir, lookfor, mode=look_meth
        )

    if isinstance(ret, dict):

        rd_keys = list(ret.keys())
        if len(rd_keys) == 0:
            logging.info("Not found")
        else:
            logging.info(
                "Found {num} packages with `{inc}'".format_map(
                    {
                        'num': len(rd_keys),
                        'inc': lookfor
                        }
                    )
                )

            print("")
            rd_keys.sort()

            for i in rd_keys:
                print("\t{}:".format(i))

                pp_lst = ret[i]
                pp_lst.sort()

                for j in pp_lst:
                    print("\t\t{}".format(j))

                print("")
        ret = 0

    else:
        ret = 1

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

def package_check_package(opts, args):
    ret = 0
    file = None

    if len(args) == 1:
        file = args[0]

    if file == None:
        logging.error("Filename required")
        ret = 2

    else:

        ret = check_package(file)
    return ret

def package_find_so_problems(opts, args):
    """
    Find so libraries missing in system and write package names
    requiring those missing libraries.
    """
    ret = 0

    basedir = '/'
#    if '-b' in opts:
#        basedir = opts['-b']

    problems = org.wayround.utils.deps_c.find_so_problems_in_linux_system()

    libs = list(problems.keys())
    libs.sort()

    log = org.wayround.utils.log.Log(
        os.getcwd(), 'problems'
        )

    print("Writing log to {}".format(log.log_filename))

    logging.info("Gathering asps file tree. Please wait...")
    tree = list_installed_asps_and_their_files(basedir, mute=False)
    logging.info("Now working")

    total_problem_packages_list = set()

    count_checked = 0
    libs_c = len(libs)
    for i in libs:
        log.info("Library `{}' required by following files:".format(i))

        files = problems[i]
        files.sort()

        for j in files:
            log.info("    {}".format(j))


        pkgs2 = find_file_in_files_installed_by_asps(
            basedir, files, mode='end', mute=False, predefined_asp_tree=tree
            )

        pkgs2_l = list(pkgs2.keys())
        pkgs2_l.sort()

        count_checked += 1

        log.info("  Contained in problem packages:")
        for j in pkgs2_l:
            log.info("    {}".format(j))

        total_problem_packages_list |= set(pkgs2_l)

        logging.info("Checked libraries: {} of {}".format(count_checked, libs_c))
        log.info('---------------------------------')

    pkgs = find_file_in_files_installed_by_asps(
        basedir, libs, mode='end', mute=False, predefined_asp_tree=tree
        )

    pkgs_l = list(pkgs.keys())
    pkgs_l.sort()

    log.info('')
    log.info("Libs found in packages:")
    for i in pkgs_l:
        log.info("    {}".format(i))

    log.info('')

    log.info("Total Problem Packages List:")
    total_problem_packages_list = list(total_problem_packages_list)
    total_problem_packages_list.sort()
    for i in total_problem_packages_list:
        log.info("    {}".format(i))

    log.stop()
    print("Log written to {}".format(log.log_filename))

    return ret

def check_package(asp_name, mute=False):
    """
    Check package for errors
    """
    ret = 0

    asp_name = org.wayround.utils.path.abspath(asp_name)

    if not asp_name.endswith('.asp'):
        if not mute:
            logging.error("Wrong file extension `{}'".format(asp_name))
        ret = 3
    else:
        try:
            tarf = tarfile.open(asp_name, mode='r')
        except:
            logging.exception("Can't open file `{}'".format(asp_name))
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

                    check_list = [
                        './04.DESTDIR.tar.xz', './05.BUILD_LOGS.tar.xz',
                        './package_info.json', './02.PATCHES.tar.xz'
                        ]

                    for i in ['./00.TARBALL', './06.LISTS']:
                        for j in tar_members:
                            if (
                                j.name.startswith(i)
                                and j.name != i
                                ):
                                check_list.append(j.name)

                    check_list.sort()

                    error_found = False

                    for i in check_list:
                        cresult = ''
                        if (
                            not i in sums
                            or tarobj_check_member_sum(tarf, sums, i) == False
                            ):
                            error_found = True
                            cresult = "FAIL"
                        else:
                            cresult = "OK"

                        if not mute:
                            print(
                                "       {name} - {result}".format_map(
                                    {
                                        'name': i,
                                        'result': cresult
                                        }
                                    )
                                )

                    if error_found:
                        logging.error("Error was found while checking package")
                        ret = 3
                    else:

                        # TODO: additionally to this leaf, make test
                        #       by tar -t output

                        fobj = org.wayround.utils.archive.tar_member_get_extract_file(
                            tarf,
                            './06.LISTS/DESTDIR.lst.xz'
                            )
                        if not isinstance(fobj, tarfile.ExFileObject):
                            ret = False
                        else:

                            try:
                                dest_dir_files_list = org.wayround.utils.archive.xzcat(
                                    fobj,
                                    convert_to_str='utf-8'
                                    )
                                dest_dir_files_list = dest_dir_files_list.splitlines()

                                for i in [
                                    'bin',
                                    'sbin',
                                    'lib',
                                    'lib64'
                                    ]:

                                    for j in dest_dir_files_list:

                                        p1 = os.path.sep + i + os.path.sep
                                        p2 = os.path.sep + i

                                        if j.startswith(p1):
                                            logging.error(
                                                "{} has file paths starting with {}".format(
                                                    os.path.basename(asp_name),
                                                    p1
                                                    )
                                                )
                                            ret = 5
                                            break

                                        elif j == p2:
                                            logging.error(
                                                "{} has file paths equal to {}".format(
                                                    os.path.basename(asp_name),
                                                    p2
                                                    )
                                                )
                                            ret = 5
                                            break

                                        if ret != 0:
                                            break

                            except:
                                logging.exception("Error")
                                ret = 4
                            finally:
                                fobj.close()
            finally:
                tarf.close()

    return ret

def check_package_aipsetup2(filename):

    ret = 0

    filename = org.wayround.utils.path.abspath(filename)
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

    info = org.wayround.aipsetup.pkginfo.get_package_info_record(
        name
        )

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
                key=functools.cmp_to_key(
                    org.wayround.aipsetup.version.package_version_comparator
                    )
                )

            if not mute:
                print("Following packages will be removed:")
                for i in lst:
                    print("    {}".format(i))

            for i in lst:

                name = org.wayround.aipsetup.name.rm_ext_from_pkg_name(i)

                if not mute:
                    logging.info("Removing package `{}'".format(name))
                remove_asp(name, destdir)

    return ret

def install_package(
    name, force=False, destdir='/'
    ):

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
            if isinstance(name_parsed, dict):
                info = org.wayround.aipsetup.pkginfo.get_package_info_record(
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
                        if isinstance(info, dict):
                            if info['reducible']:
                                logging.info(
                                    "Reducing `{}' ASPs".format(
                                        name_parsed['groups']['name']
                                        )
                                    )
                                reduce_asps(name, asps, destdir)
                                logging.info(
                                    "Reduced `{}' ASPs".format(
                                        name_parsed['groups']['name']
                                        )
                                    )

    else:
        info = org.wayround.aipsetup.pkginfo.get_package_info_record(
            name
            )

        if not isinstance(info, dict):
            logging.error("Don't know about package")
            ret = 2
        else:

            latest_in_repo = (
                org.wayround.aipsetup.pkglatest.get_latest_pkg_from_record(name)
                )

            if latest_in_repo == None:
                logging.error("Repo has no latest package")
                ret = 3
            else:

                full_name = org.wayround.utils.path.abspath(
                    org.wayround.aipsetup.config.config['repository'] +
                    os.path.sep +
                    latest_in_repo
                    )

                ret = install_package(full_name, False, destdir)


    return ret

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

    destdir = org.wayround.utils.path.abspath(destdir)

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

            package_name = os.path.basename(asp_name)
            if org.wayround.aipsetup.name.package_name_parse(package_name) == None:
                logging.error("Can't parse package name `{}'".format(package_name))
                ret = 2
            else:
                package_name = package_name[:-4]
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

                    logs_path = ''
                    if org.wayround.aipsetup.config.config[i[1]][0] == '/':
                        logs_path = org.wayround.aipsetup.config.config[i[1]][1:]
                    else:
                        logs_path = org.wayround.aipsetup.config.config[i[1]]

                    out_filename = (
                        org.wayround.utils.path.abspath(
                            os.path.join(
                                destdir,
                                logs_path,
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

                    if org.wayround.utils.archive.tar_member_get_extract_file_to(
                            tarf,
                            i[0],
                            out_filename
                            ) != 0 :
                        logging.error(
                            "Can't install asp {} as {}".format(i[2], out_filename)
                            )
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
                        try:
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
                                logging.info("Installed `{}' ;-)".format(package_name))
                        finally:
                            dd_fobj.close()

                if ret == 0:
                    logging.info("Post installation file ownerships and modes fix")
                    files = []
                    dirs = []

                    installed_file_list = org.wayround.utils.archive.\
                        tar_member_get_extract_file(
                            tarf, './06.LISTS/DESTDIR.lst.xz'
                            )
                    if not isinstance(installed_file_list, tarfile.ExFileObject):
                        logging.error("Can't get package's file list")
                        ret = 10
                    else:
                        try:
                            text_lst = org.wayround.utils.archive.xzcat(
                                installed_file_list, convert_to_str='utf-8'
                                )

                            files = text_lst.split('\n')

                            files = org.wayround.utils.list.filelist_strip_remove_empty_remove_duplicated_lines(files)
                            files.sort()

                            dirs = set()
                            for i in files:
                                dirs.add(os.path.dirname(i))
                            dirs = list(dirs)
                            dirs.sort()

                            for i in dirs:
                                f_d_p = org.wayround.utils.path.abspath(destdir + os.path.sep + i)


                                if not os.path.islink(f_d_p):
                                    os.chown(f_d_p, 0, 0)
                                    os.chmod(f_d_p, 0o755)

                            for i in files:
                                f_f_p = org.wayround.utils.path.abspath(destdir + os.path.sep + i)


                                if not os.path.islink(f_f_p):
                                    os.chown(f_f_p, 0, 0)
                                    os.chmod(f_f_p, 0o755)
                        finally:
                            installed_file_list.close()

                if ret == 0:
                    logging.info("Searching post installation script")

                    script_obj = \
                        org.wayround.utils.archive.tar_member_get_extract_file(
                            tarf, './post_install.py'
                            )

                    if not isinstance(script_obj, tarfile.ExFileObject):
                        logging.info("Can't get package's post installation script")
                    else:
                        try:
                            script_txt = script_obj.read()

                            g = {}
                            l = g
                            try:
                                exec(
                                    compile(
                                        script_txt,
                                        None,
                                        'exec'
                                        ),
                                    g,
                                    l
                                    )
                            except:
                                logging.exception(
                                    "Can't load package's post installation script"
                                    )
                                ret = 7

                            else:
                                if l['main'](destdir) != 0:
                                    logging.error("Post installation script main function returned error")
                                    ret = 8
                        finally:
                            script_obj.close()


            tarf.close()

    return ret

def remove_asp(
    asp_name,
    destdir='/',
    only_remove_package_registration=False,
    exclude=None,
    mute=False
    ):

    """
    Removes named asp from destdir system.

    exclude - can be None or list of files which is NOT PREPENDED WITH DESTDIR
    """

    exclude = copy.copy(exclude)

    ret = 0

    # ensure destdir correctness
    destdir = org.wayround.utils.path.abspath(destdir)

    lines = list_files_installed_by_asp(destdir, asp_name, mute)

    if not isinstance(lines, list):
        logging.error(
            "Some errors while getting ASP's file list for `{}'".format(
                asp_name
                )
            )
        ret = 1
    else:

        # from this point we working with other systems' files
        lines = org.wayround.utils.path.prepend_path(lines, destdir)

        lines = org.wayround.utils.path.realpaths(lines)

        logging.info("Removing `{}' files".format(asp_name))

        if not only_remove_package_registration:

            if exclude:

                # Some files need to be excluded from removal operation

                lines_before_ex = len(lines)

                exclude = org.wayround.utils.path.prepend_path(exclude, destdir)

                exclude = org.wayround.utils.path.realpaths(exclude)

                lines = list(set(lines) - set(exclude))

                # exclude from removal files starting with one of the ROOT_LINKS
                # lines, which have corresponding file in /usr-prependet dir

                # This is no longer needed as we working only with real paths
                # (which excludes duplications), and excluding Sahred Object
                # files (ET_DYN) little farther

                #                for line in lines[:]:
                #
                #                    for i in ROOT_LINKS:
                #                        if line.startswith(i + os.path.sep):
                #                            if (os.path.sep + 'usr' + line) in exclude:
                #
                #                                while line in lines:
                #                                    lines.remove(line)

                # Statistics about excluded files
                lines_after_ex = len(lines)

                if lines_before_ex != lines_after_ex:
                    logging.info(
                        "Excluded {} new files".format(
                            lines_before_ex - lines_after_ex
                            )
                        )

            # prevent removal of /bin, /sbin, /lib, /lib64 symlinks
            #            for line in lines[:]:
            #
            #                if line in ROOT_LINKS:
            #                    while line in lines:
            #                        lines.remove(line)

            logging.info("Excluding shared objects")
            shared_objects = set()
            for i in lines:
                if os.path.isfile(i):
                    if (org.wayround.utils.format.elf.get_elf_file_type(i) ==
                        org.wayround.utils.format.elf.ET_DYN):
                        shared_objects.add(i)

            # this not needed and lines (at this point) already have no
            # excluded files. but i leave this line just to accent
            if exclude:
                shared_objects -= set(exclude)

            shared_objects_tl = list(shared_objects)
            shared_objects_tl.sort()

            for i in shared_objects_tl:
                logging.info("    excluded {}".format(i))

            del(shared_objects_tl)


            lines = list(set(lines) - set(shared_objects))

            logging.info(
                "Excluded {} shared objects".format(
                    len(shared_objects)
                    )
                )


            lines.sort(reverse=True)

            for line in lines:

                rm_file_name = org.wayround.utils.path.abspath(
                    line
                    )


                if (
                    (os.path.islink(rm_file_name) and not os.path.exists(rm_file_name))
                    or
                    (os.path.isfile(rm_file_name))
                    or
                    (os.path.isdir(rm_file_name) and org.wayround.utils.file.is_dir_empty(rm_file_name))
                    ):
                    if not mute:
                        logging.info("   removing: {}".format(rm_file_name))

                    if os.path.isfile(rm_file_name) or os.path.islink(rm_file_name):

                        try:
                            os.unlink(rm_file_name)
                        except:
                            logging.exception(
                                "Couldn't remove file: {}".format(rm_file_name)
                                )
                    else:
                        try:
                            os.rmdir(rm_file_name)
                        except:
                            logging.exception(
                                "Couldn't remove dir: {}".format(rm_file_name)
                                )

        if len(shared_objects) != 0:

            if not os.path.exists(destdir + os.path.sep +
                org.wayround.aipsetup.config.config['installed_pkg_dir_removing']):

                os.makedirs(destdir + os.path.sep +
                    org.wayround.aipsetup.config.config['installed_pkg_dir_removing'])

            mv_file_name1 = org.wayround.utils.path.abspath(
                destdir + os.path.sep +
                org.wayround.aipsetup.config.config['installed_pkg_dir'] +
                os.path.sep +
                asp_name + '.xz'
                )
            mv_file_name2 = org.wayround.utils.path.abspath(
                destdir + os.path.sep +
                org.wayround.aipsetup.config.config['installed_pkg_dir_removing'] +
                os.path.sep +
                asp_name + '.xz'
                )
            if os.path.isfile(mv_file_name1):
                logging.info("   reserving: {}".format(mv_file_name1))
                os.rename(mv_file_name1, mv_file_name2)


            logging.warning("asp `{}' \n"
                "    was moved to delayed removal dir,\n"
                "    because {} of it's shared object elf files\n"
                "    remained undeleted".format(asp_name, len(shared_objects)))
        else:
            for i in [
                'installed_pkg_dir_buildlogs',
                'installed_pkg_dir_sums',
                'installed_pkg_dir'
                ]:
                rm_file_name = org.wayround.utils.path.abspath(
                    destdir + os.path.sep +
                    org.wayround.aipsetup.config.config[i] + os.path.sep +
                    asp_name + '.xz'
                    )
                if os.path.isfile(rm_file_name):
                    logging.info("   removing: {}".format(rm_file_name))
                    os.unlink(rm_file_name)
    return ret

def reduce_asps(reduce_to, reduce_what=None, destdir='/', mute=False):

    ret = 0

    if not isinstance(reduce_what, list):
        raise ValueError("reduce_what must be a list of strings")

    reduce_to = os.path.basename(reduce_to)
    reduce_to = (
        org.wayround.aipsetup.name.rm_ext_from_pkg_name(reduce_to)
        )

    for i in range(len(reduce_what)):
        reduce_what[i] = os.path.basename(reduce_what[i])
        reduce_what[i] = (
            org.wayround.aipsetup.name.rm_ext_from_pkg_name(
                reduce_what[i]
                )
            )

    if reduce_to in reduce_what:
        reduce_what.remove(reduce_to)

    if destdir != '/':
        if not mute:
            logging.info("Destdir: {}".format(destdir))

    fiba = list_files_installed_by_asp(destdir, reduce_to)

    if not isinstance(fiba, list):
        logging.error(
            "Some error getting list of files installed by {}".format(reduce_to)
            )
        ret = 1
    else:

        for i in reduce_what:
            remove_asp(
                i,
                destdir,
                exclude=fiba
                )

    return ret


def list_installed_asps(destdir='/', mute=False):
    destdir = org.wayround.utils.path.abspath(destdir)

    listdir = org.wayround.utils.path.abspath(destdir + org.wayround.aipsetup.config.config['installed_pkg_dir'])
    filelist = glob.glob(os.path.join(listdir, '*.xz'))

    ret = 0

    if not os.path.isdir(listdir):
        logging.error("not a dir {}".format(listdir))
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

def list_installed_asps_and_their_files(destdir='/', mute=True):

    lst = list_installed_asps(destdir, mute)

    ret = dict()

    for i in lst:
        ret[i] = list_files_installed_by_asp(destdir, i, mute)

#    pprint.pprint(ret)
#    exit(0)
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

def latest_installed_package_s_asp(name, destdir='/'):

    lst = list_installed_package_s_asps(name, destdir)

    ret = None
    if len(lst) > 0:
        latest = max(
            lst,
            key=functools.cmp_to_key(
                org.wayround.aipsetup.version.package_version_comparator
                )
            )

        ret = latest

    return ret

def list_installed_package_s_asps(name_or_list, destdir='/'):

    ret = {}

    return_single = False
    if isinstance(name_or_list, str):
        return_single = True
        name_or_list = [name_or_list]

    asps_list = list_installed_asps(destdir=destdir, mute=True)
    asps_list_parsed = {}

    for i in asps_list:
        asps_list_parsed[i] = org.wayround.aipsetup.name.package_name_parse(
            i,
            mute=True
            )

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
        destdir, asp_name, mute=True
        ):
    """
    Reads list of files installed by named asp.

    Destdir is not prependet to the list's items. Do it yuorself if needed.
    """
    ret = 0

    destdir = org.wayround.utils.path.abspath(destdir)

    list_dir = org.wayround.utils.path.abspath(
        destdir + os.path.sep + org.wayround.aipsetup.config.config['installed_pkg_dir']
        )

    pkg_list_file = os.path.join(list_dir, asp_name)

    if not pkg_list_file.endswith('.xz'):
        pkg_list_file += '.xz'

    try:
        f = open(pkg_list_file, 'rb')
    except:
        logging.exception("Can't open list file `{}'".format(pkg_list_file))
        ret = 2
    else:

        pkg_file_list = org.wayround.utils.archive.xzcat(
            f, convert_to_str=True
            )

        f.close()

        pkg_file_list = pkg_file_list.splitlines()
        pkg_file_list = (
            org.wayround.utils.list.filelist_strip_remove_empty_remove_duplicated_lines(pkg_file_list)
            )


        pkg_file_list.sort()

        ret = copy.copy(pkg_file_list)

    return ret


def build(source_files, remove_buildingsite_after_success=False):
    ret = 0

    par_res = org.wayround.aipsetup.name.source_name_parse(
        source_files[0],
        mute=True
        )


    if not isinstance(par_res, dict):
        logging.error("Can't parse source file name")
        ret = 1
    else:

        try:
            os.makedirs(org.wayround.aipsetup.config.config['buildingsites'])
        except:
            pass

        package_info = org.wayround.aipsetup.pkginfo.get_info_rec_by_tarball_filename(
            source_files[0]
            )

        if not package_info:
            logging.error(
                "Can't find package information for tarball `{}'".format(
                    source_files[0]
                    )
                )
            ret = 2
        else:

            tmp_dir_prefix = "{name}-{version}-{status}-{timestamp}-".format_map(
                {
                    'name': package_info['name'],
                    'version': par_res['groups']['version'],
                    'status': par_res['groups']['status'],
                    'timestamp': org.wayround.utils.time.currenttime_stamp()
                    }
                )

            build_site_dir = tempfile.mkdtemp(
                prefix=tmp_dir_prefix,
                dir=org.wayround.aipsetup.config.config['buildingsites']
                )
            build_site_dir = org.wayround.utils.path.abspath(build_site_dir)

            if org.wayround.aipsetup.buildingsite.init(build_site_dir) != 0:
                logging.error("Error initiating temporary dir")
                ret = 3
            else:
                if source_files != None and isinstance(source_files, list):

                    logging.info("Copying sources...")

                    for source_file in source_files:

                        logging.info("    {}".format(source_file))

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

                            logging.error(
                                "file {} - not dir and not file. skipping copy".format(
                                    source_file
                                    )
                                )

                    if ret != 0:
                        logging.error("Exception while copying one of source files")

                if ret == 0:

                    # FIXME: rework this
                    if complete(
                        build_site_dir,
                        source_files[0],
                        remove_buildingsite_after_success=remove_buildingsite_after_success
                        ) != 0:

                        logging.error("Package building failed")
                        ret = 5

    return ret

def _complete_info_correctness_check(workdir):

    ret = 0

    r = org.wayround.aipsetup.buildingsite.read_package_info(
        workdir, {}
        )

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
    building_site,
    main_src_file=None,
    remove_buildingsite_after_success=False
    ):

    rp = org.wayround.utils.path.relpath(building_site, os.getcwd())

    logging.info(
        "+++++++++++ Starting Complete build in `{}' +++++++++++".format(rp)
        )

    building_site = org.wayround.utils.path.abspath(building_site)

    ret = 0

    if (_complete_info_correctness_check(building_site) != 0
        or
        isinstance(main_src_file, str)
        ):

        logging.warning("buildscript information not available (or new main tarball file forced)")

        if org.wayround.aipsetup.buildingsite.apply_info(
            building_site,
            main_src_file
            ) != 0 :
            logging.error("Can't apply build information to site")
            ret = 15

    if ret == 0:
        if _complete_info_correctness_check(building_site) != 0:

            logging.error("`{}' has wrong build script name".format(main_src_file))
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

def find_file_in_files_installed_by_asps(
    destdir, instr, mode=None, mute=False, sub_mute=True, predefined_asp_tree=None
    ):
    """
    instr can be a single query or list of queries.
    """

    ret = 0

    lst = []
    if predefined_asp_tree:
        lst = list(predefined_asp_tree.keys())
    else:
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

        lst_l = len(lst)
        lst_i = 0

        for pkgname in lst:

            if pkgname.endswith('.xz'):
                pkgname = pkgname[:-3]

            predefined_file_list = None
            if predefined_asp_tree:
                predefined_file_list = predefined_asp_tree[pkgname + '.xz']

            found = find_file_in_files_installed_by_asp(
                destdir, pkgname, instr=instr,
                mode=mode,
                mute=sub_mute,
                predefined_file_list=predefined_file_list
                )

            if len(found) != 0:
                ret_dict[pkgname] = found

            if not mute:

                lst_i += 1

                perc = 0
                if lst_i == 0:
                    perc = 0.0
                else:
                    perc = 100.0 / (float(lst_l) / float(lst_i))

                org.wayround.utils.file.progress_write(
                    "    {:6.2f}% (found {} packages) ({})".format(
                        perc,
                        len(ret_dict.keys()),
                        pkgname
                        )
                    )

        if not mute:
            org.wayround.utils.file.progress_write_finish()

        ret = ret_dict

    return ret

def find_file_in_files_installed_by_asp(
    destdir, pkgname, instr, mode=None, mute=False, predefined_file_list=None
    ):
    """
    instr can be a single query or list of queries.
    """

    ret = 0

    destdir = org.wayround.utils.path.abspath(destdir)

    if not isinstance(instr, list):
        instr = [instr]

    if mode == None:
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

                elif mode == 'end':
                    for j in instr:
                        if i.endswith(j):
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

def _put_files_to_index(files, subdir):

    ret = 0

    repository_path = org.wayround.aipsetup.config.config['repository']


    for file in files:

        full_path = org.wayround.utils.path.abspath(
            repository_path + os.path.sep + subdir
            )

        if not os.path.exists(full_path):
            os.makedirs(full_path)

        if os.path.dirname(file) != full_path:

            logging.info("Moving {}\n       to {}".format(os.path.basename(file), full_path))
            sfile = full_path + os.path.sep + os.path.basename(file)
            if os.path.isfile(sfile):
                os.unlink(sfile)
            shutil.move(file, full_path)

    return ret

def put_file_to_index(filename):
    ret = 0

    logging.info("Processing file `{}'".format(os.path.basename(filename)))

    if os.path.isdir(filename) or os.path.islink(filename):
        logging.error(
            "Wrong file type `{}'".format(filename)
            )
        ret = 10
    else:

        if check_package(filename, mute=True) == 0:
            parsed = org.wayround.aipsetup.name.package_name_parse(filename)

            if not isinstance(parsed, dict):
                logging.error(
                    "Can't parse file name {}".format(
                        os.path.basename(filename)
                        )
                    )
            else:
                file = org.wayround.utils.path.abspath(filename)

                files = [
                    file
                    ]


                package_path = org.wayround.aipsetup.pkgindex.get_package_path_string(
                    parsed['groups']['name']
                    )

                if not isinstance(package_path, str):
                    logging.error("Package path error `{}'".format(parsed['groups']['name']))
                    ret = 11
                else:

                    path = package_path + os.path.sep + 'pack'

                    if not isinstance(path, str):
                        logging.error(
                            "Can't get package `{}' path string".format(
                                parsed['groups']['name']
                                )
                            )
                        ret = 12
                    else:
                        _put_files_to_index(files, path)

        else:

            logging.error("Action indefined for `{}'".format(os.path.basename(filename)))

    return ret

def list_installed_packages_and_asps(destdir='/'):

    packages = list_installed_packages(mute=True, destdir=destdir)

    ret = list_installed_package_s_asps(packages, destdir=destdir)

    return ret


def check_list_of_installed_packages_and_asps(in_dict):

    ret = 0

    keys = list(in_dict.keys())

    keys.sort()

    errors = 0

    for i in keys:

        if len(in_dict[i]) > 1:

            errors += 1
            ret = 1

            logging.warning("Package with too many ASPs found `{}'".format(i))

            in_dict[i].sort()

            for j in in_dict[i]:

                print("       {}".format(j))

    if errors > 0:
        logging.warning("Total erroneous packages: {}".format(errors))

    return ret


def get_asps_depending_on_asp(destdir, asp_name, mute):

    files = list_files_installed_by_asp(destdir, asp_name, mute)

    files = org.wayround.utils.path.prepend_path(files, destdir)

    files = org.wayround.utils.path.realpaths(files)

    elf_files = []

    # FIXME: finish

