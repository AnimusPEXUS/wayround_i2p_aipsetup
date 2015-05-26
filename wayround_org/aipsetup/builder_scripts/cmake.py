

import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
            '--no-qt-gui'
            ]

    # NOTE: 'LDFLAGS': '-ltinfow' may be required
