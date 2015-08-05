
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)

        for i in [
                ]:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]

        return ret
