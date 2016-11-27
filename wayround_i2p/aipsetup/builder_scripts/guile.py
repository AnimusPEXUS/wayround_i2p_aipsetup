

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std

# WARNING: when building for x86_64 linux with multilib GCC, libdir
#          required to be configured to '.../lib64', of guile
#          configure tool will try use 64 bit libtool with 32 bit
#          glibc in '.../lib' dir

class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # NOTE: for autotools based packages libdir is better
            #       config in std.py
            #'--libdir={}'.format(
            #    wayround_i2p.utils.path.join(
            #        self.calculate_install_libdir(),
            #    )
            #),
            ]
        return ret
