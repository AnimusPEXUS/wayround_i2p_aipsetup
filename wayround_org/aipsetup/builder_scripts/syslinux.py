

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True

        return

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        del ret['autogen']
        del ret['patch']
        del ret['build']
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = [
            'bios', 'efi32', 'efi64',
            'installer',
            'install',
            'INSTALLROOT={}'.format(self.get_dst_dir()),
            ] + self.all_automatic_flags_as_list()
        return ret
