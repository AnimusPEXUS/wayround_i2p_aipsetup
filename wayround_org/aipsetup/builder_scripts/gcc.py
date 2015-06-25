
import logging
import os.path
import subprocess
import collections
import shutil

import wayround_org.utils.file
import wayround_org.utils.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.binutils


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        self.forced_target = True
        ret = dict()
        ret['cc_file'] = os.path.join(
            self.dst_dir, 'multiarch', self.host, 'bin', 'cc'
            )
        ret['libcpp_file'] = os.path.join(
            self.dst_dir, 'multiarch', self.host, 'lib', 'cpp'
            )
        return ret

    def define_actions(self):
        ret = super().define_actions()

        ret['edit_package_info'] = self.builder_action_edit_package_info
        ret.move_to_end('edit_package_info', False)

        if self.is_crossbuilder:

            logging.info(
                "Crosscompiler building detected. splitting process on two parts"
                )

            ret['build_01'] = self.builder_action_build_01
            ret['distribute_01'] = self.builder_action_distribute_01

            ret['intermediate_instruction_1'] = \
                self.builder_action_intermediate_instruction_1

            ret['build_02'] = self.builder_action_build_02
            ret['distribute_02'] = self.builder_action_distribute_02

            ret['intermediate_instruction_2'] = \
                self.builder_action_intermediate_instruction_2

            ret['build_03'] = self.builder_action_build_03
            ret['distribute_03'] = self.builder_action_distribute_03

            del ret['build']
            del ret['distribute']

        if not self.is_crossbuilder:
            ret['after_distribute'] = self.builder_action_after_distribute

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        pi = self.package_info

        if self.is_crossbuilder:
            pi['pkg_info']['name'] = 'cb-gcc-{}'.format(self.target)
        else:
            pi['pkg_info']['name'] = 'gcc'

        bs = self.control
        bs.write_package_info(pi)

        return ret

    def builder_action_extract(self, called_as, log):

        ret = super().builder_action_extract(called_as, log)

        if ret == 0:

            for i in ['mpc', 'mpfr', 'cloog',
                      'isl',
                      # 'gmp', # NOTE: sometimes gcc could not compile like
                      #                this.
                      #                so use system gmp
                      # requires compiler for bootstrap
                      # 'binutils', 'gdb', 'glibc'
                      ]:

                if autotools.extract_high(
                        self.buildingsite,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    log.error("Can't extract component: {}".format(i))
                    ret = 2

        return ret

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(called_as, log)

        if self.is_crossbuilder:
            prefix = os.path.join(
                '/', 'usr', 'crossbuilders', self.target
                )

            ret = [
                '--prefix=' + prefix

                ] + autotools.calc_conf_hbt_options(self)

        if self.is_crossbuilder:
            ret += sorted([
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada',
                #'--enable-bootstrap',
                '--enable-threads=posix',
                '--enable-multiarch',
                # '--enable-multilib',
                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared',

                #'--without-headers',
                '--with-sysroot=/usr/crossbuilders/{}'.format(self.target)
                ])

        if self.is_crossbuild:
            ret += sorted([
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada',
                #'--enable-bootstrap',
                '--enable-threads=posix',
                '--enable-multiarch',
                '--enable-multilib',
                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared'
                ])

        if not self.is_crossbuild and not self.is_crossbuilder:
            ret += sorted([
                #'--with-sysroot={}'.format(
                #    os.path.join('/', 'multiarch', self.host)
                #    ),
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada',

                '--disable-bootstrap',

                '--enable-threads=posix',

                #'--enable-multiarch',
                #'--enable-multilib',
                '--disable-multilib',
                '--disable-multiarch',

                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared',
                #'--enable-targets=x86_64-pc-linux-gnu,i686-pc-linux-gnu'
                #'-Wl,--rpath={}'.format(
                #    os.path.join('/', 'multiarch', self.host, 'lib')
                #    ),
                ])

            """
            for i in ret:
                if i.startswith('--target='):
                    ret.remove(i)
                    break
            """
        return ret

    def builder_action_before_checks(self, called_as, log):
        print(
            "stop: checks! If You want them (it's good if You do)\n"
            "then continue build with command: aipsetup build continue checks+\n"
            "else continue build with command: aipsetup build continue distribute+\n"
            )
        ret = 1
        return ret

    def builder_action_checks(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['check'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):

        if not os.path.exists(self.custom_data['cc_file']):
            os.symlink('gcc', self.custom_data['cc_file'])

        if (not os.path.exists(self.custom_data['libcpp_file'])
                and not os.path.islink(self.custom_data['libcpp_file'])):
            os.symlink('../bin/cpp', self.custom_data['libcpp_file'])

        return 0

    def builder_action_build_01(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['all-gcc'],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_01(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install-gcc',
                'DESTDIR=' + self.dst_dir
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_intermediate_instruction_1(self, called_as, log):
        print("""\
---------------
Now You need to pack and install this gcc build.
Then install linux-hraders and glibc (headers and, maybe, some other parts).
After what - continue building from 'build_02+' action
---------------
""")
        return 1

    def builder_action_build_02(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['all-target-libgcc'],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_02(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install-target-libgcc',
                'DESTDIR=' + self.dst_dir
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_intermediate_instruction_2(self, called_as, log):
        print("""\
---------------
Now You need to pack and install this gcc build and then complete
glibc build (and install it too).
After what - continue building this gcc from 'build_03+' action
---------------
""")
        return 1

    def builder_action_build_03(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_03(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'DESTDIR=' + self.dst_dir
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
