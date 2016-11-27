

import os.path

import wayround_i2p.utils.path
import wayround_i2p.utils.file

import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            #'--with-autoopts-config={}'.format(
            #    wayround_i2p.utils.file.which(
            #        'autoopts-config',
            #        self.get_host_dir()
            #        )
            #    ),
            #'GUILE={}'.format(
            #    wayround_i2p.utils.file.which(
            #        'guile',
            #        self.get_host_dir()
            #        )
            #    ),
            #'GUILE_CONFIG={}'.format(
            #    wayround_i2p.utils.file.which(
            #        'guile-config',
            #        self.get_host_dir()
            #        )
            #    ),
            #'GUILE_SNARF={}'.format(
            #    wayround_i2p.utils.file.which(
            #        'guile-snarf',
            #        self.get_host_dir()
            #        )
            #    ),
            ]

        return ret
