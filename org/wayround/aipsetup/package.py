
"""
Module for system related package actions

 * install into system;
 * list installed;
 * find issues;
 * remove from system;
 * completely build new package from source...
 etc.
"""

import sys
import os.path
import tarfile
import glob
import tempfile
import shutil
import copy
import re
import fnmatch
import logging


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


def exported_commands():
    return {
        'install'       : package_install,
        'list'          : package_list,
        'named_list'    : package_named_list,
        'issues'        : package_issues,
        'remove'        : package_remove,
        'complete'      : package_complete,
        'build'         : package_build,
        'find_files'    : package_find_files,
        'put_to_index'  : package_put_to_index_many
        }

def commands_order():
    return [
        'list',
        'named_list',
        'install',
        'remove',
        'issues',
        'complete',
        'build',
        'find_files',
        'put_to_index'
        ]

def package_install(opts, args):
    """
    [-b=DIRNAME] FILE

    Install package. If -b is given - it is used as root
    """

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    if len(args) == 0:
        logging.error("Package name required!")
        ret = 2
    else:
        asp_name = args[0]
        ret = install(asp_name, basedir)

    return ret

def package_list(opts, args):
    """
    List installed packages.

    [-b=DIRNAME] [MASK]

    -b is same as in install.
    Default MASK is *.xz
    """

    ret = 0

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    asp_name = '*.xz'
    if len(args) > 0:
        asp_name = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if ret == 0:
        ret = list_installed_packages(asp_name, basedir)

    return ret

def package_named_list(opts, args):
    """
    List installations with name PACKAGE_NAME

    [-b=DIRNAME] PACKAGE_NAME

    -b is same as in install
    """

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    asp_name = None
    if len(args) > 0:
        asp_name = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if not isinstance(asp_name, str):
        logging.error("package name required")
        ret = 3

    if ret == 0:
        ret = named_list_packages(asp_name, basedir)

    return 0

def package_issues(opts, args):
    """
    Looks for issues with already installed package names

    [-b=DIRNAME]

        * list unparsabel names
        * list names not in info files directory
    """

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if ret == 0:
        list_packages_issues(basedir)


    return 0

def package_remove(opts, args):
    """
    Removes packages matching MASK.

    [-b=DIRNAME] MASK

    WARNING: no sanity checks!
        aipsetup package remove '*'
        will remove everything (unless system will crushes
        before is't finished)

    WARNING: removes any installed config files!
        do all necessary config backups before remove!
    """

    basedir = '/'
    if '-b' in opts:
        basedir = opts['-b']

    asp_name = None
    if len(args) > 0:
        asp_name = args[0]

    if not isinstance(basedir, str):
        logging.error("given basedir name is wrong")
        ret = 2

    if not isinstance(asp_name, str):
        logging.error("removing name mask must be not empty!")
        ret = 3

    if ret == 0:
        ret = remove_packages(asp_name, basedir)

    return 0

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

    ret = find_files(basedir, lookfor, mode=look_meth,
                     mute=False,
                     return_dict=False)

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
        ret = put_to_index_many(files)

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
                                  './package_info.py', './02.PATCHES.tar.xz']

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

