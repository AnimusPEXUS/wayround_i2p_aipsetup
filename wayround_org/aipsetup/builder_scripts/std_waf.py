
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, log):
        ret = super().builder_action_configure_define_options(log)
        ret.remove('--enable-shared')
        return ret
