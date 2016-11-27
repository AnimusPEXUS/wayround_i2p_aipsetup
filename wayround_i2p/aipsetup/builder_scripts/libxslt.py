

import os.path
import wayround_i2p.utils.path
import wayround_i2p.utils.file
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            #'--with-python-install-dir={}'.format(
            #    wayround_i2p.utils.path.join(
            #        self.calculate_install_prefix(),
            #        'lib'
            #        ),
            #    )
            '--with-python={}'.format(
                wayround_i2p.utils.path.join(
                    self.calculate_install_prefix(),
                    ),
                ),
            'PYTHON={}'.format(
                wayround_i2p.utils.file.which(
                    'python',
                    self.calculate_install_prefix()
                    )
                )
            ]
        return ret
