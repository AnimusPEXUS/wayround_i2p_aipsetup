
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

    def builder_action_configure_define_options(self, log):
        return [
            '-DCMAKE_INSTALL_PREFIX=' +
            self.package_info['constitution']['paths']['usr'],
            #    '--mandir=' + pkg_info['constitution']['paths']['man'],
            #    '--sysconfdir=' +
            #    pkg_info['constitution']['paths']['config'],
            #    '--localstatedir=' +
            #    pkg_info['constitution']['paths']['var'],
            #    '--enable-shared',
            #    '--host=' + pkg_info['constitution']['host'],
            #    '--build=' + pkg_info['constitution']['build'],
            #    '--target=' + pkg_info['constitution']['target']
            ] + cmake.calc_conf_hbt_options(self)

    def builder_action_configure(self, log):

        defined_options = self.builder_action_configure_define_options(log)

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
