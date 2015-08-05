
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '-DWITH_PLAYER=yes',
            ]
