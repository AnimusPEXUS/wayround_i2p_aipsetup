
import copy
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


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        self.forced_target = True

        self.apply_host_spec_compilers_options = True

        pkgi = self.get_package_info()

        if (pkgi['constitution']['host'] !=
                pkgi['constitution']['target'] and
                pkgi['constitution']['host'] ==
                pkgi['constitution']['build']
                ):
            self.internal_host_redefinition =\
                pkgi['constitution']['target']

        '''
        ret = {
            'Builder_multi_i686': None,
            }

        if self.get_host_from_pkgi().startswith('x86_64'):
            if wayround_org.utils.file.which(
                    'i686-pc-linux-gnu-gcc',
                    '/multiarch/i686-pc-linux-gnu'
                    ) != None:

                print("""\
---------
configured for x86_64
but i686 GCC was found too
so going to build i686 multilib support
---------
""")

                ret['Builder_multi_i686'] = Builder_multi_i686(self.control)

        '''

        return

    def define_actions(self):

        ret = super().define_actions()

        ret['edit_package_info'] = self.builder_action_edit_package_info
        ret.move_to_end('edit_package_info', False)

        if self.get_is_crossbuilder():

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

        if not self.get_is_crossbuilder() and not self.get_is_crossbuild():
            '''
            # NOTE: this block is for multilib building
            if self.custom_data['Builder_multi_i686']:
                builder = self.custom_data['Builder_multi_i686']
                acts = builder.define_actions()

                for i in list(acts.keys()):
                    ret['{}_multi_i686'.format(i)] = acts[i]
            '''

            ret.move_to_end('distribute', True)

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.get_package_info()['pkg_info']['name']
        except:
            name = None

        pi = self.get_package_info()

        if self.get_is_crossbuilder():
            pi['pkg_info']['name'] = 'cb-glibc-{}'.format(
                self.get_target_from_pkgi()
                )
        else:
            pi['pkg_info']['name'] = 'glibc'

        bs = self.control
        bs.write_package_info(pi)

        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        return {}

    def builder_action_build_define_environment(self, called_as, log):
        return {}

    def builder_action_configure_define_opts(self, called_as, log):

        with_headers = wayround_org.utils.path.join(
            self.get_host_dir(),
            'multiarch',
            self.get_host_from_pkgi(),
            'include'
            )

        ret = super().builder_action_configure_define_opts(called_as, log)

        if self.get_is_crossbuilder():
            raise Exception("redo")
            prefix = wayround_org.utils.path.join(
                self.host_crossbuilders_dir,
                self.target
                )

            with_headers = wayround_org.utils.path.join(
                prefix,
                'include'
                )

            ret = [
                '--prefix={}'.format(prefix),
                '--mandir={}'.format(wayround_org.utils.path.join(prefix, 'share', 'man')),
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
            # reenabled those 3 items on 11 aug 2015: sims I need it
            '--enable-multi-arch',
            '--enable-multiarch',
            '--enable-multilib',

            # this is from configure --help. configure looking for
            # linux/version.h file
            #'--with-headers=/usr/src/linux/include',
            '--with-headers={}'.format(with_headers),
            '--enable-shared',

            # temp
            #'libc_cv_forced_unwind=yes'
            ]

        '''
        # NOTE: it's not working
        if self.host_strong.startswith('x86_64'):
            ret += ['slibdir=lib64']
        else:
            ret += ['slibdir=lib']
        '''

        if self.get_is_crossbuilder():
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

    # NOTE: this block is for multilib building
    def _t1(self, ret):
        ret = copy.copy(ret)
        if self.get_host_from_pkgi() == 'x86_64-pc-linux-gnu':
            if self.get_arch_from_pkgi().startswith('x86_64'):
                ret += [
                    'slibdir={}'.format(
                        wayround_org.utils.path.join(
                            self.get_host_dir(),
                            'lib64'
                            )
                        )
                    ]
            else:
                ret += [
                    'slibdir={}'.format(
                        wayround_org.utils.path.join(
                            self.get_host_dir(),
                            'lib'
                            )
                        )
                    ]
        else:
            raise Exception("To Be Done")
        return ret

    # NOTE: this block is for multilib building
    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret = self._t1(ret)
        return ret

    # NOTE: this block is for multilib building
    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret = self._t1(ret)
        return ret

    '''
    def builder_action_build_01(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['all-gcc'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
    '''

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
            environment={},
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
                wayround_org.utils.path.join('csu', 'subdir_lib')
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.bld_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_01_3(self, called_as, log):

        gres = glob.glob(wayround_org.utils.path.join(self.bld_dir, 'csu', '*crt*.o'))

        dest_lib_dir = wayround_org.utils.path.join(
            self.dst_host_crossbuilders_dir,
            self.target,
            self.calculate_main_multiarch_lib_dir_name()
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
            self.calculate_main_multiarch_lib_dir_name()
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
            environment={},
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
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret


class Builder_multi_i686(Builder):

    # TODO: force x86_64-pc-linux-gnu-gcc (not i686-pc-linux-gnu-gcc) build
    #       32bit part of glibc

    def define_custom_data(self):
        self.separate_build_dir = wayround_org.utils.path.join(self.src_dir, 'build_i686')
        ret = {
            'original_host': self.host_strong
            }
        #self.total_host_redefinition = 'i686-pc-linux-gnu'
        #self.total_build_redefinition = 'i686-pc-linux-gnu'
        #self.total_build_redefinition = 'x86_64-pc-linux-gnu'
        #self.total_target_redefinition = 'i686-pc-linux-gnu'

        self.internal_host_redefinition = 'i686-pc-linux-gnu'
        #self.internal_build_redefinition = 'x86_64-pc-linux-gnu'

        self.force_crossbuilder = False
        self.force_crossbuild = False

        return ret

    def define_actions(self):

        lst = [
            #('redefine_host', self.builder_action_redefine_host),
            ('make_dir', self.builder_action_make_dir),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            #('restore_host_definition',
            #    self.builder_action_restore_host_definition),
            ('distribute', self.builder_action_distribute),
            #('raname_arch_dir', self.builder_action_rename_arch_dir)
            ]

        ret = collections.OrderedDict(lst)

        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        return {}

    def builder_action_build_define_environment(self, called_as, log):
        return {}

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        '''
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--prefix=',
                    '--includedir=',
                    '--libdir=',
                    '--mandir=',
                    '--with-headers=',
                    ]:
                if ret[i].startswith(j):
                    ret[i] = ret[i].replace(
                        'i686-pc-linux-gnu',
                        self.custom_data['original_host']
                        )
        '''

        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    'CC=',
                    'GCC=',
                    'CXX='
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        '''
        ret += [
            'CC={}'.format(
                wayround_org.utils.file.which(
                    '{}-gcc'.format(self.custom_data['original_host'])
                    )
                ),
            'CXX={}'.format(
                wayround_org.utils.file.which(
                    '{}-g++'.format(self.custom_data['original_host'])
                    )
                ),
            'GCC={}'.format(
                wayround_org.utils.file.which(
                    '{}-gcc'.format(self.custom_data['original_host'])
                    )
                ),
            ]
        '''

        ret += [
            'CC={}-gcc -m32'.format(self.custom_data['original_host']),
            'CXX={}-g++ -m32'.format(self.custom_data['original_host']),
            #'GCC={}-gcc'.format(self.custom_data['original_host']),
            ]

        ret += [
            # 'CFLAGS=-m32'
            ]

        ret += [
            # '--disable-werror'
            ]

        return ret

    # NOTE: this block is for multilib building
    def _t2(self, ret):
        ret = copy.copy(ret)
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    'slibdir=',
                    ]:
                if ret[i].startswith(j):
                    ret[i] = ret[i].replace(
                        'i686-pc-linux-gnu',
                        self.custom_data['original_host']
                        )
        return ret

    # NOTE: this block is for multilib building
    def builder_action_build_define_args(self, called_as, log):
        ret = Builder.builder_action_build_define_args(self, called_as, log)
        # print('ret: {}'.format(ret))
        ret = self._t2(ret)
        return ret

    # NOTE: this block is for multilib building
    def builder_action_distribute_define_args(self, called_as, log):
        ret = Builder.builder_action_distribute_define_args(
            self,
            called_as,
            log
            )
        ret = self._t2(ret)
        return ret

    def builder_action_make_dir(self, called_as, log):
        os.makedirs(self.separate_build_dir, exist_ok=True)
        return 0

    # builder_action_configure = Builder.builder_action_configure

    # builder_action_build = Builder.builder_action_build

    def builder_action_restore_host_definition(self, called_as, log):
        self.total_host_redefinition = None
        self.total_build_redefinition = None
        self.total_target_redefinition = None
        log.info("Restored host definition to: {}".format(self.host_strong))
        return 0

    # builder_action_distribute = Builder.builder_action_distribute

    '''
    def builder_action_rename_arch_dir(self, called_as, log):
        ret = 0

        dir_name = self.dst_host_multiarch

        self.total_host_redefinition=None
        self.total_build_redefinition = None
        self.total_target_redefinition = None

        if os.path.isdir()
        return ret
    '''
