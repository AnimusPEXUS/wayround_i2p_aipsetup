

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [

            #'--with-nspr-includes={}'.format(self.get_host_dir()),

            #'--with-nspr-libs={}'.format(self.get_host_dir()),

            #'--with-nss-includes={}'.format(self.get_host_dir()),

            #'--with-nss-libs={}'.format(self.get_host_dir()),

            '--enable-vala-bindings',
            '--disable-uoa',
            ]
