

import os.path
import copy

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def builder_action_configure_define_opts(self, called_as, log):
        ret = [
            '--prefix={}'.format(self.get_host_arch_dir()),
            '--shared',
            ]

        if '64' in self.get_arch_from_pkgi():
            ret += ['--64']

        return ret

    def builder_action_configure_define_environment(self, called_as, log):

        ret = self.all_automatic_flags_as_dict()

        return ret

    def builder_action_build_define_args(self, called_as, log):
        return [
            'prefix={}'.format(self.get_dst_host_arch_dir())
            ]

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'prefix={}'.format(self.get_dst_host_arch_dir())
            ]
