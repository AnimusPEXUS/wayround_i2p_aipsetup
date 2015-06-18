
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        ret = [
            ]

        if not self.is_crossbuild and not self.is_crossbuilder:
            ret += [
                ]
        else:
            ret += [
                '--without-python',
                '--without-ncurses',
                '--without-systemd'
                ]

        return super().builder_action_configure_define_options(log) + ret
