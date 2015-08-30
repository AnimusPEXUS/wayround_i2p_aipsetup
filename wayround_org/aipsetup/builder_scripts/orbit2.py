

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # NOTE: warnings will be not looking on this
            #       option. Werror need to be remover manually

            # '--enable-compile-warnings=no',
            # 'CFLAGS=-g -O2'
            ]
        return ret
