

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        return {'error': self.builder_action_configure}

    def builder_action_configure(self, called_as, log):
        raise Exception(
            "implementation required. but as far as I can tell"
            " MessaGLUT is deprecated"
            )
