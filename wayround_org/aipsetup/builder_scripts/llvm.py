

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        return None

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--bindir=' +
            wayround_org.utils.path.join(
                self.calculate_install_prefix(),
                'bin'
                ),

            '--sbindir=' +
            wayround_org.utils.path.join(
                self.calculate_install_prefix(),
                'sbin'
                ),

            ]

        return ret
