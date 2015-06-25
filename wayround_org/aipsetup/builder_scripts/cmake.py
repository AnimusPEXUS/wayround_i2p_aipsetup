

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return [
            '--no-qt-gui',
            '--prefix=/usr',
            '--'
            ] + super().builder_action_configure_define_options(called_as, log)

    builder_action_configure = \
        wayround_org.aipsetup.builder_scripts.std.Builder.builder_action_configure

    # NOTE: 'LDFLAGS': '-ltinfow' may be required
