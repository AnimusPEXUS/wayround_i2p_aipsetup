

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(log) + [
            '--enable-libsystemd-login=yes',
            '--enable-introspection=yes',
            '--with-mozjs=mozjs-17.0'
            ]
