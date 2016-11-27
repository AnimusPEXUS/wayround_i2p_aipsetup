

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--enable-foomatic-rip-hplip-install',
            '--enable-hpijs-install',
            '--enable-hpcups-install',
            '--enable-gui-build',
            '--enable-foomatic-ppd-install',
            '--enable-foomatic-drv-install',
            '--enable-cups-drv-install',
            '--enable-cups-ppd-install',
            ]
