#!/usr/bin/python

import os
import os.path
import shutil
import logging
import glob
import re

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'configure', 'build', 'distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)

        separate_build_dir = False
        source_configure_reldir = 'mozilla/security/nss'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'configure' in actions and ret == 0:
#            nss_build_all: build_coreconf build_nspr build_dbm all

            makefile = os.path.join(
                src_dir, 'mozilla', 'security', 'nss', 'Makefile'
                )

            f = open(makefile, 'r')
            lines = f.readlines()
            f.close()

            for i in range(len(lines)):
                lines[i] = lines[i].rstrip('\n')

            for i in range(len(lines)):

                if lines[i].startswith('nss_build_all:'):
                    line = lines[i].split(' ')

                    while 'build_nspr' in line:
                        line.remove('build_nspr')

                    lines[i] = ' '.join(line)

                if lines[i].startswith('nss_clean_all:'):
                    line = lines[i].split(' ')

                    while 'clobber_nspr' in line:
                        line.remove('clobber_nspr')

                    lines[i] = ' '.join(line)

            for i in range(len(lines)):
                lines[i] = lines[i] + '\n'

            f = open(makefile, 'w')
            f.writelines(lines)
            f.close()

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'nss_build_all',
                    'BUILD_OPT=1',
                    'NSPR_INCLUDE_DIR=/usr/include/nspr',
                    'USE_SYSTEM_ZLIB=1',
                    'ZLIB_LIBS=-lz',
                    'NSS_USE_SYSTEM_SQLITE=1'
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:

            dest_dir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(
                            buildingsite
                            )

            dist_dir = os.path.join(
                src_dir, 'mozilla', 'dist'
                )

            OBJ_dir = glob.glob(dist_dir + os.path.sep + '*.OBJ')

            if len(OBJ_dir) != 1:
                logging.error("single `dist/Linux*' dir not found")
                ret = 10
            else:
                OBJ_dir = dist_dir + os.path.sep + os.path.basename(OBJ_dir[0])

                logging.info(
                    "Dereferencing links in {}".format(
                        os.path.relpath(
                            OBJ_dir,
                            src_dir
                            )
                        )
                    )

                files = os.listdir(os.path.join(OBJ_dir, 'bin'))

                # comment this 'for' if want more files
                for i in files:
                    if not i in ['certutil', 'nss-config', 'pk12util']:
                        os.unlink(
                            os.path.join(OBJ_dir, 'bin', i)
                            )


                if org.wayround.utils.file.dereference_files_in_dir(
                    OBJ_dir
                    ) != 0:
                    logging.error("Some errors while dereferencing symlinks. see above.")
                    ret = 11
                else:

                    logging.info("Preparing distribution dir tree")

                    try:
                        os.mkdir(
                            os.path.join(OBJ_dir, 'include'),
                            mode=0o755
                            )
                    except:
                        pass

                    try:
                        os.mkdir(
                            os.path.join(OBJ_dir, 'usr'),
                            mode=0o755
                            )
                    except:
                        pass

                    shutil.move(
                        os.path.join(OBJ_dir, 'bin'),
                        os.path.join(OBJ_dir, 'usr')
                        )

                    shutil.move(
                        os.path.join(OBJ_dir, 'lib'),
                        os.path.join(OBJ_dir, 'usr')
                        )

                    shutil.move(
                        os.path.join(OBJ_dir, 'include'),
                        os.path.join(OBJ_dir, 'usr')
                        )

                    libs = os.listdir(os.path.join(OBJ_dir, 'usr', 'lib'))

                    libs2 = []
                    for i in libs:
                        re_res = re.match(r'lib(.*?).so', i)
                        if re_res:
                            libs2.append(re_res.group(1))

                    libs = libs2

                    del libs2

                    libs.sort()

                    for i in range(len(libs)):
                        libs[i] = '-l{}'.format(libs[i])

                    libs = ' '.join(libs)

                    try:
                        os.mkdir(
                            os.path.join(OBJ_dir, 'usr', 'include', 'nss'),
                            mode=0o755
                            )
                    except:
                        pass

#                    os.symlink(
#                        'nspr',
#                        OBJ_dir + os.path.sep + 'usr' +
#                        os.path.sep + 'include' + os.path.sep + 'nss'
#                        )

                    for i in ['private', 'public']:
                        org.wayround.utils.file.files_by_mask_copy_to_dir(
                            os.path.join(dist_dir, i, 'nss'),
                            os.path.join(OBJ_dir, 'usr', 'include', 'nss'),
                            mask='*'
                            )

                    logging.info("Writing package config files")
                    pkg_config = """
prefix={prefix}
exec_prefix=${{prefix}}
libdir=${{exec_prefix}}/lib
includedir=${{exec_prefix}}/include/nss

Name: NSS
Description: Network Security Services
Version: {nss_major_version}.{nss_minor_version}.{nss_patch_version}
Libs: -L${{libdir}} {libs}
Cflags: -I${{includedir}}
""".format(
                        prefix='/usr',
                        nss_major_version=pkg_info['pkg_nameinfo']['groups']['version_list'][0],
                        nss_minor_version=pkg_info['pkg_nameinfo']['groups']['version_list'][1],
                        nss_patch_version=pkg_info['pkg_nameinfo']['groups']['version_list'][2],
                        libs=libs
                        )
