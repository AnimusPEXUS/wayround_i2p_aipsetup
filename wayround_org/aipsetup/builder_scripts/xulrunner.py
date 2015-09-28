

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-application=xulrunner',

            '--disable-alsa',
            '--enable-pulseaudio',

            # '--disable-optimize',
            #'--with-system-png',
            #'--enable-official-branding',
            #'--enable-optimize=-O3 -fno-keep-inline-dllexport',

            '--enable-calendar',
            '--enable-default-toolkit=cairo-gtk3',
            '--enable-freetype2',
            '--enable-gio',
            '--enable-gstreamer=1.0',
            '--enable-optimize',
            '--enable-safe-browsing',
            '--enable-shared',
            '--enable-shared-js',
            '--enable-storage',
            '--enable-system-cairo',
            '--enable-system-ffi',
            '--enable-system-pixman',
            '--enable-webrtc',
            '--enable-xft',
            '--with-pthreads',
            '--with-system-bz2',
            '--with-system-icu',
            '--with-system-jpeg',
            '--with-system-libevent',
            '--with-system-libvpx',
            '--with-system-nspr',
            '--with-system-nss',
            '--with-system-zlib',
            ]

        return ret
