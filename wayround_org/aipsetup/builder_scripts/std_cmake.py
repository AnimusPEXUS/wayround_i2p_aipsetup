
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

    def builder_action_configure_define_compilers_options(self, d):
        if not 'CMAKE_C_COMPILER' in d:
            d['CMAKE_C_COMPILER'] = []
        d['CMAKE_C_COMPILER'].append('{}-gcc'.format(self.host_strong))

        if not 'CMAKE_CXX_COMPILER' in d:
            d['CMAKE_CXX_COMPILER'] = []
        d['CMAKE_CXX_COMPILER'].append('{}-g++'.format(self.host_strong))

        return

    def builder_action_configure_define_linking_interpreter_option(self, d):

        if not 'CMAKE_EXE_LINKER_FLAGS' in d:
            d['CMAKE_EXE_LINKER_FLAGS'] = []

        d['CMAKE_EXE_LINKER_FLAGS'].append(
            self.calculate_default_linker_program_gcc_parameter()
            )

        return

    def builder_action_configure_define_linking_lib_dir_options(self, d):

        if not 'LDFLAGS' in d:
            d['LDFLAGS'] = []

        d['LDFLAGS'].append('-L{}'.format(self.host_multiarch_lib_dir))

        return

    def builder_action_configure_define_options(self, called_as, log):

        minus_d_list = ['-D{}'.format(x)
                        for x in self.all_automatic_flags_as_list()]

        ret = [
            '-DCMAKE_INSTALL_PREFIX={}'.format(self.host_multiarch_dir),
            '-DCMAKE_SYSROOT={}'.format(self.host_multiarch_dir),
            '-DSYSCONFDIR=/etc',
            '-DLOCALSTATEDIR=/var',
            ] + cmake.calc_conf_hbt_options(self) + minus_d_list

        print(
            'builder_action_configure_define_options: {}'.format(
                ret
                )
            )

        return ret

    def builder_action_configure(self, called_as, log):

        defined_options = self.builder_action_configure_define_options(
            called_as,
            log)

        envs = self.builder_action_configure_define_environment(
            called_as,
            log
            )

        pkg_config_paths = self.calculate_pkgconfig_search_paths()

        envs.update(
            {'PKG_CONFIG_PATH': ':'.join(pkg_config_paths)}
            )

        ret = cmake.cmake_high(
            self.buildingsite,
            log=log,
            options=defined_options,
            arguments=[],
            environment=envs,
            environment_mode='copy',
            source_subdir=self.source_configure_reldir,
            build_in_separate_dir=self.separate_build_dir
            )
        return ret
