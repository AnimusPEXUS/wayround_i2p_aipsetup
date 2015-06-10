

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_options(self, log):
        return [
            '--no-qt-gui',
            '--prefix=/usr'
            ]

    builder_action_configure = wayround_org.aipsetup.builder_scripts.std.Builder.builder_action_configure

    # NOTE: 'LDFLAGS': '-ltinfow' may be required
