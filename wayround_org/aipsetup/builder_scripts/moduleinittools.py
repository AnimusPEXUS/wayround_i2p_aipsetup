

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_run_script_not_bash(
            self,
            called_as,
            log
            ):
        return True

    def builder_action_configure_define_relative_call(self, called_as, log):
        return True
