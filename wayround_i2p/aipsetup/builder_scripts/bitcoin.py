

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

   # def calculate_pkgconfig_search_paths(self):
   #
   #     return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-incompatible-bdb',
            '--with-gui=qt5',
            #'--disable-tests',
            'CFLAGS=-g -O2 -fPIC',
            'CXXFLAGS=-g -O2 -fPIC'
            ]
        return ret
