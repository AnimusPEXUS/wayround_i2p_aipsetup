

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

# TODO: requires work on

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        ret = super().builder_action_configure_define_options(called_as, log)
        # print('ret: {}'.format(ret))
        for i in [
                '--includedir=',
                '--mandir=',
                '--sysconfdir=',
                '--localstatedir=',
                'LDFLAGS=',
                '--host=',
                '--build=',
                '--target='
                ]:
            for j in ret[:]:
                if j.startswith(i):
                    ret.remove(j)
        return ret
