

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

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
