

import wayround_org.utils.file

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = False
        return

    def builder_action_configure_define_opts(self, called_as, log):
        ret = [
            '-Dprefix={}'.format(self.calculate_install_prefix()),
            '-Dcc={}-gcc'.format(self.get_host_from_pkgi()),
            '-Duseshrplib',
            '-d'
            ]
        #if self.get_arch_from_pkgi().startswith('x86_64'):
        #    ret +=
        #ret = [
        #    '--prefix={}'.format(self.calculate_install_prefix()),
        #    'CC={}'.format(self.calculate_CC_string()),
        #    ]
        return ret

    '''
    def builder_action_configure_define_environment(self, called_as, log):
        return self.all_automatic_flags_as_dict()
    '''

    def builder_action_configure_define_script_name(self, called_as, log):
        # return 'configure.gnu'
        return 'Configure'
