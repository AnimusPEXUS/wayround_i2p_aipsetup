import os.path
import tempfile
import shutil
import sys
import pprint

import org.wayround.utils.time
import org.wayround.utils.checksum
import org.wayround.utils.error
import org.wayround.utils.archive
import org.wayround.utils.deps_c


def print_help():
    print("""\
aipsetup pack command

    destdir_checksum

        create checksums for files in destdir

    destdir_filelist

    destdir_deps_c

    remove_source_and_build_dirs

    compress_patches_destdir_and_logs

    compress_files_in_lists_dir

    remove_patches_destdir_and_buildlogs_dirs

    remove_decompressed_files_from_lists_dir

    make_checksums_for_building_site

    pack_buildingsite

""")

def router(opts, args, config):

    ret = 0
    args_l = len(args)

    if args_l == 0:
        print("-e- not enough parameters")
        ret = 1
    else:

        if args[0] == 'help':
            print_help()

        elif args[0] in ['destdir_checksum',
                         'destdir_filelist',
                         'destdir_deps_c',
                         'remove_source_and_build_dirs',
                         'compress_patches_destdir_and_logs',
                         'compress_files_in_lists_dir',
                         'remove_patches_destdir_and_buildlogs_dirs',
                         'remove_decompressed_files_from_lists_dir',
                         'make_checksums_for_building_site',
                         'pack_buildingsite']:

            dirname = '.'

            if args_l > 1:
                dirname = args[1]

            ret = eval("%(name)s(config, dirname)" % {
                    'name': args[0]
                    })

        elif args[0] == 'complite':

            dirname = '.'

            if args_l > 1:
                dirname = args[1]

            ret = complite(config, dirname)

        else:
            print("-e- Wrong pack command")


    return ret


def destdir_checksum(config, buildingsite):

    ret = 0

    destdir = buildingsite.getDir_DESTDIR(buildingsite)

    lists_dir = buildingsite.getDir_LISTS(buildingsite)

    output_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.sha512'
            )
        )

    try:
        os.makedirs(lists_dir)
    except:
        pass

    if not os.path.isdir(destdir):
        print("-e- DESTDIR not found")
        ret = 1
    elif not os.path.isdir(lists_dir):
        print("-e- LIST dir can't be used")
        ret = 2
    else:
        org.wayround.utils.checksum.make_dir_checksums(
            destdir,
            output_file
            )

    return ret


def destdir_filelist(config, buildingsite):

    ret = 0

    destdir = buildingsite.getDir_DESTDIR(buildingsite)

    lists_dir = buildingsite.getDir_LISTS(buildingsite)

    output_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.lst'
            )
        )

    try:
        os.makedirs(lists_dir)
    except:
        pass

    if not os.path.isdir(destdir):
        print("-e- DESTDIR not found")
        ret = 1
    elif not os.path.isdir(lists_dir):
        print("-e- LIST dir can't be used")
        ret = 2
    else:
        org.wayround.utils.file.list_files_recurcive(
            destdir,
            output_file
            )

    return ret

def destdir_deps_c(config, buildingsite):
    ret = 0
    destdir = buildingsite.getDir_DESTDIR(buildingsite)

    lists_dir = buildingsite.getDir_LISTS(buildingsite)

    lists_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.lst'
            )
        )

    deps_file = os.path.abspath(
        os.path.join(
            lists_dir,
            'DESTDIR.dep_c'
            )
        )

    f = open(lists_file, 'r')
    file_list_txt = f.read()
    f.close()
    del(f)
    file_list = file_list_txt.splitlines()
    del(file_list_txt)

    deps = {}
    elfs = 0
    n_elfs = 0
    print("-i- Generating C deps lists")
    file_list_l = len(file_list)
    file_list_i = 1
    for i in file_list:
        file_list_i += 1
        org.wayround.utils.file.progress_write("    (%(perc).2f%%) ELFs: %(elfs)d; non-ELFs: %(n_elfs)d" % {
            'perc': 100 / (float(file_list_l) / file_list_i),
            'elfs': elfs,
            'n_elfs': n_elfs
            })
        filename = destdir + '/' + i
        filename.replace(r'//', '/')
        filename = os.path.abspath(filename)
        dep = org.wayround.utils.deps_c.elf_deps(filename)
        if isinstance(dep, list):
            elfs += 1
            deps[i] = dep
        else:
            #print '-e- not an elf %(name)s' % {
                #'name': filename
                #}
            n_elfs += 1
    print("")
    print("-i- ELFs: %(elfs)d; non-ELFs: %(n_elfs)d" % {
        'elfs': elfs,
        'n_elfs': n_elfs
        })
    f = open(deps_file, 'w')
    f.write(pprint.pformat(deps))
    f.close()
    return ret

def remove_source_and_build_dirs(config, buildingsite):

    ret = 0

    for i in [buildingsite.DIR_SOURCE,
              buildingsite.DIR_BUILDING]:
        dirname = os.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        if os.path.isdir(dirname):
            org.wayround.utils.file.remove_if_exists(dirname)
        else:
            print("-w- Dir not exists: %(dirname)s" % {
                'dirname': dirname
                })

    return ret

