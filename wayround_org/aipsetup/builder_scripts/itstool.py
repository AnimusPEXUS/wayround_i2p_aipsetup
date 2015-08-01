

import os.path
import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(called_as, log)
        ret += [
            'PYTHON={}'.format(
                wayround_org.utils.file.which(
                    'python3',
                    self.host_multiarch_dir
                    )
                ),
            ]

        return ret
