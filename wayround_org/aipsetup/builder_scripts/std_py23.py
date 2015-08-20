
import logging
import os.path
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class BuilderForPy2(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_environment(self, called_as, log):
        return {'PYTHON': 'python2'}

    def define_actions(self):
        return collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            #('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('autogen', self.builder_action_autogen),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])


class BuilderForPy3(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_environment(self, called_as, log):
        return {'PYTHON': 'python3'}

    def define_actions(self):
        return collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            #('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('autogen', self.builder_action_autogen),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {
            'py2_builder': BuilderForPy2(self.control),
            'py3_builder': BuilderForPy3(self.control),
            }

    def define_actions(self):

        lst = [
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup)
            ]

        actions = self.custom_data['py2_builder'].get_defined_actions()
        for i in actions.keys():
            lst.append(('for_py2_{}'.format(i), actions[i]))

        actions = self.custom_data['py3_builder'].get_defined_actions()
        for i in actions.keys():
            lst.append(('for_py3_{}'.format(i), actions[i]))

        return collections.OrderedDict(lst)
