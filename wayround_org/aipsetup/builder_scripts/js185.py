

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.source_configure_reldir = 'js/src'
        return None

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-x',
            '--with-pthreads',
            '--with-system-nspr',
            #                    '--enable-readline',
            '--enable-threadsafe',
            ]
