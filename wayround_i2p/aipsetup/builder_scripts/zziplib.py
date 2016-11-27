

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_run_script_not_bash(
            self, called_as, log
            ):
        return True

    def builder_action_configure_define_relative_call(self, called_as, log):
        return True
