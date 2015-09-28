

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.builder_scripts.std_qmake


class Builder(wayround_org.aipsetup.builder_scripts.std_qmake.Builder):

    def define_actions(self):
        ret = super().define_actions()
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        return ret
