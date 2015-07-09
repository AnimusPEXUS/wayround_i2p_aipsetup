

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.source_configure_reldir = 'nspr'
        return None

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(called_as, log)

        ret += [
            '--with-mozilla',
            '--with-pthreads',
            '--enable-ipv6',
            # TODO: depends!!!!!!!!!!!
            ]

        if self.host == 'x86_64-pc-linux-gnu':
            ret += ['--enable-64bit']

        return ret
