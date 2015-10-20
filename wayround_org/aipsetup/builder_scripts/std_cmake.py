
import logging
import os.path
import collections

import wayround_org.aipsetup.build
from wayround_org.aipsetup.buildtools import cmake
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        return None

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def calculate_compilers_options(self, d):
        if not 'CMAKE_C_COMPILER' in d:
            d['CMAKE_C_COMPILER'] = []
        d['CMAKE_C_COMPILER'].append('{}'.format(self.calculate_CC()))

        if not 'CMAKE_CXX_COMPILER' in d:
            d['CMAKE_CXX_COMPILER'] = []
        d['CMAKE_CXX_COMPILER'].append('{}'.format(self.calculate_CXX()))

        if not 'CMAKE_CXX_FLAGS' in d:
            d['CMAKE_CXX_FLAGS'] = []
        d['CMAKE_CXX_FLAGS'].append(
            '-m{}'.format(self.get_multilib_variant_int())
            )

        if not 'CMAKE_C_FLAGS' in d:
            d['CMAKE_C_FLAGS'] = []
        d['CMAKE_C_FLAGS'].append(
            '-m{}'.format(self.get_multilib_variant_int())
            )
        # d['CMAKE_C_FLAGS'].append(
        #    '-I{}'.format(
        #        wayround_org.utils.path.join(
        #            self.calculate_install_prefix(),
        #            'include'
        #            )
        #        )
        #    )

        return

    def builder_action_configure_define_opts(self, called_as, log):

        minus_d_list = [
            '-D{}'.format(x) for x in self.all_automatic_flags_as_list()
            ]

        ret = [
            #'-DCMAKE_INSTALL_PREFIX={}'.format(
            #    self.calculate_install_prefix()
            #    ),
            #
            #'-DCMAKE_SYSROOT={}'.format(self.calculate_install_prefix()),
            '-DSYSCONFDIR=/etc',
            '-DLOCALSTATEDIR=/var',
            #'-DCMAKE_SYSTEM_PREFIX_PATH={}'.format(
            #    self.calculate_install_prefix()
            #    ),
            #'-DCMAKE_SYSTEM_INCLUDE_PATH={}'.format(
            #    wayround_org.utils.path.join(
            #        self.calculate_install_prefix(),
            #        'include'
            #        )
            #    ),
            # '-DCMAKE_FIND_ROOT_PATH={}'.format(
            #    self.calculate_install_prefix()
            #    ),
            ]

        std_opts = super().builder_action_configure_define_opts(called_as, log)

        for i in [
                'PREFIX',
                'BINDIR',
                'SBINDIR',
                'LIBEXECDIR',
                'SYSCONFDIR',
                'SHAREDSTATEDIR',
                'LOCALSTATEDIR',
                'LIBDIR',
                'INCLUDEDIR',
                'OLDINCLUDEDIR',
                'DATAROOTDIR',
                'DATADIR',
                'MANDIR',
                'DOCDIR',
                ]:

            i_l_n = '--{}='.format(i.lower())

            for j in std_opts:
                if j.startswith(i_l_n):
                    ret.append(
                        '-DCMAKE_INSTALL_{}={}'.format(
                            i,
                            j.split('=', 1)[1]
                            )
                        )

        ret += cmake.calc_conf_hbt_options(self) + minus_d_list

        '''
        if self.get_arch_from_pkgi().startswith('x86_64'):
            ret += [
                '-DLIB_SUFFIX=64',
                '-DLIBDIR_SUFFIX=64',
                '-DX86_64=1',

                #'-DARCH_64=TRUE',
                #'-DFIND_LIBRARY_USE_LIB64_PATHS=1'
                ]
        '''

        if self.get_arch_from_pkgi().startswith('x86_64'):
            ret += [
                '-DLIB_SUFFIX=64',
                '-DLIBDIR_SUFFIX=64',
                ]

        return ret

    def builder_action_configure(self, called_as, log):

        self.check_deprecated_methods(called_as, log)

        envs = {}
        if hasattr(self, 'builder_action_configure_define_environment'):
            envs = self.builder_action_configure_define_environment(
                called_as,
                log
                )

        opts = []
        if hasattr(self, 'builder_action_configure_define_opts'):
            opts = self.builder_action_configure_define_opts(
                called_as,
                log
                )

        args = []
        if hasattr(self, 'builder_action_configure_define_args'):
            args = self.builder_action_configure_define_args(
                called_as,
                log
                )

        ret = cmake.cmake_high(
            self.buildingsite_path,
            log=log,
            options=opts,
            arguments=args,
            environment=envs,
            environment_mode='copy',
            source_subdir=self.source_configure_reldir,
            build_in_separate_dir=self.separate_build_dir
            )

        return ret

    #def builder_action_build_define_environment(self, called_as, log):
    #    return {}

    #def builder_action_distribute_define_environment(self, called_as, log):
    #    return {}
