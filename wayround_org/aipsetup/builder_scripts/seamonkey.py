

import wayround_org.aipsetup.builder_scripts.xulrunner


class Builder(wayround_org.aipsetup.builder_scripts.xulrunner.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-application=suite',
            ]
        return ret
