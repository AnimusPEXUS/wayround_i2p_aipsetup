

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

# TODO: requires work on


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def builder_action_configure_define_environment(self, called_as, log):

        ret = self.all_automatic_flags_as_dict()

        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        # print('ret: {}'.format(ret))
        for i in [
                '--includedir=',
                '--mandir=',
                '--sysconfdir=',
                '--localstatedir=',
                'LDFLAGS=',
                '--host=',
                '--build=',
                '--target=',
                'CC=',
                'CXX=',
                'GCC='
                ]:
            for j in ret[:]:
                if j.startswith(i):
                    ret.remove(j)
        return ret
