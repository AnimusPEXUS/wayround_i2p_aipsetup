

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(called_as, log)

        ret += [
            ]

        for i in [
                '--includedir=',
                '--mandir=',
                '--sysconfdir=',
                '--localstatedir=',
                '--enable-shared',
                '--host=',
                '--build=',
                '--tarbet=',
                'LDFLAGS='
                ]:
            for j in range(len(ret)-1,-1,-1):
                if ret[j].startswith(i):
                    del ret[j]

        return ret
