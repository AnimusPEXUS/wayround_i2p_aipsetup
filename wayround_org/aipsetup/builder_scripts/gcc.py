
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
        ret['cc_file'] = os.path.join(self.dst_dir, 'usr', 'bin', 'cc')
        ret['libcpp_file'] = os.path.join(self.dst_dir, 'usr', 'lib', 'cpp')
        return ret

    def define_actions(self):
        ret = super().define_actions()
        if self.is_crossbuilder:
            ret['edit_package_info'] = self.builder_action_edit_package_info
            ret.move_to_end('edit_package_info', False)

        if not self.is_crossbuilder:
            ret['after_distribute'] = self.builder_action_after_distribute

        return ret

    def builder_action_edit_package_info(self, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        if name in ['gcc', None]:

            self.package_info['pkg_info']['name'] = \
                'cb-gcc-{target}'.format(
                    target=self.target
                    )

            bs = self.control

            bs.write_package_info(self.package_info)

        return ret

    def builder_action_extract(self, log):

        ret = super().builder_action_extract(
            log
            )

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

    def builder_action_configure_define_options(self, log):
        ''

        """
            '--with-gmp={}'.format(
                wayround_org.utils.path.join(
                    self.target_host_root,
                    '/usr'
                    )
                ),
            '--with-mpfr={}'.format(
                wayround_org.utils.path.join(
                    self.target_host_root,
                    '/usr'
                    )
                ),
        """

        ret = super().builder_action_configure_define_options(log)

        if self.is_crossbuilder:
            prefix = os.path.join(
                '/', 'usr', 'crossbuilders', self.target
                )

            ret = [
                '--prefix=' + prefix

                #'--mandir=' + os.path.join(prefix, 'share', 'man'),
                #'--sysconfdir=' +
                # self.package_info['constitution']['paths']['config'],
                #'--localstatedir=' +
                # self.package_info['constitution']['paths']['var'],
                #'--enable-shared'
                ] + autotools.calc_conf_hbt_options(self)

        ret += [
            # experimental options
            # '--enable-targets=all',

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
            #'--disable-lto',

            # normal options

            # disabled for experiment
            #'--with-arch-32=i486',
            #'--with-tune=generic',

            #'--enable-languages=c,c++,java,objc,obj-c++,fortran,ada',
            #'--enable-languages=c,c++,java,objc,obj-c++,fortran',
            #'--enable-languages=ada',
            # '--enable-bootstrap',
            # '--with-build-time-tools=
            # /home/agu/_sda3/_UNICORN/b/gnat/
            # gnat-gpl-2014-x86-linux-bin',
            #'--enable-shared'
            ]
        """
        if self.is_crossbuild or self.is_crossbuilder:
            ret += [
                '--enable-languages=c,c++',

                '--disable-libatomic',
                '--disable-libgomp',
                '--disable-libitm',
                '--disable-libquadmath',
                '--disable-libsanitizer',
                '--disable-libssp',
                '--disable-libvtv',
                '--disable-libcilkrts',
                #'--disable-libstdc++-v3',
                ]

            for i in ['CFLAGS', 'LDFLAGS', 'CXXFLAGS']:
                for j in range(len(ret) - 1, -1, -1):
                    if ret[j].startswith(i):
                        del ret[j]
        """

        if self.is_crossbuilder:
            ret += sorted([
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada,go',
                #'--enable-bootstrap',
                '--enable-threads=posix',
                '--enable-multiarch',
                # '--enable-multilib',
                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared'
                ])

        if self.is_crossbuild:
            ret += sorted([
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,ada',
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
                '--enable-tls',
                '--enable-nls',
                '--enable-__cxa_atexit',
                '--enable-languages=c,c++,java,objc,obj-c++,fortran,ada,go',

                '--disable-bootstrap',

                '--enable-threads=posix',
                '--enable-multiarch',

                # TODO: I don't know why, but I want it enabled
                '--enable-multilib',

                '--enable-checking=release',
                '--enable-libada',
                '--enable-shared',
                #'--enable-targets='
                #'i686-pc-linux-gnu,'
                #'x86_64-pc-linux-gnu'
                ])

        for i in ['CFLAGS', 'LDFLAGS', 'CXXFLAGS']:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]

        return ret

    def builder_action_before_checks(self, log):
        print(
            "stop: checks! If You want them (it's good if You do)\n"
            "then continue build with command: aipsetup build continue checks+\n"
            "else continue build with command: aipsetup build continue distribute+\n"
            )
        ret = 1
        return ret

    def builder_action_checks(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=['check'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, log):

        if not os.path.exists(self.custom_data['cc_file']):
            os.symlink('gcc', self.custom_data['cc_file'])

        if (not os.path.exists(self.custom_data['libcpp_file'])
                and not os.path.islink(self.custom_data['libcpp_file'])):
            os.symlink('../bin/cpp', self.custom_data['libcpp_file'])

        return 0
