
import logging
import os.path

import wayround_i2p.aipsetup.build
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.utils.file

import wayround_i2p.aipsetup.builder_scripts.std_cmake


class Builder(wayround_i2p.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '-DPULSEAUDIO=ON',
            '-DPULSEAUDIO_SHARED=ON',
            '-DALSA=OFF',
            '-DALSA_SHARED=OFF',
            ]
