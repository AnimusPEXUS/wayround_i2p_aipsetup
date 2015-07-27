

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        return {'error': self.builder_action_configure}

    def builder_action_configure(self, called_as, log):
        raise Exception(
            "implementation required. but as far as I can tell"
            " MessaGLUT is deprecated"
            )
