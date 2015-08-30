

import os.path
import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_environment(self, called_as, log):
        return {
            'PYTHON': wayround_org.utils.file.which(
                'python2',
                self.get_host_dir()
                )
            }
