# -*- coding: utf-8 -*-

"""
This module is part of aipsetup.

It't purpuse is to check, install, uninstall package
"""

import sys
import os.path
import tarfile

import aipsetup.utils.checksum
import aipsetup.utils.error
import aipsetup.storage.archive

def print_help():
    print """\
aipsetup pack command


"""

def router(opts, args, config):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print "-e- command not given"
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
                print "-e- Pacakge name required!"
                ret = 2
            else:
                asp_name = args[1]
                ret = install(config, asp_name, basedir)
        else:
            print "-e- Wrong command"
            ret = 1

    return ret

def check_package(config, asp_name):
    """
    Check package for errors
    """
    ret = 0

    if not asp_name.endswith('.asp'):
        print "-e- Wrong file extension"
        ret = 3
    else:
        try:
            tarf = tarfile.open(asp_name, mode='r')
        except:
            print "-e- Can't open file %(name)s"
            print aipsetup.utils.error.return_exception_info(
                sys.exc_info()
                )
            ret = 1
        else:
            f = aipsetup.storage.archive.tar_member_get_extract_file(
                tarf,
                './package.sha512'
                )
            if not isinstance(f, tarfile.ExFileObject):
                print "-e- Can't get checksums from package file"
                ret = 2
            else:
                sums_txt = f.read()
                f.close()
                sums = aipsetup.utils.checksum.parse_checksums_text(
                    sums_txt
                    )
                del(sums_txt)

                sums2 = {}
                for i in sums:
                    sums2['.'+i]=sums[i]
                sums = sums2
                del(sums2)

                #print repr(sums)

                tar_members = tarf.getmembers()

                check_list = ['./04.DESTDIR.tar.xz', './05.BUILD_LOGS.tar.xz',
                              './package_info.py', './02.PATCHES.tar.xz']

                for i in ['./00.TARBALL',  './06.LISTS']:
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

                    print "       %(name)s - %(result)s" % {
                        'name': i,
                        'result': cresult
                        }

                if error_found:
                    print "-e- Error was found while checking package"
                    ret = 3
                else:
                    ret = 0

            tarf.close()
    return ret

def tarobj_check_member_sum(tarobj, sums, member_name):
    ret = True
    fobj = aipsetup.storage.archive.tar_member_get_extract_file(
        tarobj,
        member_name
        )
    if not isinstance(fobj, tarfile.ExFileObject):
        ret = False
    else:
        sum = aipsetup.utils.checksum.make_fileobj_checksum(fobj)
        if sum == sums[member_name]:
            ret = True
        else:
            ret = False
        fobj.close()
    return ret

def install(config, asp_name, destdir='/'):

    ret = 0

    destdir = os.path.abspath(destdir)

    print "-i- Performing package checks before it's installation"
    if check_package(config, asp_name) != 0:
        print "-e- Package defective - installation failed"
        ret = 1
    else:
        try:
            tarf = tarfile.open(asp_name, mode='r')
        except:
            print "-e- Can't open file %(name)s"
            aipsetup.utils.error.print_exception_info(sys.exc_info())
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

                print "-i- Installing %(what)s" % {
                    'what': i[2]
                    }

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

                if aipsetup.storage.archive.\
                    tar_member_get_extract_file_to(
                        tarf, i[0], out_filename
                        ) != 0 :
                    print "-e- Can't install %(what)s as %(outname)s" % {
                        'what': i[2],
                        'outname': out_filename
                        }
                    ret = 2
                    break

            if ret == 0:
                print "-i- Installing package's destdir"

                dd_fobj = aipsetup.storage.archive.\
                    tar_member_get_extract_file(
                        tarf, './04.DESTDIR.tar.xz'
                        )
                if not isinstance(dd_fobj, tarfile.ExFileObject):
                    print "-e- Can't get package's destdir"
                    ret = 4
                else:
                    if aipsetup.storage.archive.\
                        decompress_dir_contents_tar_compressor_fobj(
                            dd_fobj, destdir, 'xz',
                            verbose_tar=True,
                            verbose_compressor=True
                            ) != 0:
                        print "-e- Package destdir decompression error"
                        ret = 5
                    else:
                        ret = 0
                    dd_fobj.close()

            tarf.close()

    return ret
