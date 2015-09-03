

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            # NOTE: we don't have gstreamer 0.10 anymore
            #'--disable-video', '--disable-audio',
            '--enable-gtk-doc',
            '--enable-introspection',
            ]
