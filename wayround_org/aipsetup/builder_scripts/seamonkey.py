

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--enable-application=suite',
            '--enable-calendar',
            '--enable-default-toolkit=cairo-gtk3',
            '--enable-freetype2',
            '--enable-safe-browsing',
            '--enable-shared',
            '--enable-shared-js',
            '--enable-storage',
            '--enable-xft',
            #'--enable-optimize=-O3 -fno-keep-inline-dllexport',
            '--enable-optimize',
            '--enable-webrtc',
            '--enable-gstreamer=1.0',
            '--with-pthreads',
            '--with-system-nspr',
            '--with-system-nss',
            ]
