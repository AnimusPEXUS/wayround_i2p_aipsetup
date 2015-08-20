
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = []

        if not self.get_is_crossbuild() and not self.get_is_crossbuilder():
            pass
        else:
            ret += [
                '--without-guile'
                ]

        return super().builder_action_configure_define_opts(called_as, log) + ret
