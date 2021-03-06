

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-virglrenderer',

            '--disable-gtk',
            #'--with-gtkabi=3.0',

            #'--cpu=x86_64',
            '--audio-drv-list=pa',

            '--enable-sdl',
            '--with-sdlabi=2.0',

            '--enable-kvm',
            '--enable-system',
            '--enable-user',
            '--enable-linux-user',
            #'--enable-bsd-user',
            #'--enable-guest-base',
            ]

        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--enable-shared',
                    '--host=',
                    '--build=',
                    '--target=',
                    'CC=',
                    'CXX=',
                    'GCC=',
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        return ret
