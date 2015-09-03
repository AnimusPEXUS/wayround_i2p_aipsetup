

import wayround_org.aipsetup.builder_scripts.python


class Builder(wayround_org.aipsetup.builder_scripts.python.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-pydebug'
            ]
