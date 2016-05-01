

import wayround_org.aipsetup.builder_scripts.std

# TODO: provide selinux support


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_autogen(self, called_as, log):
        super().builder_action_autogen(called_as, log)
        return 0

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            # '--enable-man',
            # '--without-selinux'
            ]
