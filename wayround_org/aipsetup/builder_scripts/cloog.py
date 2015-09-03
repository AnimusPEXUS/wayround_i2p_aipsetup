

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # NOTE: --with-gmp-prefix= - required. else cloog
            #      configurer will use 32bit gmp found in lib dir
            #      to build for x86_64
            #'--with-gmp=system',
            #'--with-gmp-prefix={}'.format(self.get_host_dir()),

            # NOTE: with isl same as with gmp
            #'--with-isl=system',
            #'--with-isl-prefix={}'.format(self.get_host_dir()),
            ]
        return ret

    # def builder_action_build_define_cpu_count(self, called_as, log):
    #    return 1
