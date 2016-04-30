
import os.path
import logging
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

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = False

        ret = dict()
        ret['cc_file'] = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(), 'bin', 'cc'
            )
        ret['libcpp_file'] = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'lib',
            'cpp'
            )
        return ret

    def define_actions(self):
        ret = super().define_actions()

        ret['edit_package_info'] = self.builder_action_edit_package_info
        ret.move_to_end('edit_package_info', False)

        if self.get_is_crossbuilder():

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

        if not self.get_is_crossbuilder():
            pass
            # ret['after_distribute'] = self.builder_action_after_distribute

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.get_package_info()['pkg_info']['name']
        except:
            name = None

        pi = self.get_package_info()

        if self.get_is_crossbuilder():
            pi['pkg_info']['name'] = 'cb-gcc-{}'.format(
                self.get_target_from_pkgi()
                )
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
                      #'gmp',
                      # NOTE: sometimes gcc could not compile with gmp.
                      #       so use system gmp
                      # requires compiler for bootstrap
                      # 'binutils', 'gdb', 'glibc'
                      ]:

                if autotools.extract_high(
                        self.buildingsite_path,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    log.error("Can't extract component: {}".format(i))
                    ret = 2

        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        return {}

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)

        if self.get_is_crossbuilder():

            prefix = wayround_org.utils.path.join(
                self.get_host_crossbuilders_dir(),
                self.get_target_from_pkgi()
                )

            ret = [
                '--prefix=' + prefix,
                '--mandir=' +
                wayround_org.utils.path.join(prefix, 'share', 'man'),
                '--sysconfdir=/etc',
                '--localstatedir=/var',
                '--enable-shared',
                '--disable-gold',
                ] + autotools.calc_conf_hbt_options(self)

        if self.get_is_crossbuilder():
            ret += [
                '--disable-gold',
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada',
                '--disable-bootstrap',
                '--enable-threads=posix',

                '--disable-multiarch',
                '--disable-multilib',

                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared',

                # use it when you haven't built glibc basic parts yet
                # '--without-headers',

                # use it when you already have glibc headers and basic parts
                # installed
                # using this parameter may reqire creating hacky symlink
                # pointing to /multiarch dir - you'll see error what file not
                # found.
                # so after gcc and glibc built and installed - rebuild gcc both
                # without --with-sysroot= and without --without-headers options
                '--with-sysroot={}'.format(
                    wayround_org.utils.path.join(
                        self.get_host_crossbuilders_dir(),
                        self.target
                        )
                    )
                # TODO: need to try building without --with-sysroot if possible
                ]

        if self.get_is_crossbuild():
            ret += [
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada',
                '--disable-bootstrap',
                '--enable-threads=posix',

                '--disable-multiarch',
                '--disable-multilib',

                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared',

                '--disable-gold',
                ]

        if not self.get_is_crossbuild() and not self.get_is_crossbuilder():
            ret += [

                '--disable-gold',

                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',

                # NOTE: gcc somtimes fails to crossbuild self with go enabled
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada', 

                '--disable-bootstrap',

                '--enable-threads=posix',

                # wine Wow64 support requires this
                # ld: Relocatable linking with relocations from format
                #     elf64-x86-64 (aclui.Itv5tk.o) to format elf32-i386
                #     (aclui.pnv73q.o) is not supported
                '--enable-multiarch',
                '--enable-multilib',

                #'--disable-multiarch',
                #'--disable-multilib',

                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared',

                #'--oldincludedir=' +
                # wayround_org.utils.path.join(
                #    self.get_host_dir(),
                #    'include'
                #    ),

                #'--with-gxx-include-dir={}'.format(
                #    wayround_org.utils.path.join(
                #        self.get_host_arch_dir(),
                #        'include-c++',
                #        #'c++',
                #        #'5.2.0'
                #        )
                #    ),

                # experimental option for this place
                #
                # NOTE: without it gcc tryes to use incompatible
                #       /lib/crt*.o files.
                #
                # NOTE: this is required. else libs will be searched
                #       in /lib and /usr/lib, but not in
                #       /multihost/xxx/lib!:
                '--with-sysroot={}'.format(self.get_host_dir()),

                # '--with-build-sysroot={}'.format(self.get_host_arch_dir())
                '--with-native-system-header-dir={}'.format(
                    wayround_org.utils.path.join(
                        #'/',
                        #'multiarch',
                        # self.get_host_from_pkgi(),
                        self.get_host_dir(),
                        'include'
                    )
                ),
                #'--with-isl={}'.format(self.get_host_dir())
            ]

            if self.get_host_from_pkgi().startswith('x86_64'):
                ret += [
                    '--enable-targets=all'
                    ]

        return ret

    # def builder_action_build_define_environment(self, called_as, log):
    def builder_action_build_define_environment(self, called_as, log):
        return {}

    '''
    def builder_action_build_define_environment(self, called_as, log):
        ret = super().builder_action_build_define_environment(called_as, log)

        if self.get_arch_from_pkgi().startswith('x86_64'):

            for i in ['lib', 'lib64', 'lib32', 'libx32']:

                joined = wayround_org.utils.path.join(
                    '/multiarch', 'i686-pc-linux-gnu', i
                    )

                if os.path.isdir(joined):
                    ret['LD_LIBRARY_PATH'] += ':{}'.format(joined)

        return ret
    '''

    # def builder_action_build_define_cpu_count(self, called_as, log):
    #    return 1

    def builder_action_before_checks(self, called_as, log):
        log.info(
            "stop: checks! If You want them (it's good if You do)\n"
            "then continue build with command: aipsetup build continue checks+\n"
            "else continue build with command: aipsetup build continue distribute+\n"
            )
        ret = 1
        return ret

    def builder_action_checks(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
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
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=['all-gcc'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_01(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'install-gcc',
                'DESTDIR={}'.format(self.get_dst_dir())
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_intermediate_instruction_1(self, called_as, log):
        log.info("""
---------------
Now You need to pack and install this gcc build.
Then install linux-headers and glibc (headers and, maybe, some other parts).
After what - continue building from 'build_02+' action
---------------
""")
        return 1

    def builder_action_build_02(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=['all-target-libgcc'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_02(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'install-target-libgcc',
                'DESTDIR={}'.format(self.get_dst_dir())
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_intermediate_instruction_2(self, called_as, log):
        log.info("""
---------------
Now You need to pack and install this gcc build and then complete
glibc build (and install it too).
After what - continue building this gcc from 'build_03+' action
---------------
""")
        return 1

    def builder_action_build_03(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_03(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'install',
                'DESTDIR={}'.format(self.get_dst_dir())
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
