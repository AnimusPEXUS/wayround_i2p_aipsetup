
import logging
import os.path
import time
import collections
import glob
import shutil
import subprocess

import wayround_org.utils.file
import wayround_org.utils.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


# For history
# RUN[$j]='echo "CFLAGS += -march=i486 -mtune=native" > configparms

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        self.forced_target = True
        self.apply_host_spec_linking_options = True
        self.apply_host_spec_compilers_options = False

        if (self.package_info['constitution']['host'] !=
                self.package_info['constitution']['target'] and
                self.package_info['constitution']['host'] ==
                self.package_info['constitution']['build']
            ):
            self.internal_host_redefinition =\
                self.package_info['constitution']['target']

        return None

    def define_actions(self):

        ret = super().define_actions()

        ret['edit_package_info'] = self.builder_action_edit_package_info
        ret.move_to_end('edit_package_info', False)

        if self.is_crossbuilder:

            logging.info(
                "Crosscompiler building detected. splitting process on two parts"
                )

            # ret['build_01'] = self.builder_action_build_01
            ret['distribute_01'] = self.builder_action_distribute_01
            ret['distribute_01_2'] = self.builder_action_distribute_01_2
            ret['distribute_01_3'] = self.builder_action_distribute_01_3
            ret['distribute_01_4'] = self.builder_action_distribute_01_4
            ret['distribute_01_5'] = self.builder_action_distribute_01_5

            ret['intermediate_instruction'] = \
                self.builder_action_intermediate_instruction

            ret['build_02'] = self.builder_action_build_02
            ret['distribute_02'] = self.builder_action_distribute_02

            del ret['build']
            del ret['distribute']
        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        pi = self.package_info

        if self.is_crossbuilder:
            pi['pkg_info']['name'] = 'cb-glibc-{}'.format(self.target)
        else:
            pi['pkg_info']['name'] = 'glibc'

        bs = self.control
        bs.write_package_info(pi)

        return ret

    def builder_action_configure_define_options(self, called_as, log):

        with_headers = os.path.join(self.host_multiarch_dir, 'include')

        ret = super().builder_action_configure_define_options(called_as, log)

        if self.is_crossbuilder:
            prefix = os.path.join(
                self.host_crossbuilders_dir,
                self.target
                )

            with_headers = os.path.join(
                prefix,
                'include'
                )

            ret = [
                '--prefix={}'.format(prefix),
                '--mandir={}'.format(os.path.join(prefix, 'share', 'man')),
                '--sysconfdir=/etc',
                '--localstatedir=/var',
                '--enable-shared'
                ] + autotools.calc_conf_hbt_options(self)

        ret += [
            '--enable-obsolete-rpc',
            '--enable-kernel=3.19',
            '--enable-tls',
            '--with-elf',

            # disabled those 3 items on 2 jul 2015
            '--disable-multi-arch',
            '--disable-multiarch',
            '--disable-multilib',

            # this is from configure --help. configure looking for
            # linux/version.h file
            #'--with-headers=/usr/src/linux/include',
            '--with-headers={}'.format(with_headers),
            '--enable-shared'
            ]

        if self.is_crossbuilder:
            ret += [
                # this can be commented whan gcc fulli built and installed
                #'libc_cv_forced_unwind=yes',

                # this parameter is required to build `build_02+' stage.
                # comment and completle rebuild this glibc after rebuilding
                # gcc without --without-headers and with
                # --with-sysroot parameter.
                #
                # 'libc_cv_ssp=no'
                #
                # else You will see errors like this:
                #     gethnamaddr.c:185: undefined reference to
                #     `__stack_chk_guard'
                ]

        return ret

    def builder_action_distribute(self, called_as, log):

        ret = super().builder_action_distribute(called_as, log)

        if ret == 0:

            try:
                os.rename(
                    os.path.join(self.dst_dir, 'etc', 'ld.so.cache'),
                    os.path.join(self.dst_dir, 'etc', 'ld.so.cache.distr')
                    )
            except:
                log.exception("Can't rename ld.so.cache file")

        return ret

    """
    def builder_action_build_01(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['all-gcc'],
            environment=self.builder_action_make_define_environment(called_as, log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
    """

    def builder_action_distribute_01(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install-bootstrap-headers=yes',
                'install-headers',
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

    def builder_action_distribute_01_2(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                os.path.join('csu', 'subdir_lib')
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_01_3(self, called_as, log):

        gres = glob.glob(os.path.join(self.bld_dir, 'csu', '*crt*.o'))

        dest_lib_dir = wayround_org.utils.path.join(
            self.dst_host_crossbuilders_dir,
            self.target,
            'lib'
            )

        os.makedirs(dest_lib_dir, exist_ok=True)

        for i in gres:
            from_ = i
            to = dest_lib_dir
            log.info("Copying `{}' to `{}'".format(from_, to))
            shutil.copy2(from_, to)

        return 0

    def builder_action_distribute_01_4(self, called_as, log):

        cwd = wayround_org.utils.path.join(
            self.dst_host_crossbuilders_dir,
            self.target,
            'lib'
            )

        cmd = [
            self.target + '-gcc',
            '-nostdlib',
            '-nostartfiles',
            '-shared',
            '-x',
            'c',
            '/dev/null',
            '-o',
            'libc.so'
            ]

        log.info("directory: {}".format(cwd))
        log.info("cmd: {}".format(' '.join(cmd)))
        p = subprocess.Popen(cmd, cwd=cwd)
        ret = p.wait()
        return ret

    def builder_action_distribute_01_5(self, called_as, log):

        cwd = wayround_org.utils.path.join(
            self.dst_host_crossbuilders_dir,
            self.target,
            'include',
            'gnu'
            )

        cwdf = wayround_org.utils.path.join(cwd, 'stubs.h')

        os.makedirs(cwd, exist_ok=True)

        if not os.path.isfile(cwdf):
            with open(cwdf, 'w') as f:
                pass

        return 0

    def builder_action_intermediate_instruction(self, called_as, log):
        log.info("""
---------------
pack and install this glibc build.
then continue with gcc build_02+
---------------
""")
        return 1

    def builder_action_build_02(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[],
            environment=self.builder_action_make_define_environment(
                called_as,
                log
                ),
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
                'install',
                'DESTDIR={}'.format(self.dst_dir)
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log
                ),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
