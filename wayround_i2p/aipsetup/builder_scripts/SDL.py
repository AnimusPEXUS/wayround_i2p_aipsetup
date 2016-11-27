
import logging
import os.path

import wayround_i2p.aipsetup.build
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.utils.file

import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--enable-audio',
            '--enable-video',
            '--enable-events',
            '--enable-libc',
            '--enable-loads',
            '--enable-file',
            '--disable-alsa',
            '--enable-pulseaudio',
            '--enable-pulseaudio-shared'
            ]
