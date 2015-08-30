
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        ret.remove('--enable-shared')

        for i in range(len(ret) - 1, -1, -1):
            for j in ['CC=', 'CXX=', 'GCC=']:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        return ret
