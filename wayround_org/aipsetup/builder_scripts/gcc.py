
import logging
import os.path
import subprocess
import collections

import wayround_org.utils.file
import wayround_org.utils.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.binutils


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        ret = dict()
        ret['cc_file'] = os.path.join(self.dst_dir, 'usr', 'bin', 'cc')
        ret['libcpp_file'] = os.path.join(self.dst_dir, 'usr', 'lib', 'cpp')
        return ret

    def define_actions(self):
        ret = collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            #('before_checks', self.builder_action_before_checks),
            #('checks', self.builder_action_checks),
            ('distribute', self.builder_action_distribute),
            ('after_distribute', self.builder_action_after_distribute)
            ])
        return ret

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
            # experimental options
            # '--enable-targets=all',
            '--enable-tls',
            '--enable-nls',

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
            '--enable-__cxa_atexit',

            # disabled for experiment
            #'--with-arch-32=i486',
            #'--with-tune=generic',

            #'--enable-languages=c,c++,java,objc,obj-c++,fortran,ada',
            '--enable-languages=c,c++,java,objc,obj-c++,fortran',
            #'--enable-languages=ada',
            '--enable-bootstrap',
            '--enable-threads=posix',
            '--enable-multiarch',
            '--enable-multilib',
            '--enable-checking=release',
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
            # '--with-build-time-tools=
            # /home/agu/_sda3/_UNICORN/b/gnat/
            # gnat-gpl-2014-x86-linux-bin',
            '--enable-shared'
            ]

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
            options=['-k'],
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
