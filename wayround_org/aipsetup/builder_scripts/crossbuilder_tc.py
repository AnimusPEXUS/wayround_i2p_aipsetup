
import sys
import logging
import os.path
import subprocess
import collections
import inspect
import glob
import shutil

import wayround_org.utils.file
import wayround_org.utils.path


import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.gcc
import wayround_org.aipsetup.builder_scripts.binutils
import wayround_org.aipsetup.builder_scripts.linux
import wayround_org.aipsetup.builder_scripts.glibc
#import wayround_org.aipsetup.builder_scripts.crossbuilder_binutils01


def calculate_prefix(dst_dir, target):

    return wayround_org.utils.path.join(
        '/', 'usr', 'crossbuilders', target
        #, 'usr'
        )


def calculate_dst_dir_prefix(dst_dir, target):
    c_p = calculate_prefix(dst_dir, target)
    return wayround_org.utils.path.join(dst_dir, c_p,)


def calc_path_addition(dst_dir, target):

    c_p = calculate_prefix(dst_dir, target)

    ret = '{}:{}:{}'.format(
        os.environ['PATH'],
        wayround_org.utils.path.join(dst_dir, c_p, 'bin'),
        wayround_org.utils.path.join(dst_dir, c_p, 'sbin')
        )

    return ret


class LinuxHeadersBuilder(wayround_org.aipsetup.builder_scripts.linux.Builder):

    def define_custom_data(self):
        ret = super().define_custom_data()
        self.source_configure_reldir = 'linux'
        return ret

    def define_actions(self):
        return collections.OrderedDict([
            #('src_cleanup', self.builder_action_src_cleanup),
            #('extract', self.builder_action_extract),
            ('distr_headers_all',
                self.builder_action_distr_headers_all)
            ])

    def builder_action_extract(self, called_as, log):
        ret = autotools.extract_high(
            self.buildingsite,
            'linux',
            log=log,
            unwrap_dir=False,
            rename_dir='linux'
            )
        return ret


