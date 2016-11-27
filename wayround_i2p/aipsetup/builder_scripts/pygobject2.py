

import os.path
import wayround_i2p.utils.path
import wayround_i2p.utils.file
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_environment(self, called_as, log):
        return {
            'PYTHON': wayround_i2p.utils.file.which(
                'python2',
                self.get_host_dir()
                )
            }
