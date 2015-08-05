

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-gtkabi=3.0',
            #'--cpu=x86_64',
            '--audio-drv-list=pulse',
            '--enable-sdl'
            '--enable-kvm',
            '--enable-system',
            '--enable-user',
            '--enable-linux-user',
            #'--enable-bsd-user',
            #'--enable-guest-base',
            ]