def install(asp_name, destdir='/'):

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
            logging.exception("Can't open file %(name)s")
            ret = 1
        else:

            package_name = asp_name[:-4]

            for i in [
                ('./06.LISTS/DESTDIR.lst.xz',
                 'installed_pkg_dir',
                 "package's file list"),
                ('./06.LISTS/DESTDIR.sha512.xz',
                 'installed_pkg_dir_sums',
                 "package's check sums"),
                ('./05.BUILD_LOGS.tar.xz',
                 'installed_pkg_dir_buildlogs',
                 "package's buildlogs")
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

                if org.wayround.utils.archive.\
                    tar_member_get_extract_file_to(
                        tarf, i[0], out_filename
                        ) != 0 :
                    logging.error("Can't install %(what)s as %(outname)s" % {
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
                    if org.wayround.utils.archive.\
                        extract_tar_canonical_fobj(
                            dd_fobj, destdir, 'xz',
                            verbose_tar=True,
                            verbose_compressor=True,
                            add_tar_options=['--no-same-owner', '--no-same-permissions']
                            ) != 0:
                        logging.error("Package destdir decompression error")
                        ret = 5
                    else:
                        ret = 0
                        logging.info("Installation look like complite :-)")
                    dd_fobj.close()

            tarf.close()

    return ret

def list_packages_issues(destdir='/'):
    installed_packages_list = list_installed_packages('*', destdir=destdir, return_list=True)

    info_dir = os.path.abspath(org.wayround.aipsetup.config.config['info'])

    check_list = set()

    issued = set()

    for i in installed_packages_list:

        name = ''

        if not i.endswith('.xz'):
            name = i
        else:
            name = i[:-3]

        parsed_name = org.wayround.aipsetup.name.package_name_parse(name)
        if parsed_name == None:
            logging.warning("Error while parsing name `%(name)s'" % {
                'name': name
                })
        else:
            check_list.add(parsed_name['groups']['name'])

    check_list = list(check_list)
    check_list.sort()
    for i in check_list:
        info_file = os.path.join(
            info_dir, i + '.xml'
            )
        if not isinstance(org.wayround.aipsetup.info.read_from_file(info_file), dict):
            logging.warning("Some issue with `%(name)s' info file" % {
                'name': i
                })
            issued.add(i)

    issued = list(issued)
    issued.sort()
    logging.info("Found issues with following (%(num)d) packages:" % {
        'num': len(issued)
        })
    org.wayround.utils.text.columned_list_print(
        issued, fd=sys.stdout.fileno()
    )

    return

def named_list_packages(asp_name, destdir='/'):
    lst = list_installed_packages('*', destdir=destdir, return_list=True)

    out_list = []

    for i in lst:

        name = ''

        if not i.endswith('.xz'):
            name = i
        else:
            name = i[:-3]

        parsed_name = org.wayround.aipsetup.name.package_name_parse(name)
        if parsed_name == None:
            pass
        else:
            #print repr(parsed_name)
            if parsed_name['groups']['name'] == asp_name:
                out_list.append(name)

    org.wayround.utils.text.columned_list_print(
        out_list, fd=sys.stdout.fileno()
    )

    return


def list_installed_packages(mask, destdir='/', return_list=False, mute=False):
    destdir = os.path.abspath(destdir)
    listdir = os.path.abspath(destdir + org.wayround.aipsetup.config.config['installed_pkg_dir'])
    listdir = listdir.replace(os.path.sep * 2, os.path.sep)
    filelist = glob.glob(os.path.join(listdir, mask))

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
        bases.sort()

        for i in ['sums', 'buildlogs']:
            if i in bases:
                bases.remove(i)

        if not mute:
            org.wayround.utils.text.columned_list_print(
                bases, fd=sys.stdout.fileno()
            )

        if return_list:
            ret = bases

    return ret

def remove_package(name, destdir='/'):

    ret = 0

    destdir = os.path.abspath(destdir)

    listdir = os.path.abspath(destdir + os.path.sep + org.wayround.aipsetup.config.config['installed_pkg_dir'])
    listdir = listdir.replace(os.path.sep * 2, os.path.sep)

    filename = os.path.abspath(listdir + os.path.sep + name + '.xz')

    if not os.path.isfile(filename):
        logging.error("Not found package file list `%(name)s'" % {
            'name': filename
            })
        ret = 1
    else:
        try:
            f = open(filename, 'r')
        except:
            logging.error("Error opening file %(name)s" % {
                'name': filename
                })
            ret = 2
        else:
            txt = org.wayround.utils.archive.xzcat(f)
            f.close()
            del(f)
            lines = txt.splitlines()
            del(txt)

            lines.sort(None, None, True)

            for line in lines:
                rm_file_name = os.path.abspath(destdir + os.path.sep + line)
                rm_file_name = rm_file_name.replace(os.path.sep * 2, os.path.sep)
                if os.path.isfile(rm_file_name):
                    logging.info("removing %(name)s" % {
                        'name': rm_file_name
                        })
                    os.unlink(rm_file_name)

            for i in ['installed_pkg_dir_buildlogs',
                      'installed_pkg_dir_sums',
                      'installed_pkg_dir']:
                rm_file_name = os.path.abspath(
                    destdir + os.path.sep + org.wayround.aipsetup.config.config[i] + os.path.sep + name + '.xz'
                    )
                rm_file_name = rm_file_name.replace(os.path.sep * 2, os.path.sep)
                if os.path.isfile(rm_file_name):
                    logging.info("removing %(name)s" % {
                        'name': rm_file_name
                        })
                    os.unlink(rm_file_name)
    return ret

def remove_packages(mask, destdir='/'):
    ret = 0
    lst = list_installed_packages(mask, destdir='/', return_list=True)
    for i in lst:

        name = ''

        if not i.endswith('.xz'):
            name = i
        else:
            name = i[:-3]

        logging.info("Removing package `%(name)s'" % {
            'name': name
            })
        remove_package(name, destdir)

    return ret

def reduce_old(name, destdir='/'):
    # TODO: write or delete
    pass

#   build [TARBALL1] [TARBALL2] .. [TARBALLn]

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

def complete(dirname):

    log = org.wayround.utils.log.Log(
        org.wayround.aipsetup.buildingsite.getDIR_BUILD_LOGS(dirname), 'buildingsite complete'
        )
    log.info("Buildingsite processes started")
    log.warning("Closing this log now, cause it can't work farther")
    log.stop()

    ret = 0

    if org.wayround.aipsetup.build.complete(dirname) != 0:
        logging.error("Error on building stage")
        ret = 1
    elif org.wayround.aipsetup.pack.complete(dirname) != 0:
        logging.error("Error on packaging stage")
        ret = 2

    return ret

def find_files(destdir, instr, mode=None, mute=False,
               return_dict=True):

    ret = 0

    lst = list_installed_packages(mask='*.xz', destdir=destdir,
                        return_list=True,
                        mute=True)
    if not isinstance(lst, list):
        logging.error("Error getting installed packages list")
        ret = 1
    else:
        lst.sort()

        ret_dict = dict()

        for pkgname in lst:
            if pkgname.endswith('.xz'):
                pkgname = pkgname[:-3]

            found = find_file(destdir, pkgname, instr=instr,
                              mode=mode,
                              mute=True, return_list=True)

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

def find_file(destdir, pkgname, instr, mode=None, mute=False,
              return_list=True):
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

        pkg_file_list = package_files(destdir, pkgname,
                                      mute=False,
                                      return_list=True)

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
            if not mute:
                org.wayround.utils.text.columned_list_print(
                    out_list, fd=sys.stdout.fileno()
                )

            if return_list:
                ret = copy.copy(out_list)

    return ret

def package_files(destdir, pkgname,
                  return_list=True):
    ret = 0

    destdir = os.path.abspath(destdir)

    list_dir = destdir + os.path.sep + org.wayround.aipsetup.config.config['installed_pkg_dir']
    list_dir = list_dir.replace(os.path.sep * 2, os.path.sep)
    list_dir = os.path.abspath(list_dir)

    pkg_list_file = os.path.join(list_dir, pkgname)

    if not pkg_list_file.endswith('.xz'):
        pkg_list_file += '.xz'

    try:
        f = open(pkg_list_file, 'r')
    except:
        logging.exception("Can't open list file")
        ret = 2
    else:

        pkg_file_list = org.wayround.utils.archive.xzcat(f)

        f.close()

        pkg_file_list = pkg_file_list.splitlines()

        pkg_file_list.sort()

        logging.info(
            org.wayround.utils.text.columned_list_print(
                pkg_file_list, fd=sys.stdout.fileno()
                )
            )

        if return_list:
            ret = copy.copy(pkg_file_list)

    return ret


def check_package_aipsetup2(filename):

    ret = 0

    filename = os.path.abspath(filename)
    if not filename.endswith('.tar.xz'):
        ret = 1
    else:
        filename_sha512 = filename + '.sha512'
        filename_md5 = filename + '.md5'

        if not os.path.isfile(filename) \
            or not os.path.isfile(filename_sha512) \
            or not os.path.isfile(filename_md5):
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

def put_to_index_many(files):

    for i in files:
        if os.path.exists(i):
            put_to_index(i)

    return 0

def put_to_index(filename):
    ret = 0

    if os.path.isdir(filename) or os.path.islink(filename):
        logging.error("wrong file type `%(name)s'" % {
            'name': filename
            })
        ret = 10
    else:

        if check_package_aipsetup2(filename) == 0:
            filename = os.path.abspath(filename)
            filename_sha512 = filename + '.sha512'
            filename_md5 = filename + '.md5'
            fbn = os.path.basename(filename)

            par_res = org.wayround.aipsetup.name.package_name_parse(fbn)
            if not isinstance(par_res, dict):
                logging.error("Couldn't parse filename `%(fn)s'" % {
                    'fn': fbn
                    })
                ret = 1
            else:
                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    par_res['groups']['name']
                    )

                if path == None:
                    logging.error("Can't get `%(package)s' path from database" % {
                        'package': par_res['groups']['name']
                        })
                    ret = 2
                else:
                    full_path = org.wayround.aipsetup.config.config['repository'] + os.path.sep + path
                    full_path = os.path.abspath(full_path.replace(os.path.sep * 2, os.path.sep))

                    if org.wayround.aipsetup.pkgindex.create_required_dirs_at_package(
                        full_path
                        ) != 0:
                        logging.error("Can't ensure existence of required dirs")
                        ret = 3
                    else:

                        full_path_pack = full_path + '/aipsetup2'

                        logging.info("moving `%(n1)s' to `%(n2)s'" % {
                            'n1': filename,
                            'n2': full_path_pack
                            })
                        for i in [
                            (filename, full_path_pack + os.path.sep + fbn),
                            (filename_md5, full_path_pack + os.path.sep + fbn + '.md5'),
                            (filename_sha512, full_path_pack + os.path.sep + fbn + '.sha512')
                            ]:
                            if (os.path.abspath(i[0]) != os.path.abspath(i[1])):

                                org.wayround.utils.file.remove_if_exists(
                                    i[1]
                                    )

                                shutil.move(i[0], i[1])

        elif check_package(filename, mute=True) == 0:
            filename = os.path.abspath(filename)
            fbn = os.path.basename(filename)
            par_res = org.wayround.aipsetup.name.package_name_parse(fbn)
            if not isinstance(par_res, dict):
                logging.error("Couldn't parse filename `%(fn)s'" % {
                    'fn': fbn
                    })
                ret = 1
            else:
                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    par_res['groups']['name']
                    )
                if path == None:
                    logging.error("Can't get `%(package)s' path from database" % {
                        'package': par_res['groups']['name']
                        })
                    ret = 2
                else:
                    full_path = org.wayround.aipsetup.config.config['repository'] + os.path.sep + path
                    full_path = os.path.abspath(full_path.replace(os.path.sep * 2, os.path.sep))

                    if org.wayround.aipsetup.pkgindex.create_required_dirs_at_package(
                        full_path
                        ) != 0:
                        logging.error("Can't ensure existence of required dirs")
                        ret = 3
                    else:

                        full_path_pack = full_path + '/pack'

                        logging.info("moving `%(n1)s' to `%(n2)s'" % {
                            'n1': filename,
                            'n2': full_path_pack + os.path.sep + fbn
                            })

                        if (os.path.abspath(filename) != os.path.abspath(full_path_pack + os.path.sep + fbn)):
                            org.wayround.utils.file.remove_if_exists(
                                full_path_pack + os.path.sep + fbn
                                )
                            shutil.move(filename, full_path_pack + os.path.sep + fbn)

        else:

            sn_pres = org.wayround.aipsetup.name.source_name_parse(
                filename
                )

            if not isinstance(sn_pres, dict):
                logging.warning("File action undefined: `%(name)s'" % {
                    'name': filename
                    })
            else:
                logging.info("Source name parsed")
                fbn = os.path.basename(filename)
                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    sn_pres['groups']['name']
                    )

                if path == None:
                    logging.error("Can't get `%(package)s' path from database" % {
                        'package': sn_pres['groups']['name']
                        })
                    ret = 2
                else:
                    full_path = org.wayround.aipsetup.config.config['repository'] + os.path.sep + path
                    full_path = os.path.abspath(full_path.replace(os.path.sep * 2, os.path.sep))

                    if org.wayround.aipsetup.pkgindex.create_required_dirs_at_package(
                        full_path
                        ) != 0:
                        logging.error("Can't ensure existence of required dirs")
                        ret = 3
                    else:

                        full_path_source = full_path + '/source'

                        logging.info("moving `%(n1)s' to `%(n2)s'" % {
                            'n1': filename,
                            'n2': full_path_source + os.path.sep + fbn
                            })

                        if (os.path.abspath(filename) != os.path.abspath(full_path_source + os.path.sep + fbn)):
                            org.wayround.utils.file.remove_if_exists(
                                full_path_source + os.path.sep + fbn
                                )
                            shutil.move(filename, full_path_source + os.path.sep + fbn)
                            if os.path.isfile(filename + '.asc'):
                                shutil.move(filename + '.asc', full_path_source + os.path.sep + fbn + '.asc')

    return ret
