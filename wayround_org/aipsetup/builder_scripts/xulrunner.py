

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--enable-application=xulrunner',
            '--enable-default-toolkit=cairo-gtk3',
            '--enable-freetype2',
            '--enable-shared',
            '--disable-optimize',
            '--enable-shared-js',
            '--enable-xft',
            '--with-pthreads',
            #                    '--disable-webrtc',
            '--enable-gstreamer=1.0',
            '--enable-optimize',
            '--with-system-nspr',
            '--with-system-nss',
            ]
