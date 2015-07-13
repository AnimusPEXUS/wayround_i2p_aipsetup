
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

    def builder_action_configure_define_options(self, called_as, log):

        dl = wayround_org.aipsetup.build.find_dl(
            os.path.join(
                '/',
                'multiarch',
                self.host
                )
            )

        rpath = os.path.join(
            '/',
            'multiarch',
            self.host,
            'lib'
            )

        exe_linker_flags = '-Wl,--dynamic-linker=' + dl

        """
        exe_linker_flags = '-Wl,--dynamic-linker=' + \
            dl + \
            ' -Wl,-rpath={}'.format(rpath) + \
            ' -Wl,-rpath-link={}'.format(rpath)
        """

        ret = [
            #'-DCMAKE_INSTALL_PREFIX=/usr',
            '-DCMAKE_INSTALL_PREFIX={}'.format(self.host_multiarch_dir),
            '-DSYSCONFDIR=/etc',
            '-DLOCALSTATEDIR=/var',
            '-DCMAKE_EXE_LINKER_FLAGS=' + exe_linker_flags,
            '-DCMAKE_C_COMPILER={}-gcc'.format(self.host_strong),
            '-DCMAKE_CXX_COMPILER={}-g++'.format(self.host_strong),
            #    '--mandir=' + pkg_info['constitution']['paths']['man'],
            #    '--sysconfdir=' +
            #    pkg_info['constitution']['paths']['config'],
            #    '--localstatedir=' +
            #    pkg_info['constitution']['paths']['var'],
            #    '--enable-shared',
            #    '--host=' + pkg_info['constitution']['host'],
            #    '--build=' + pkg_info['constitution']['build'],
            #    '--target=' + pkg_info['constitution']['target']
            ]

        return ret + cmake.calc_conf_hbt_options(self)

    def builder_action_configure(self, called_as, log):

        defined_options = self.builder_action_configure_define_options(
            called_as,
            log)

        ret = cmake.cmake_high(
            self.buildingsite,
            log=log,
            options=defined_options,
            arguments=[],
            environment={},
            environment_mode='copy',
            source_subdir=self.source_configure_reldir,
            build_in_separate_dir=self.separate_build_dir
            )
        return ret
