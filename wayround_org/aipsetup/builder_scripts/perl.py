
import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True
        return

    def builder_action_configure_define_options(self, called_as, log):
        ret = [
            '--prefix={}'.format(self.host_multiarch_dir)
            ]
        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        return self.all_automatic_flags_as_dict()

    def builder_action_configure_define_script_name(self, called_as, log):
        return 'configure.gnu'
