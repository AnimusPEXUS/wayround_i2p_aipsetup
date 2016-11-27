

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            # NOTE: we don't have gstreamer 0.10 anymore
            #'--disable-video', '--disable-audio',
            '--enable-gtk-doc',
            '--enable-introspection',
            ]
