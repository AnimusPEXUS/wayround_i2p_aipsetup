

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            ]
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--enable-shared'
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    # break
        return ret
