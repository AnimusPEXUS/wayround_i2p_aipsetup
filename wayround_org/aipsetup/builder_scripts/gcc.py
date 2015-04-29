
import logging
import os.path
import subprocess
import collections

import wayround_org.utils.file

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.binutils


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = dict()
        ret['cc_file'] = os.path.join(self.dst_dir, 'usr', 'bin', 'cc')
        ret['libcpp_file'] = os.path.join(self.dst_dir, 'usr', 'lib', 'cpp')
        return ret

    def define_actions(self):
        ret = collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            #('before_checks', self.builder_action_before_checks),
            #('checks', self.builder_action_checks),
            ('distribute', self.builder_action_distribute),
            ('after_distribute', self.builder_action_after_distribute)
            ])
        return ret

    builder_action_dst_cleanup =\
        wayround_org.aipsetup.builder_scripts.binutils.Builder\
        .builder_action_dst_cleanup

    def builder_action_configure(self):

        target = self.package_info['constitution']['target']
        host = self.package_info['constitution']['host']
        build = self.package_info['constitution']['build']

        prefix = self.package_info['constitution']['paths']['usr']
        mandir = self.package_info['constitution']['paths']['man']
        sysconfdir = self.package_info['constitution']['paths']['config']
        localstatedir = self.package_info['constitution']['paths']['var']

        if ('crossbuilder_mode' in self.custom_data
                and self.custom_data['crossbuilder_mode'] == True):
            pass
            #prefix = os.path.join(
            #    '/', 'usr', 'lib', 'unicorn_crossbuilders', target
            #    )
            # mandir = os.path.join(prefix, 'man')
            # sysconfdir = os.path.join(prefix, 'etc')
            # localstatedir = os.path.join(prefix, 'var')

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
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

                '--enable-languages=c,c++,java,objc,obj-c++,ada,fortran',
                '--enable-bootstrap',
                '--enable-threads=posix',
                '--enable-multiarch',
                '--enable-multilib',
                '--enable-checking=release',
                '--with-gmp=/usr',
                '--with-mpfr=/usr',
                # '--with-build-time-tools=
                # /home/agu/_sda3/_UNICORN/b/gnat/
                # gnat-gpl-2014-x86-linux-bin',
                '--enable-shared',

                '--prefix=' + prefix,
                '--mandir=' + mandir,
                '--sysconfdir=' + sysconfdir,
                '--localstatedir=' + localstatedir,

                '--host=' + host,
                '--build=' + build,
                '--target=' + target
                ],
            arguments=[],
            environment={
                # 'CC': '/home/agu/_sda3/_UNICORN/b/gnat/
                #  gnat-gpl-2014-x86-linux-bin/bin/gcc',
                # 'CXX': '/home/agu/_sda3/_UNICORN/b/
                # gnat/gnat-gpl-2014-x86-linux-bin/bin/g++',
                },
            environment_mode='copy',
            source_configure_reldir=self.source_configure_reldir,
            use_separate_buildding_dir=self.separate_build_dir,
            script_name='configure',
            run_script_not_bash=False,
            relative_call=False
            )
        return ret

    def builder_action_before_checks(self):
        print(
            "stop: checks! If You want them (it's good if You do)\n"
            "then continue build with command: aipsetup build continue checks+\n"
            "else continue build with command: aipsetup build continue distribute+\n"
            )
        ret = 1
        return ret

    def builder_action_checks(self):
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

    def builder_action_after_distribute(self):

        if not os.path.exists(self.custom_data['cc_file']):
            os.symlink('gcc', self.custom_data['cc_file'])

        if (not os.path.exists(self.custom_data['libcpp_file'])
                and not os.path.islink(self.custom_data['libcpp_file'])):
            os.symlink('../bin/cpp', self.custom_data['libcpp_file'])

        return 0
