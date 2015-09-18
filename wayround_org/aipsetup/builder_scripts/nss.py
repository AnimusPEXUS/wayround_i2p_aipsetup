
import glob
import os.path
import re
import shutil
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file
import wayround_org.utils.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.source_configure_reldir = 'nss'
        self.apply_host_spec_compilers_options = True
        return None

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):
        #            nss_build_all: build_coreconf build_nspr build_dbm all

        makefile = wayround_org.utils.path.join(
            self.get_src_dir(),
            self.source_configure_reldir,
            'Makefile'
            )

        f = open(makefile, 'r')
        lines = f.read().splitlines()
        f.close()

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

        f = open(makefile, 'w')
        f.write('\n'.join(lines))
        f.close()
        return 0

    def builder_action_build_define_cpu_count(self, called_as, log):
        # FIXME: nss can't build with more than 1 j
        return 1

    def builder_action_build_define_args(self, called_as, log):
        opts64 = []
        if self.get_arch_from_pkgi() == 'x86_64-pc-linux-gnu':
            opts64 = ['USE_64=1']

        ret = [
            'nss_build_all',
            'BUILD_OPT=1',
            'NSPR_INCLUDE_DIR={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'include',
                    'nspr'
                    )
                ),
            'USE_SYSTEM_ZLIB=1',

            'ZLIB_LIBS=-lz',
            'NSS_USE_SYSTEM_SQLITE=1',
            ] + opts64 + self.all_automatic_flags_as_list()

        return ret

    def builder_action_distribute(self, called_as, log):

        ret = 0

        dest_dir = self.get_dst_dir()

        dist_dir = wayround_org.utils.path.join(
            self.get_src_dir(),
            'dist'
            )

        OBJ_dir = glob.glob(wayround_org.utils.path.join(dist_dir, '*.OBJ'))

        if len(OBJ_dir) != 1:
            log.error("`dist/Linux*' must be exactly one")
            ret = 10

        if ret == 0:

            OBJ_dir = OBJ_dir[0]

            OBJ_dir = wayround_org.utils.path.join(
                dist_dir,
                os.path.basename(OBJ_dir)
                )

            OBJ_dir_bin = wayround_org.utils.path.join(OBJ_dir, 'bin')
            OBJ_dir_lib = wayround_org.utils.path.join(
                OBJ_dir,
                'lib'
                )
            OBJ_dir_include = wayround_org.utils.path.join(OBJ_dir, 'include')

            OBJ_dir_rmarch = wayround_org.utils.path.join(
                OBJ_dir,
                'multihost'
                )

            OBJ_dir_march = wayround_org.utils.path.join(
                OBJ_dir,
                self.calculate_install_prefix()
                )

            OBJ_dir_ma_bin = wayround_org.utils.path.join(
                OBJ_dir_march,
                'bin'
                )
            OBJ_dir_ma_lib = wayround_org.utils.path.join(
                OBJ_dir_march,
                'lib'
                )
            OBJ_dir_ma_lib_pkgconfig = wayround_org.utils.path.join(
                OBJ_dir_ma_lib,
                'pkgconfig'
                )
            OBJ_dir_ma_include = wayround_org.utils.path.join(
                OBJ_dir_march,
                'include'
                )

            OBJ_dir_ma_include_nss = wayround_org.utils.path.join(
                OBJ_dir_ma_include,
                'nss'
                )

        if ret == 0:

            # convert links in bin

            log.info("Converting symbolic links to files")
            log.info(
                "    in `{}'".format(
                    wayround_org.utils.path.relpath(
                        OBJ_dir_bin,
                        self.get_src_dir()
                        )
                    )
                )

            files = sorted(os.listdir(OBJ_dir_bin))

            errors = 0
            for i in files:
                log.info("    {}".format(i))
                if wayround_org.utils.file.convert_symlink_to_file(
                        wayround_org.utils.path.join(OBJ_dir_bin, i)
                        ) != 0:
                    errors += 1
                    log.info("        error")
                else:
                    log.info("        ok")

            if errors != 0:
                ret = 2

        if ret == 0:

            # convert links in lib

            log.info("Converting symbolic links to files")
            log.info(
                "    in `{}'".format(
                    wayround_org.utils.path.relpath(
                        OBJ_dir_lib,
                        self.get_src_dir()
                        )
                    )
                )

            files = sorted(os.listdir(OBJ_dir_lib))

            errors = 0
            for i in files:
                log.info("    {}".format(i))
                if wayround_org.utils.file.convert_symlink_to_file(
                        wayround_org.utils.path.join(OBJ_dir_lib, i)
                        ) != 0:
                    errors += 1
                    log.info("        error")
                else:
                    log.info("        ok")

            # ret = 333 # for debugging

            if errors != 0:
                ret = 2

        # if ret == 0:
        if False:

            # NOTE: this is dead code. lived here for history

            # comment this 'for' if want more files
            '''
            for i in files:
                if not i in ['certutil', 'nss-config', 'pk12util']:
                    os.unlink(
                        wayround_org.utils.path.join(OBJ_dir, 'bin', i)
                        )
            '''
            '''
            if wayround_org.utils.file.dereference_files_in_dir(
                    OBJ_dir
                    ) != 0:
                log.error(
                    "Some errors while dereferencing symlinks. see above."
                    )
                ret = 11
            '''

        if ret == 0:

            log.info("Preparing distribution dir tree")

            os.makedirs(OBJ_dir_include, exist_ok=True)
            os.makedirs(OBJ_dir_march, exist_ok=True)

            for i in [
                    OBJ_dir_bin,
                    OBJ_dir_lib,
                    OBJ_dir_include
                    ]:
                shutil.move(i, OBJ_dir_march)

            log.info("    composing shared libraries list")

            libs = os.listdir(OBJ_dir_ma_lib)

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

            log.info("    working on includes")

            os.makedirs(OBJ_dir_ma_include_nss, exist_ok=True)
            # os.symlink(
            #    'nspr',
            #    OBJ_dir + os.path.sep + 'usr' +
            #    os.path.sep + 'include' + os.path.sep + 'nss'
            #    )

            for i in ['private', 'public']:
                wayround_org.utils.file.files_by_mask_copy_to_dir(
                    wayround_org.utils.path.join(
                        dist_dir,
                        i,
                        'nss'
                        ),
                    OBJ_dir_ma_include_nss,
                    mask='*'
                    )

            log.info("Writing package config files")

            nss_major_version = 0
            nss_minor_version = 0
            nss_patch_version = 0

            if (
                len(
                    self.get_package_info()['pkg_nameinfo'][
                        'groups']['version_list']
                    )
                    > 0):
                nss_major_version = \
                    self.get_package_info()['pkg_nameinfo'][
                        'groups']['version_list'][0]

            if (
                len(
                    self.get_package_info()['pkg_nameinfo'][
                        'groups']['version_list'])
                    > 1):
                nss_minor_version = \
                    self.get_package_info()['pkg_nameinfo'][
                        'groups']['version_list'][1]

            if (
                len(
                    self.get_package_info()['pkg_nameinfo'][
                        'groups']['version_list'])
                    > 2):
                nss_patch_version = \
                    self.get_package_info()['pkg_nameinfo'][
                        'groups']['version_list'][2]

            log.info(
                "Applying version {}.{}.{}".format(
                    nss_major_version,
                    nss_minor_version,
                    nss_patch_version
                    )
                )

            pkg_config = """
prefix={prefix}
exec_prefix={prefix}
libdir={libdir}
includedir=${{exec_prefix}}/include/nss

Name: NSS
Description: Network Security Services
Version: {nss_major_version}.{nss_minor_version}.{nss_patch_version}
Libs: -L${{libdir}} {libs}
Cflags: -I${{includedir}}
""".format(
                prefix=self.calculate_install_prefix(),
                libdir=self.calculate_install_libdir(),
                nss_major_version=nss_major_version,
                nss_minor_version=nss_minor_version,
                nss_patch_version=nss_patch_version,
                libs=libs
                )
            # -lnss{nss_major_version} -lnssutil{nss_major_version}
            # -lsmime{nss_major_version} -lssl{nss_major_version}
            # -lsoftokn{nss_major_version}

            os.makedirs(
                OBJ_dir_ma_lib_pkgconfig,
                exist_ok=True
                )

            f = open(
                wayround_org.utils.path.join(
                    OBJ_dir_ma_lib_pkgconfig,
                    'nss.pc'
                    ),
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
                prefix=self.calculate_install_prefix(),
                # libdir=self.calculate_install_libdir(),
                nss_major_version=nss_major_version,
                nss_minor_version=nss_minor_version,
                nss_patch_version=nss_patch_version
                )

            os.makedirs(OBJ_dir_ma_bin, exist_ok=True)

            f = open(
                wayround_org.utils.path.join(OBJ_dir_ma_bin, 'nss-config'),
                'w'
                )

            f.write(nss_config)
            f.close()

            if self.get_arch_from_pkgi().startswith('x86_64'):
                os.rename(
                    OBJ_dir_ma_lib,
                    wayround_org.utils.path.normpath(
                        OBJ_dir_ma_lib + '/../lib64'
                        )
                    )

            log.info("    moving files to distribution dir")
            shutil.move(OBJ_dir_rmarch, dest_dir)
            log.info("        files moved")

        return ret
