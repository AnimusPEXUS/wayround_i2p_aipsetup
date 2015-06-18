

import wayround_org.aipsetup.builder_scripts.std

# TODO: provide selinux support


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_autogen(self, called_as, log):
        super().builder_action_autogen(log)
        return 0

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(log) + [
            '--enable-man',
            # '--without-selinux'
            ]
