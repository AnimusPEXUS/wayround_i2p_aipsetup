

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--enable-shared',
            '--enable-gpl',
            '--enable-libtheora',
            '--enable-libvorbis',
            '--enable-x11grab',
            '--enable-libmp3lame',
            '--enable-libx264',
            '--enable-libxvid',
            '--enable-runtime-cpudetect',
            '--enable-doc',
            ]
