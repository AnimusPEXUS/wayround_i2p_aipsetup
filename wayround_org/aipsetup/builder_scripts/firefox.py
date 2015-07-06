

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--with-system-libevent',
            '--with-system-libvpx',
            #'--with-system-nspr',
            #'--with-system-nss',
            '--with-system-icu',
            '--enable-gio',
            '--enable-system-cairo',
            '--enable-system-ffi',
            '--enable-system-pixman',
            '--enable-official-branding',
            '--with-system-bz2',
            '--with-system-jpeg',
            #'--with-system-png',
            '--with-system-zlib',
            '--disable-alsa',
            '--enable-pulseaudio',
            '--enable-application=browser',
            '--enable-default-toolkit=cairo-gtk3',
            '--enable-freetype2',
            '--enable-shared',
            #'--enable-shared-js',
            '--enable-xft',
            '--with-pthreads',
            '--enable-webrtc',
            '--enable-optimize',  # -O3 -fno-keep-inline-dllexport
            '--enable-gstreamer=1.0',
            '--with-system-nspr',
            '--with-system-nss',
            ]
