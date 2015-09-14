

import wayround_org.aipsetup.builder_scripts.std

import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def disabled_builder_action_configure_define_environment(
            self,
            called_as,
            log
            ):
        ret = self.all_automatic_flags_as_dict()
        return ret

    def builder_action_build_define_opts(self, called_as, log):
        ret = super().builder_action_build_define_opts(called_as, log)
        ret += self.all_automatic_flags_as_list()
        ret += [
            'PREFIX={}'.format(self.calculate_install_prefix()),
            'SBINDIR={}/sbin'.format(self.calculate_install_prefix()),
            'KERNEL_INCLUDE={}/include'.format(self.calculate_install_prefix()),
            'DBM_INCLUDE:={}/include'.format(self.calculate_install_prefix()),
            ]
        return ret

    def builder_action_distribute_define_opts(self, called_as, log):
        ret = super().builder_action_build_define_opts(called_as, log)
        ret += self.all_automatic_flags_as_list()
        ret += [
            'PREFIX={}'.format(self.calculate_install_prefix()),
            'SBINDIR={}/sbin'.format(self.calculate_install_prefix()),
            'KERNEL_INCLUDE={}/include'.format(self.calculate_install_prefix()),
            'DBM_INCLUDE:={}/include'.format(self.calculate_install_prefix()),
            ]
        return ret