# -lnss{nss_major_version} -lnssutil{nss_major_version} -lsmime{nss_major_version} -lssl{nss_major_version} -lsoftokn{nss_major_version}

                    try:
                        os.mkdir(
                            OBJ_dir + os.path.sep + 'usr' + os.path.sep +
                            'lib' + os.path.sep + 'pkgconfig',
                            mode=0o755
                            )
                    except:
                        pass

                    f = open(
                        OBJ_dir + os.path.sep + 'usr' + os.path.sep +
                        'lib' + os.path.sep + 'pkgconfig' + os.path.sep + 'nss.pc',
                        'w'
                        )

                    f.write(pkg_config)
                    f.close()

                    nss_config = """\
#!/bin/sh

prefix={prefix}
exec_prefix={prefix}

major_version={nss_major_version}
minor_version={nss_minor_version}
patch_version={nss_patch_version}

usage()
{{
    cat <<EOF
Usage: nss-config [OPTIONS] [LIBRARIES]
Options:
    [--prefix[=DIR]]
    [--exec-prefix[=DIR]]
    [--includedir[=DIR]]
    [--libdir[=DIR]]
    [--version]
    [--libs]
    [--cflags]
Dynamic Libraries:
    nss
    nssutil
    smime
    ssl
    softokn
EOF
    exit $1
}}

if test $# -eq 0; then
    usage 1 1>&2
fi

lib_nss=yes
lib_nssutil=yes
lib_smime=yes
lib_ssl=yes
lib_softokn=yes

while test $# -gt 0; do
  case "$1" in
  -*=*) optarg=`echo "$1" | sed 's/[-_a-zA-Z0-9]*=//'` ;;
  *) optarg= ;;
  esac

  case $1 in
    --prefix=*)
      prefix=$optarg
      ;;
    --prefix)
      echo_prefix=yes
      ;;
    --exec-prefix=*)
      exec_prefix=$optarg
      ;;
    --exec-prefix)
      echo_exec_prefix=yes
      ;;
    --includedir=*)
      includedir=$optarg
      ;;
    --includedir)
      echo_includedir=yes
      ;;
    --libdir=*)
      libdir=$optarg
      ;;
    --libdir)
      echo_libdir=yes
      ;;
    --version)
      echo ${{major_version}}.${{minor_version}}.${{patch_version}}
      ;;
    --cflags)
      echo_cflags=yes
      ;;
    --libs)
      echo_libs=yes
      ;;
    nss)
      lib_nss=yes
      ;;
    nssutil)
      lib_nssutil=yes
      ;;
    smime)
      lib_smime=yes
      ;;
    ssl)
      lib_ssl=yes
      ;;
    softokn)
      lib_softokn=yes
      ;;
    *)
      usage 1 1>&2
      ;;
  esac
  shift
done

# Set variables that may be dependent upon other variables
if test -z "$exec_prefix"; then
    exec_prefix=`pkg-config --variable=exec_prefix nss`
fi
if test -z "$includedir"; then
    includedir=`pkg-config --variable=includedir nss`
fi
if test -z "$libdir"; then
    libdir=`pkg-config --variable=libdir nss`
fi

if test "$echo_prefix" = "yes"; then
    echo $prefix
fi

if test "$echo_exec_prefix" = "yes"; then
    echo $exec_prefix
fi

if test "$echo_includedir" = "yes"; then
    echo $includedir
fi

if test "$echo_libdir" = "yes"; then
    echo $libdir
fi

if test "$echo_cflags" = "yes"; then
    echo -I$includedir
fi

if test "$echo_libs" = "yes"; then
      libdirs="-L$libdir"
      if test -n "$lib_nss"; then
    libdirs="$libdirs -lnss${{major_version}}"
      fi
      if test -n "$lib_nssutil"; then
        libdirs="$libdirs -lnssutil${{major_version}}"
      fi
      if test -n "$lib_smime"; then
    libdirs="$libdirs -lsmime${{major_version}}"
      fi
      if test -n "$lib_ssl"; then
    libdirs="$libdirs -lssl${{major_version}}"
      fi
      if test -n "$lib_softokn"; then
        libdirs="$libdirs -lsoftokn${{major_version}}"
      fi
      echo $libdirs
fi
""".format(
                        prefix='/usr',
                        nss_major_version=pkg_info['pkg_nameinfo']['groups']['version_list'][0],
                        nss_minor_version=pkg_info['pkg_nameinfo']['groups']['version_list'][1],
                        nss_patch_version=pkg_info['pkg_nameinfo']['groups']['version_list'][2]
                        )

                    f = open(
                        OBJ_dir + os.path.sep + 'usr' + os.path.sep +
                        'bin' + os.path.sep + 'nss-config',
                        'w'
                        )

                    f.write(nss_config)
                    f.close()

                    files = os.listdir(
                        OBJ_dir + os.path.sep + 'usr' + os.path.sep + 'bin'
                        )

                    for i in files:
                        os.chmod(
                            OBJ_dir + os.path.sep + 'usr' + os.path.sep +
                            'bin' + os.path.sep + i,
                            mode=0o755
                            )

                    logging.info("Moving files to distribution dir")
                    shutil.move(OBJ_dir + os.path.sep + 'usr', dest_dir)
                    logging.info("Files moved")

    return ret
