
import logging
import os.path
import subprocess
import collections
import inspect

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.gcc
import wayround_org.aipsetup.builder_scripts.binutils


class BinutilsBuilder(wayround_org.aipsetup.builder_scripts.binutils.Builder):

    def define_custom_data(self):
        ret = super().define_custom_data()
        ret['crossbuilder_mode'] = True
        return ret

    def builder_action_extract(self):
        ret = autotools.extract_high(
            self.buildingsite,
            'binutils',
            unwrap_dir=True,
            rename_dir=False
            )
        return ret


class GCCBuilder(wayround_org.aipsetup.builder_scripts.gcc.Builder):

    def define_custom_data(self):
        ret = super().define_custom_data()
        ret['crossbuilder_mode'] = True
        return ret

    def builder_action_extract(self):
        ret = autotools.extract_high(
            self.buildingsite,
            'gcc',
            unwrap_dir=True,
            rename_dir=False
            )
        return ret


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        return collections.OrderedDict([
            ('build_binutils', self.builder_action_build_binutils),
            ('build_gcc', self.builder_action_build_gcc)
            ])

    def define_custom_data(self):
        return {}

    def builder_action_build_binutils(self):

        binutils_builder = BinutilsBuilder(self.buildingsite)
        ret = binutils_builder.run_action()

        return ret

    def builder_action_build_gcc(self):

        gcc_builder = GCCBuilder(self.buildingsite)
        ret = gcc_builder.run_action()

        return ret
