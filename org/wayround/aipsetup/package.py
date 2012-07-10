# -*- coding: utf-8 -*-

"""
This module is part of aipsetup.

It't purpuse is to check, install, uninstall package
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

import org.wayround.utils.checksum
import org.wayround.utils.error
import org.wayround.utils.text
import org.wayround.utils.time
import org.wayround.utils.archive

import org.wayround.aipsetup.pkgindex
import org.wayround.aipsetup.name
import org.wayround.aipsetup.buildingsite

def print_help():
    print("""\
aipsetup package command

   install [-b=DIRNAME] FILE

      Install package. If -b is given - it is used as root

   list [-b=DIRNAME] [MASK]

      List installed packages. -b is same as in install.
      Default MASK is *.xz

   names_list [-b=DIRNAME] PACKAGE_NAME

      List installations with name PACKAGE_NAME.
      -b is same as in install.

   package_issues [-b=DIRNAME]

      Looks for issues with already installed package names:
         * list unparsabel names
         * list names not in info files directory

   remove [-b=DIRNAME] MASK

      Removes packages matching MASK.

      WARNING: no sanity checks!
          aipsetup package remove '*'
          will remove everything (unless system will crush
          before is't finished)

      WARNING: removes any installed config files!
          do all necessery config backups before remove!

   find_files [-b=DIRNAME] [-m=beg|re|plain|sub|fm] LOOKFOR

      Looks for LOOKFOR in all installed packages using one of methods:

         sub   - (default) filename contains LOOKFOR
         re    - LOOKFOR is RegExp
         beg   - file name starts with LOOKFOR
         plain - Exact LOOKFOR match
         fm    - LOOKFOR is file mask

   put_to_index_many FILEMASK
""")

def router(opts, args, config):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print("-e- command not given")
        ret = 1
    else:

        if args[0] == 'help':
            print_help()
        elif args[0] == 'install':

            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            if args_l == 1:
                print("-e- Pacakge name required!")
                ret = 2
            else:
                asp_name = args[1]
                ret = install(config, asp_name, basedir)

        elif args[0] == 'list':

            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            asp_name = '*.xz'
            if args_l > 1:
                asp_name = args[1]

            if not isinstance(basedir, str):
                print("-e- given basedir name is wrong")
                ret = 2

            if ret == 0:
                ret = list_packages(config, asp_name, basedir)

        elif args[0] == 'named_list':

            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            asp_name = None
            if args_l > 1:
                asp_name = args[1]

            if not isinstance(basedir, str):
                print("-e- given basedir name is wrong")
                ret = 2

            if not isinstance(asp_name, str):
                print("-e- package name required")
                ret = 3

            if ret == 0:
                ret = named_list_packages(config, asp_name, basedir)

        elif args[0] == 'package_issues':
            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            if not isinstance(basedir, str):
                print("-e- given basedir name is wrong")
                ret = 2

            if ret == 0:
                list_packages_issues(config, basedir)

        elif args[0] == 'remove':

            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            asp_name = None
            if args_l > 1:
                asp_name = args[1]

            if not isinstance(basedir, str):
                print("-e- given basedir name is wrong")
                ret = 2

            if not isinstance(asp_name, str):
                print("-e- removing name mask must be not empty!")
                ret = 3

            if ret == 0:
                ret = remove_packages(config, asp_name, basedir)

        elif args[0] == 'complite':

            dirname = '.'

            if args_l > 1:
                dirname = args[1]

            ret = complite(config, dirname)

        elif args[0] == 'build':

            sources = []

            if args_l > 1:
                sources = args[1:]

            if len(sources) == 0:
                print("-e- No source files named")
                ret = 2

            if ret == 0:
                ret = build(config, sources)

        elif args[0] == 'find_files':

            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            look_meth = 'sub'
            for i in opts:
                if i[0] == '-m':
                    look_meth = i[1]

            lookfor = ''
            if args_l > 1:
                lookfor = args[1]

            ret = find_files(config, basedir, lookfor, mode=look_meth,
                             mute=False,
                             return_dict=False)

        elif args[0] == 'put_to_index_many':

            files = []
            if args_l > 1:
                files = args[1:]

            if len(files) == 0:
                print('-e- File names required')
                ret = 2
            else:
                ret = put_to_index_many(config, files)

        else:
            print("-e- Wrong command")
            ret = 1

    return ret

def check_package(config, asp_name, mute=False):
    """
    Check package for errors
    """
    ret = 0

    asp_name = os.path.abspath(asp_name)

    if not asp_name.endswith('.asp'):
        if not mute:
            print("-e- Wrong file extension `%(name)s'" % {
                'name': asp_name
                })
        ret = 3
    else:
        try:
            tarf = tarfile.open(asp_name, mode='r')
        except:
            print("-e- Can't open file `%(name)s'" % {
                'name': asp_name
                })
            print(org.wayround.utils.error.return_exception_info(
                sys.exc_info()
                ))
            ret = 1
        else:
            f = org.wayround.utils.archive.tar_member_get_extract_file(
                tarf,
                './package.sha512'
                )
            if not isinstance(f, tarfile.ExFileObject):
                print("-e- Can't get checksums from package file")
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
                    print("-e- Error was found while checking package")
                    ret = 3
                else:
                    ret = 0

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

def install(config, asp_name, destdir='/'):

    ret = 0

    destdir = os.path.abspath(destdir)

    print("-i- Performing package checks before it's installation")
    if check_package(config, asp_name) != 0:
        print("-e- Package defective - installation failed")
        ret = 1
    else:
        try:
            tarf = tarfile.open(asp_name, mode='r')
        except:
            print("-e- Can't open file %(name)s")
            org.wayround.utils.error.print_exception_info(sys.exc_info())
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

                print("-i- Installing %(what)s" % {
                    'what': i[2]
                    })

                logs_path = ''
                if config[i[1]][0] == '/':
                    logs_path = config[i[1]][1:]
                else:
                    logs_path = config[i[1]]

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
                    print("-e- Can't install %(what)s as %(outname)s" % {
                        'what': i[2],
                        'outname': out_filename
                        })
                    ret = 2
                    break

            if ret == 0:
                print("-i- Installing package's destdir")

                dd_fobj = org.wayround.utils.archive.\
                    tar_member_get_extract_file(
                        tarf, './04.DESTDIR.tar.xz'
                        )
                if not isinstance(dd_fobj, tarfile.ExFileObject):
                    print("-e- Can't get package's destdir")
                    ret = 4
                else:
                    if org.wayround.utils.archive.\
                        decompress_dir_contents_tar_compressor_fobj(
                            dd_fobj, destdir, 'xz',
                            verbose_tar=True,
                            verbose_compressor=True,
                            add_tar_options=['--no-same-owner', '--no-same-permissions']
                            ) != 0:
                        print("-e- Package destdir decompression error")
                        ret = 5
                    else:
                        ret = 0
                        print("-i- Installation look like complite :-)")
                    dd_fobj.close()

            tarf.close()

    return ret

def list_packages_issues(config, destdir='/'):
    lst = list_packages(config, '*', destdir=destdir, return_list=True)

    info_dir = os.path.abspath(config['info'])

    check_list = set()

    issued = set()

    for i in lst:

        name = ''

        if not i.endswith('.xz'):
            name = i
        else:
            name = i[:-3]

        parsed_name = org.wayround.aipsetup.name.package_name_parse(name)
        if parsed_name == None:
            print("-w- Error while parsing name `%(name)s'" % {
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
            print("-w- Some issue with `%(name)s' info file" % {
                'name': i
                })
            issued.add(i)

    issued = list(issued)
    issued.sort()
    print("-i- Found issues with following (%(num)d) packages:" % {
        'num': len(issued)
        })
    org.wayround.utils.text.columned_list_print(
        issued, fd=sys.stdout.fileno()
    )

    return

def named_list_packages(config, asp_name, destdir='/'):
    lst = list_packages(config, '*', destdir=destdir, return_list=True)

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


def list_packages(config, mask, destdir='/', return_list=False, mute=False):
    destdir = os.path.abspath(destdir)
    listdir = os.path.abspath(destdir + config['installed_pkg_dir'])
    listdir = listdir.replace(r'//', '/')
    filelist = glob.glob(os.path.join(listdir, mask))

    ret = 0

    if not os.path.isdir(listdir):
        print("-e- not a dir %(dir)s" % {
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

def remove_package(config, name, destdir='/'):

    ret = 0

    destdir = os.path.abspath(destdir)

    listdir = os.path.abspath(destdir + '/' + config['installed_pkg_dir'])
    listdir = listdir.replace(r'//', '/')

    filename = os.path.abspath(listdir + '/' + name + '.xz')

    if not os.path.isfile(filename):
        print("-e- Not found package file list `%(name)s'" % {
            'name': filename
            })
        ret = 1
    else:
        try:
            f = open(filename, 'r')
        except:
            print("-e- Error opening file %(name)s" % {
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
                rm_file_name = os.path.abspath(destdir + '/' + line)
                rm_file_name = rm_file_name.replace(r'//', '/')
                if os.path.isfile(rm_file_name):
                    print("-i- removing %(name)s" % {
                        'name': rm_file_name
                        })
                    os.unlink(rm_file_name)

            for i in ['installed_pkg_dir_buildlogs',
                      'installed_pkg_dir_sums',
                      'installed_pkg_dir']:
                rm_file_name = os.path.abspath(
                    destdir + '/' + config[i] + '/' + name + '.xz'
                    )
                rm_file_name = rm_file_name.replace(r'//', '/')
                if os.path.isfile(rm_file_name):
                    print("-i- removing %(name)s" % {
                        'name': rm_file_name
                        })
                    os.unlink(rm_file_name)
    return ret

def remove_packages(config, mask, destdir='/'):
    ret = 0
    lst = list_packages(config, mask, destdir='/', return_list=True)
    for i in lst:

        name = ''

        if not i.endswith('.xz'):
            name = i
        else:
            name = i[:-3]

        print("-i- Removing package `%(name)s'" % {
            'name': name
            })
        remove_package(config, name, destdir)

    return ret

def reduce_old(config, name, destdir='/'):
    # TODO: write or delete
    pass

#   build [TARBALL1] [TARBALL2] .. [TARBALLn]

def build(config, source_files):
    ret = 0

    par_res = org.wayround.aipsetup.name.source_name_parse(
        config, source_files[0]
        )

    if par_res == None:
        print("-e- Can't parse source file name")
        ret = 1
    else:

        try:
            os.makedirs(config['buildingsites'])
        except:
            pass

        tmp_dir_prefix = "%(name)s-%(timestamp)s-" % {
            'name': par_res['groups']['name'],
            'timestamp': org.wayround.utils.time.currenttime_stamp()
            }

        build_site_dir = tempfile.mkdtemp(
            prefix=tmp_dir_prefix,
            dir=config['buildingsites']
            )
        build_site_dir = os.path.abspath(build_site_dir)

        if org.wayround.aipsetup.buildingsite.init(config, build_site_dir) != 0:
            print("-e- Error initiating temporary dir")
            ret = 2
        else:
            if source_files != None and isinstance(source_files, list):

                print("-i- copying sources")

                for source_file in source_files:

                    print(("-i-    %(name)s" % {
                        'name': source_file
                        }))

                    if os.path.isfile(source_file) \
                            and not os.path.islink(source_file):

                        try:
                            shutil.copy(
                                source_file, os.path.join(
                                    build_site_dir,
                                    org.wayround.aipsetup.buildingsite.DIR_TARBALL
                                    )
                                )
                        except:
                            org.wayround.utils.error.print_exception_info(
                                sys.exc_info()
                                )
                            ret = -3

                    else:

                        print(("-e- file %(file)s - not dir and not file." % {
                            'file': source_file
                            }))
                        print("    skipping copy")

                if ret != 0:
                    print("-e- Exception while copying one of soruce files")

            if org.wayround.aipsetup.buildingsite.apply_info(
                config, build_site_dir, source_files[0]) == 0:

                if complite(config, build_site_dir) != 0:
                    print("-e- Package building failed")
                    ret = 5

    return ret

def complite(config, dirname):

    log = org.wayround.utils.log.Log(
        config, dirname, 'buildingsite complite'
        )
    log.write("-i- Buildingsite processes started")
    log.write("-i- Closing this log now, cause it can't be done farther")
    log.stop()

    ret = 0

    if org.wayround.aipsetup.build.complite(config, dirname) != 0:
        print("-e- Error on building stage")
        ret = 1
    elif org.wayround.aipsetup.pack.complite(config, dirname) != 0:
        print("-e- Error on packaging stage")
        ret = 2

    return ret

def find_files(config, destdir, instr, mode=None, mute=False,
               return_dict=True):

    ret = 0

    lst = list_packages(config, mask='*.xz', destdir=destdir,
                        return_list=True,
                        mute=True)
    if not isinstance(lst, list):
        print("-e- Error getting installed packages list")
        ret = 1
    else:
        lst.sort()

        ret_dict = dict()

        for pkgname in lst:
            if pkgname.endswith('.xz'):
                pkgname = pkgname[:-3]

            found = find_file(config, destdir, pkgname, instr=instr,
                              mode=mode,
                              mute=True, return_list=True)

            if len(found) != 0:
                ret_dict[pkgname] = found

        if not mute:
            rd_keys = list(ret_dict.keys())
            if len(rd_keys) == 0:
                print("-i- Not found")
            else:
                print("-i- Found %(num)d packages with `%(inc)s'" % {
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

def find_file(config, destdir, pkgname, instr, mode=None, mute=False,
              return_list=True):
    ret = 0

    destdir = os.path.abspath(destdir)

    if not isinstance(instr, list):
        instr = [instr]

    if mode == None:
        mode = 'sub'

    if not mode in ['re', 'plain', 'sub', 'beg', 'fm']:
        print("-e- wrong mode")
        ret = 1
    else:

        if not pkgname.endswith('.xz'):
            pkgname += '.xz'

        pkg_file_list = package_files(config, destdir, pkgname,
                                      mute=False,
                                      return_list=True)

        if not isinstance(pkg_file_list, list):
            print("-e- Can't get list of files")
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

def package_files(config, destdir, pkgname, mute=False,
                  return_list=True):
    ret = 0

    destdir = os.path.abspath(destdir)

    list_dir = destdir + '/' + config['installed_pkg_dir']
    list_dir = list_dir.replace(r'//', '/')
    list_dir = os.path.abspath(list_dir)

    pkg_list_file = os.path.join(list_dir, pkgname)

    if not pkg_list_file.endswith('.xz'):
        pkg_list_file += '.xz'

    try:
        f = open(pkg_list_file, 'r')
    except:
        print("-e- Can't open list file")
        org.wayround.utils.error.print_exception_info(sys.exc_info())
        ret = 2
    else:

        pkg_file_list = org.wayround.utils.archive.xzcat(f)

        f.close()

        pkg_file_list = pkg_file_list.splitlines()

        pkg_file_list.sort()

        if not mute:
            org.wayround.utils.text.columned_list_print(
                pkg_file_list, fd=sys.stdout.fileno()
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

def put_to_index_many(config, files):

    for i in files:
        if os.path.exists(i):
            put_to_index(config, i)

    return 0

def put_to_index(config, filename):
    ret = 0

    if os.path.isdir(filename) or os.path.islink(filename):
        print("-e- wrong file type `%(name)s'" % {
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
                print("-e- Couldn't parse filename `%(fn)s'" % {
                    'fn': fbn
                    })
                ret = 1
            else:
                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    config,
                    par_res['groups']['name']
                    )
                if path == None:
                    print("-e- Can't get `%(package)s' path from database" % {
                        'package': par_res['groups']['name']
                        })
                    ret = 2
                else:
                    full_path = config['repository'] + '/' + path
                    full_path = os.path.abspath(full_path.replace(r'//', '/'))

                    if org.wayround.aipsetup.pkgindex.create_required_dirs_at_package(
                        full_path
                        ) != 0:
                        print("-e- Can't ensure existance of required dirs")
                        ret = 3
                    else:

                        full_path_pack = full_path + '/aipsetup2'

                        print("-i- moving `%(n1)s' to `%(n2)s'" % {
                            'n1': filename,
                            'n2': full_path_pack
                            })
                        for i in [
                            (filename, full_path_pack + '/' + fbn),
                            (filename_md5, full_path_pack + '/' + fbn + '.md5'),
                            (filename_sha512, full_path_pack + '/' + fbn + '.sha512')
                            ]:
                            if (os.path.abspath(i[0]) != os.path.abspath(i[1])):

                                org.wayround.utils.file.remove_if_exists(
                                    i[1]
                                    )

                                shutil.move(i[0], i[1])

        elif check_package(config, filename, mute=True) == 0:
            filename = os.path.abspath(filename)
            fbn = os.path.basename(filename)
            par_res = org.wayround.aipsetup.name.package_name_parse(fbn)
            if not isinstance(par_res, dict):
                print("-e- Couldn't parse filename `%(fn)s'" % {
                    'fn': fbn
                    })
                ret = 1
            else:
                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    config,
                    par_res['groups']['name']
                    )
                if path == None:
                    print("-e- Can't get `%(package)s' path from database" % {
                        'package': par_res['groups']['name']
                        })
                    ret = 2
                else:
                    full_path = config['repository'] + '/' + path
                    full_path = os.path.abspath(full_path.replace(r'//', '/'))

                    if org.wayround.aipsetup.pkgindex.create_required_dirs_at_package(
                        full_path
                        ) != 0:
                        print("-e- Can't ensure existance of required dirs")
                        ret = 3
                    else:

                        full_path_pack = full_path + '/pack'

                        print("-i- moving `%(n1)s' to `%(n2)s'" % {
                            'n1': filename,
                            'n2': full_path_pack + '/' + fbn
                            })

                        if (os.path.abspath(filename) != os.path.abspath(full_path_pack + '/' + fbn)):
                            org.wayround.utils.file.remove_if_exists(
                                full_path_pack + '/' + fbn
                                )
                            shutil.move(filename, full_path_pack + '/' + fbn)

        else:

            sn_pres = org.wayround.aipsetup.name.source_name_parse(
                config, filename
            )

            if not isinstance(sn_pres, dict):
                print("-w- File action undefined: `%(name)s'" % {
                    'name': filename
                    })
            else:
                print("-i- Source name parsed")
                fbn = os.path.basename(filename)
                path = org.wayround.aipsetup.pkgindex.get_package_path(
                    config,
                    sn_pres['groups']['name']
                    )
                if path == None:
                    print("-e- Can't get `%(package)s' path from database" % {
                        'package': sn_pres['groups']['name']
                        })
                    ret = 2
                else:
                    full_path = config['repository'] + '/' + path
                    full_path = os.path.abspath(full_path.replace(r'//', '/'))

                    if org.wayround.aipsetup.pkgindex.create_required_dirs_at_package(
                        full_path
                        ) != 0:
                        print("-e- Can't ensure existance of required dirs")
                        ret = 3
                    else:

                        full_path_source = full_path + '/source'

                        print("-i- moving `%(n1)s' to `%(n2)s'" % {
                            'n1': filename,
                            'n2': full_path_source + '/' + fbn
                            })

                        if (os.path.abspath(filename) != os.path.abspath(full_path_source + '/' + fbn)):
                            org.wayround.utils.file.remove_if_exists(
                                full_path_source + '/' + fbn
                                )
                            shutil.move(filename, full_path_source + '/' + fbn)
                            if os.path.isfile(filename + '.asc'):
                                shutil.move(filename + '.asc', full_path_source + '/' + fbn + '.asc')

    return ret
