# -*- coding: utf-8 -*-

"""
This module is part of aipsetup.

It't purpuse is to check, install, uninstall package
"""

import sys
import os
import os.path
import tarfile
import glob

import aipsetup.name
import aipsetup.utils.checksum
import aipsetup.utils.error
import aipsetup.utils.text
import aipsetup.storage.archive

def print_help():
    print """\
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

        elif args[0] == 'list':

            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            asp_name = '*.xz'
            if args_l > 1:
                asp_name = args[1]

            if not isinstance(basedir, basestring):
                print "-e- given basedir name is wrong"
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

            if not isinstance(basedir, basestring):
                print "-e- given basedir name is wrong"
                ret = 2

            if not isinstance(asp_name, basestring):
                print "-e- package name required"
                ret = 3

            if ret == 0:
                ret = named_list_packages(config, asp_name, basedir)

        elif args[0] == 'package_issues':
            basedir = '/'
            for i in opts:
                if i[0] == '-b':
                    basedir = i[1]

            if not isinstance(basedir, basestring):
                print "-e- given basedir name is wrong"
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

            if not isinstance(basedir, basestring):
                print "-e- given basedir name is wrong"
                ret = 2

            if not isinstance(asp_name, basestring):
                print "-e- removing name mask must be not empty!"
                ret = 3

            if ret == 0:
                ret = remove_packages(config, asp_name, basedir)

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
                            verbose_compressor=True,
                            add_tar_options = ['--no-same-owner', '--no-same-permissions']
                            ) != 0:
                        print "-e- Package destdir decompression error"
                        ret = 5
                    else:
                        ret = 0
                        print "-i- Installation look like complite :-)"
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

        parsed_name = aipsetup.name.package_name_parse(name)
        if parsed_name == None:
            print "-w- Error while parsing name `%(name)s'" % {
                'name': name
                }
        else:
            check_list.add(parsed_name['groups']['name'])

    check_list = list(check_list)
    check_list.sort()
    for i in check_list:
        info_file = os.path.join(
            info_dir, i + '.xml'
            )
        if not isinstance(aipsetup.info.read_from_file(info_file), dict):
            print "-w- Some issue with `%(name)s' info file" % {
                'name': i
                }
            issued.add(i)

    issued = list(issued)
    issued.sort()
    print "-i- Found issues with following (%(num)d) packages:" % {
        'num': len(issued)
        }
    aipsetup.utils.text.columned_list_print(
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

        parsed_name = aipsetup.name.package_name_parse(name)
        if parsed_name == None:
            pass
        else:
            #print repr(parsed_name)
            if parsed_name['groups']['name'] == asp_name:
                out_list.append(name)

    aipsetup.utils.text.columned_list_print(
        out_list, fd=sys.stdout.fileno()
    )

    return


def list_packages(config, mask, destdir='/', return_list=False):
    destdir = os.path.abspath(destdir)
    listdir = os.path.abspath(destdir + config['installed_pkg_dir'])
    listdir = listdir.replace(r'//', '/')
    filelist = glob.glob(os.path.join(listdir, mask))

    ret = 0

    if not os.path.isdir(listdir):
        print "-e- not a dir %(dir)s" % {
            'dir': listdir
            }
        ret = 1
    else:
        bases = []
        for each in filelist:
            bases.append(os.path.basename(each))
        bases.sort()

        for i in ['sums', 'buildlogs']:
            if i in bases:
                bases.remove(i)

        if not return_list:
            aipsetup.utils.text.columned_list_print(
                bases, fd=sys.stdout.fileno()
            )
        else:
            ret = bases

    return ret

def remove_package(config, name, destdir='/'):

    ret = 0

    destdir = os.path.abspath(destdir)

    listdir = os.path.abspath(destdir + '/' + config['installed_pkg_dir'])
    listdir = listdir.replace(r'//', '/')

    filename = os.path.abspath(listdir + '/' + name + '.xz')

    if not os.path.isfile(filename):
        print "-e- Not found package file list `%(name)s'" % {
            'name': filename
            }
        ret = 1
    else:
        try:
            f = open(filename, 'r')
        except:
            print "-e- Error opening file %(name)s" % {
                'name': filename
                }
            ret = 2
        else:
            txt = aipsetup.storage.archive.xzcat(f)
            f.close()
            del(f)
            lines = txt.splitlines()
            del(txt)

            lines.sort(None, None, True)

            for line in lines:
                rm_file_name = os.path.abspath(destdir + '/' + line)
                rm_file_name = rm_file_name.replace(r'//', '/')
                if os.path.isfile(rm_file_name):
                    print "-i- removing %(name)s" % {
                        'name': rm_file_name
                        }
                    os.unlink(rm_file_name)

            for i in ['installed_pkg_dir_buildlogs',
                      'installed_pkg_dir_sums',
                      'installed_pkg_dir']:
                rm_file_name = os.path.abspath(
                    destdir + '/' + config[i] + '/' + name + '.xz'
                    )
                rm_file_name = rm_file_name.replace(r'//', '/')
                if os.path.isfile(rm_file_name):
                    print "-i- removing %(name)s" % {
                        'name': rm_file_name
                        }
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

        print "-i- Removing package `%(name)s'" % {
            'name': name
            }
        remove_package(config, name, destdir)

    return ret

def reduce_old(config, name, destdir='/'):
    pass