class BinutilsBuilder(
        wayround_org.aipsetup.builder_scripts.std.Builder
        ):

    def define_custom_data(self):
        self.separate_build_dir = False
        self.source_configure_reldir = 'binutils'
        self.bld_dir = self.bld_dir + '_binutils'
        return

    def define_actions(self):
        return collections.OrderedDict([
            # ('src_cleanup', self.builder_action_src_cleanup),
            #('bld_cleanup', self.builder_action_bld_cleanup),
            #('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_extract(self, called_as, log):
        ret = autotools.extract_high(
            self.buildingsite,
            'binutils',
            log=log,
            unwrap_dir=False,
            rename_dir='binutils'
            )
        return ret

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            #'--enable-targets=all',

            # '--with-sysroot' makes problems when building native GCC.
            # does proplrms arise when building crosscompiler?
            '--with-sysroot',

            # '--enable-multiarch',

            #'--enable-multilib',
            '--disable-multilib',

            #                    '--disable-libada',
            #                    '--enable-bootstrap',
            #'--enable-64-bit-bfd',
            '--disable-werror',
            '--enable-libada',
            '--enable-libssp',
            #'--enable-objc-gc',
            # '--enable-targets='
            # 'i486-pc-linux-gnu,'
            # 'i586-pc-linux-gnu,'
            # 'i686-pc-linux-gnu,'
            # 'i786-pc-linux-gnu,'
            # 'ia64-pc-linux-gnu,'
            # 'x86_64-pc-linux-gnu,'
            # 'aarch64-linux-gnu',
            ]

    def builder_action_configure_define_environment(self, called_as, log):
        return {
            'PATH': calc_path_addition(self.dst_dir, self.target)
            }


class GCC01Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        self.source_configure_reldir = 'gcc'
        self.bld_dir = self.bld_dir + '_gcc'
        return

    def define_actions(self):
        return collections.OrderedDict([
            # ('src_cleanup', self.builder_action_src_cleanup),
            #('bld_cleanup', self.builder_action_bld_cleanup),
            # ('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_extract(self, called_as, log):
        ret = autotools.extract_high(
            self.buildingsite,
            'gcc',
            log=log,
            unwrap_dir=False,
            rename_dir='gcc'
            )
        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        return {
            'PATH': calc_path_addition(self.dst_dir, self.target)
            }

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            # experimental options
            # '--enable-targets=all',
            #'--enable-tls',
            #'--enable-nls',
            #'--disable-nls',

            # '--enable-targets='
            # 'i486-pc-linux-gnu,'
            # 'i586-pc-linux-gnu,'
            # 'i686-pc-linux-gnu,'
            # 'i786-pc-linux-gnu,'
            # 'ia64-pc-linux-gnu,'
            # 'x86_64-pc-linux-gnu,'
            # 'aarch64-linux-gnu',

            # then lto enabled it causes problems to systemd.
            # some time has passed since then - trying to enable lto
            # '--disable-lto',

            # normal options
            #'--enable-__cxa_atexit',

            # disabled for experiment
            #'--with-arch-32=i486',
            #'--with-tune=generic',

            #'--enable-languages=c,c++,java,objc,obj-c++,ada,fortran',
            #'--enable-languages=c,c++,ada',
            '--enable-languages=c,c++',

            # '--enable-bootstrap',

            #'--enable-threads=posix',
            '--disable-threads',

            #'--enable-multiarch',
            '--disable-multiarch',

            #'--enable-multilib',
            '--disable-multilib',

            #'--enable-checking=release',

            #'--with-gmp=/usr',
            #'--with-mpfr=/usr',

            # '--with-build-time-tools=
            # /home/agu/_sda3/_UNICORN/b/gnat/
            # gnat-gpl-2014-x86-linux-bin',

            #'--enable-shared',
            #'--disable-shared',

            #'--with-sysroot=' + os.path.normpath(
            #    os.path.join(prefix, '..')
            #    ),
            #'--without-headers',
            #'--with-newlib',


            # from lfs - to avoid using make all-gcc
            #'--disable-decimal-float',
            '--disable-threads',
            #'--disable-libatomic',
            #'--disable-libgomp',
            #'--disable-libitm',
            #'--disable-libquadmath',
            #'--disable-libsanitizer',
            # '--disable-libssp',
            #'--disable-libvtv',
            #'--disable-libcilkrts',
            #'--disable-libstdc++-v3',
            ]

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['all-gcc'],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install-gcc',
                'DESTDIR=' + self.dst_dir
                ],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret


class Glibc01Builder(wayround_org.aipsetup.builder_scripts.glibc.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        self.source_configure_reldir = 'glibc'
        self.bld_dir = self.bld_dir + '_glibc'
        return

    def define_actions(self):
        return collections.OrderedDict([
            # ('src_cleanup', self.builder_action_src_cleanup),
            #('bld_cleanup', self.builder_action_bld_cleanup),
            #('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('distribute-headers1', self.builder_action_distribute_headers1),
            ('distribute-headers2', self.builder_action_distribute_headers2),
            ('copy_crt_objects', self.builder_action_copy_crt_objects),
            ('create_dummy_libc', self.builder_action_create_dummy_libc)
            ])

    def builder_action_extract(self, called_as, log):
        ret = autotools.extract_high(
            self.buildingsite,
            'glibc',
            log=log,
            unwrap_dir=False,
            rename_dir='glibc'
            )
        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        return {
            'PATH': calc_path_addition(self.dst_dir, self.target)
            }

    def builder_action_configure_define_options(self, called_as, log):
        headers_path = os.path.join(
            calculate_dst_dir_prefix(self.dst_dir, self.target),
            'include'
            )

        if self.is_crossbuild or self.is_crossbuilder:
            os.path.normpath(os.path.join(headers_path, '..'))

        return super().builder_action_configure_define_options(called_as, log) + [
            #'--enable-obsolete-rpc',
            '--enable-kernel=4.0',
            #'--enable-tls',
            '--with-elf',

            #'--enable-multi-arch',
            #'--enable-multiarch',

            #'--enable-multilib',
            #'--disable-multilib',

            # this is from configure --help. configure looking for
            # linux/version.h file

            '--with-headers=' + headers_path,

            #'--enable-shared',

            '--prefix=' + prefix,
            '--mandir=' + mandir,
            '--sysconfdir=' + sysconfdir,
            '--localstatedir=' + localstatedir,

            '--host=' + self.target,
            # host must be same as target this time
            '--build=' + self.build,
            '--target=' + self.target,
            'libc_cv_forced_unwind=yes'
            ]

    def builder_action_distribute_headers1(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install-bootstrap-headers=yes',
                #'install',
                'install-headers',
                'DESTDIR=' + self.dst_dir
                ],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_headers2(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'csu/subdir_lib'
                ],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_copy_crt_objects(self, called_as, log):

        gres = glob.glob(os.path.join(self.bld_dir, 'csu', '*crt*.o'))

        for i in gres:
            from_ = i
            to = os.path.join(
                calculate_dst_dir_prefix(
                    self.dst_dir,
                    self.target
                    ),
                self.target,
                'lib'
                )
            log.info("Copying `{}' to `{}'".format(from_, to))
            shutil.copy2(from_, to)

        return 0

    def builder_action_create_dummy_libc(self, called_as, log):
        cwd = os.path.join(
            calculate_dst_dir_prefix(self.dst_dir, self.target),
            'lib'
            )
        cmd = [
            os.path.join(
                '..', 'bin',
                self.target + '-gcc'
                ),
            '-nostdlib',
            '-nostartfiles',
            '-shared',
            '-x',
            'c',
            '/dev/null',
            '-o',
            'libc.so'
            ]
        logging.info("directory: {}".format(cwd))
        logging.info("cmd: {}".format(' '.join(cmd)))
        p = subprocess.Popen(cmd, cwd=cwd)
        ret = p.wait()
        return ret


class GCC02Builder(GCC01Builder):

    def define_actions(self):
        return collections.OrderedDict([
            #('src_cleanup', self.builder_action_src_cleanup),
            #('bld_cleanup', self.builder_action_bld_cleanup),
            #('extract', self.builder_action_extract),
            #('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['all-target-libgcc'],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install-target-libgcc',
                'DESTDIR=' + self.dst_dir
                ],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret


class Glibc02Builder(Glibc01Builder):

    def define_actions(self):
        return collections.OrderedDict([
            # ('src_cleanup', self.builder_action_src_cleanup),
            #('bld_cleanup', self.builder_action_bld_cleanup),
            # ('extract', self.builder_action_extract),
            #('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute),
            ])

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'DESTDIR=' + self.dst_dir
                ],
            environment={
                'PATH': calc_path_addition(self.dst_dir, self.target)
                },
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        linux_builder = LinuxHeadersBuilder(self.buildingsite)
        binutils_builder = BinutilsBuilder(self.buildingsite)
        gcc01_builder = GCC01Builder(self.buildingsite)
        glibc01_builder = Glibc01Builder(self.buildingsite)
        gcc02_builder = GCC02Builder(self.buildingsite)
        glibc02_builder = Glibc02Builder(self.buildingsite)

        ret = {
            'linux_builder': linux_builder,
            'binutils_builder': binutils_builder,
            'gcc01_builder': gcc01_builder,
            'glibc01_builder': glibc01_builder,
            'gcc02_builder': gcc02_builder,
            'glibc02_builder': glibc02_builder
            }

        return ret

    def define_actions(self):

        action_list = []

        action_list += [
            ('apply_pkg_nameinfo', self.builder_action_edit_package_info),
            ('extract_libs', self.builder_action_extract_libs),
            ('extract_sources', self.builder_action_extract_sources),
            ('copy_libs_into_sources',
                self.builder_action_copy_libs_into_sources),
            ('make_build_dirs', self.builder_action_make_build_dirs),
            ('clean_build_dirs', self.builder_action_clean_build_dirs),
            ('create_etc_files', self.builder_action_create_etc_files)
            ]

        for j in [
                'linux',
                'binutils',
                'gcc01', 'glibc01',
                'gcc02', 'glibc02'
                ]:

            s_actions =\
                self.custom_data[j + '_builder'].define_actions()

            for i in s_actions.keys():
                action_list.append(
                    (j + '_' + i, s_actions[i])
                    )

        return collections.OrderedDict(action_list)

    def builder_action_extract_libs(self, called_as, log):

        ret = 0

        failed_unpack = []

        for i in ['gmp', 'cloog', 'isl', 'mpc', 'mpfr']:

            if not os.path.isdir(os.path.join(self.src_dir, i)):

                if autotools.extract_high(
                        self.buildingsite,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:
                    failed_unpack.append(i)
                    ret = 1

        for i in sorted(failed_unpack):
            log.error("failed unpack: {}".format(i))

        return ret

    def builder_action_extract_sources(self, called_as, log):

        ret = 0

        failed_unpack = []

        for i in [
                'binutils',
                'gcc',
                'linux',
                'glibc'
                ]:

            if not os.path.isdir(os.path.join(self.src_dir, i)):

                if autotools.extract_high(
                        self.buildingsite,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    failed_unpack.append(i)
                    ret = 1

        for i in sorted(failed_unpack):
            log.error("failed unpack: {}".format(i))

        return ret

    def builder_action_copy_libs_into_sources(self, called_as, log):

        for i in ['gmp', 'cloog', 'isl', 'mpc', 'mpfr']:

            for j in ['binutils', 'gcc']:

                from_ = os.path.join(
                    self.src_dir, i
                    )
                to = os.path.join(
                    self.src_dir, j, i
                    )

                log.info("Copying `{}' to `{}'".format(from_, to))
                shutil.copytree(from_, to)

        return 0

    def builder_action_make_build_dirs(self, called_as, log):

        ret = 0

        for i in [
                'binutils',
                'gcc',
                'linux',
                'glibc'
                ]:

            dirname = self.bld_dir + '_' + i

            try:
                os.makedirs(dirname, exist_ok=True)
            except:
                logging.exception(
                    "can't make building dir: {}".format(i)
                    )
                ret = 1

        return ret

    def builder_action_clean_build_dirs(self, called_as, log):

        ret = 0

        for i in [
                'binutils',
                'gcc',
                'linux',
                'glibc'
                ]:

            dirname = self.bld_dir + '_' + i

            if os.path.isdir(dirname):
                logging.info("cleaningup building dir: {}".format(dirname))

                try:
                    wayround_org.utils.file.cleanup_dir(dirname)
                except:
                    logging.exception(
                        "can't make building dir: {}".format(i)
                        )
                    ret = 1

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        files = os.listdir(self.tar_dir)

        tar = None
        for i in files:
            if i.startswith('glibc'):
                tar = i

        if tar is None:
            ret = 1
        else:
            bs = wayround_org.aipsetup.build.BuildingSiteCtl(self.buildingsite)
            bs.apply_pkg_nameinfo_on_buildingsite(tar)
        return ret

    def builder_action_create_etc_files(self, called_as, log):

        etc_dir = os.path.join(self.dst_dir, 'etc', 'profile.d', 'SET')
        etc_dir_file = os.path.join(
            etc_dir,
            '011.{}.binutils'.format(self.target)
            )

        os.makedirs(etc_dir, exist_ok=True)

        if not os.path.isdir(etc_dir):
            raise Exception("Required dir creation error")

        fi = open(etc_dir_file, 'w')

        fi.write(
            """\
#!/bin/bash
export PATH=$PATH:/usr/lib/unicorn_crossbuilders/{target}/usr/bin:\
/usr/lib/unicorn_crossbuilders/{target}/usr/sbin
""".format(target=self.target)
            )

        fi.close()

        return 0