def compress_patches_destdir_and_logs(config, buildingsite):

    ret = 0

    for i in [buildingsite.DIR_PATCHES,
              buildingsite.DIR_DESTDIR,
              buildingsite.DIR_BUILD_LOGS]:
        dirname = os.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        filename = "%(dirname)s.tar.xz" % {
            'dirname': dirname
            }

        if not os.path.isdir(dirname):
            print("-w- Dir not exists: %(dirname)s" % {
                'dirname': dirname
                })
            ret = 1
            break
        else:
            print("-i- Compressing %(i)s" % {
                'i': i
                })
            org.wayround.utils.archive.compress_dir_contents_tar_compressor(
                dirname,
                filename,
                'xz',
                verbose_tar=False,
                verbose_compressor=True
                )

    return ret

def compress_files_in_lists_dir(config, buildingsite):

    ret = 0

    lists_dir = buildingsite.getDir_LISTS(buildingsite)

    for i in ['DESTDIR.lst', 'DESTDIR.sha512', 'DESTDIR.dep_c']:

        infile = os.path.join(lists_dir, i)
        outfile = infile + '.xz'

        if org.wayround.utils.archive.compress_file_xz(infile, outfile) != 0:
            print("-e- Error compressing files in lists dir")
            ret = 1
            break

    return ret

def remove_patches_destdir_and_buildlogs_dirs(config, buildingsite):

    ret = 0

    for i in [buildingsite.DIR_PATCHES,
              buildingsite.DIR_DESTDIR,
              buildingsite.DIR_BUILD_LOGS]:
        dirname = os.path.abspath(
            os.path.join(
                buildingsite,
                i
                )
            )
        if os.path.isdir(dirname):
            org.wayround.utils.file.remove_if_exists(dirname)
        else:
            print("-w- Dir not exists: %(dirname)s" % {
                'dirname': dirname
                })

    return ret

def remove_decompressed_files_from_lists_dir(config, buildingsite):

    ret = 0

    lists_dir = buildingsite.getDir_LISTS(buildingsite)

    for i in ['DESTDIR.lst', 'DESTDIR.sha512', 'DESTDIR.dep_c']:

        filename = os.path.join(lists_dir, i)

        if os.path.exists(filename):
            try:
                os.unlink(filename)
            except:
                print("-e- Can't remove file %(name)s" % {
                    'name': filename
                    })
                ret = 1

    return ret

def make_checksums_for_building_site(config, buildingsite):

    ret = 0

    buildingsite = os.path.abspath(buildingsite)

    package_checksums = os.path.join(
        buildingsite,
        'package.sha512'
        )

    if os.path.exists(package_checksums):
        org.wayround.utils.file.remove_if_exists(package_checksums)

    try:
        tf = tempfile.mkstemp()
    except:
        print("-e- Error creating temporary file")
        org.wayround.utils.error.print_exception_info(sys.exc_info())
        ret = 1
    else:
        f = os.fdopen(tf[0], 'w')

        if org.wayround.utils.checksum.make_dir_checksums_fo(
            buildingsite,
            f) != 0:
            print("-e- Error creating checksums for buildingsite")
            ret = 2

        f.close()
        shutil.move(tf[1], package_checksums)

    return ret


def pack_buildingsite(config, buildingsite):

    pi = buildingsite.read_package_info(
        config, buildingsite, ret_on_error=None)

    if pi == None:
        print("-e- error getting information about package")
    else:

        pack_dir = os.path.abspath(
            os.path.join(
                buildingsite,
                '..',
                'pack'
                )
            )

        pack_file_name = os.path.join(
            pack_dir,
            "%(pkgname)s-%(version)s%(versionl)s%(versionln)s-%(timestamp)s-%(archinfo)s.asp" % {
                'pkgname': pi['pkg_nameinfo']['groups']['name'],
                'version': pi['pkg_nameinfo']['groups']['version'],
                'versionl': pi['pkg_nameinfo']['groups']['version_letter'],
                'versionln': pi['pkg_nameinfo']['groups']['version_letter_number'],
                'timestamp': org.wayround.utils.time.currenttime_stamp(),
                'archinfo': "%(arch)s-%(type)s-%(kernel)s-%(os)s" % {
                    'arch'  : pi['constitution']['host_arch'],
                    'type'  : pi['constitution']['host_type'],
                    'kernel': pi['constitution']['host_kenl'],
                    'os'    : pi['constitution']['host_name']
                    }
                }
            )

        try:
            os.makedirs(pack_dir)
        except:
            pass

        org.wayround.utils.archive.pack_dir_contents_tar(
            buildingsite,
            pack_file_name
            )

    return 0

def complite(config, dirname):

    ret = 0

    for i in ['destdir_checksum',
              'destdir_filelist',
              'destdir_deps_c',
              'remove_source_and_build_dirs',
              'compress_patches_destdir_and_logs',
              'compress_files_in_lists_dir',
              'remove_patches_destdir_and_buildlogs_dirs',
              'remove_decompressed_files_from_lists_dir',
              'make_checksums_for_building_site',
              'pack_buildingsite']:
        if eval("%(name)s(config, dirname)" % {
                'name': i
                }) != 0:
            print("-e- Error on %(name)s" % {
                'name': i
                })
            ret = 1
            break

    return ret
