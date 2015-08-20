
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
        d['CMAKE_C_COMPILER'].append('{}-gcc'.format(self.calculate_CC))

        if not 'CMAKE_CXX_COMPILER' in d:
            d['CMAKE_CXX_COMPILER'] = []
        d['CMAKE_CXX_COMPILER'].append('{}-g++'.format(self.calculate_CXX))

        return

    def builder_action_configure_define_opts(self, called_as, log):

        minus_d_list = ['-D{}'.format(x)
                        for x in self.all_automatic_flags_as_list()]

        ret = [
            '-DCMAKE_INSTALL_PREFIX={}'.format(self.get_host_arch_dir()),
            '-DCMAKE_SYSROOT={}'.format(self.get_host_arch_dir()),
            '-DSYSCONFDIR=/etc',
            '-DLOCALSTATEDIR=/var',
            ] + cmake.calc_conf_hbt_options(self) + minus_d_list

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
