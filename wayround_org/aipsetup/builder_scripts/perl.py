
import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        ret = [
            '--prefix={}'.format(self.host_multiarch_dir)
            ]
        return ret

    def builder_action_configure_define_script_name(self, called_as, log):
        return 'configure.gnu'
