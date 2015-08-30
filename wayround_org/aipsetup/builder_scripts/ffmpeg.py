

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
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

        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--includedir=',
                    '--sysconfdir=',
                    '--localstatedir=',
                    '--sbindir=',
                    '--bindir=',
                    '--libexecdir=',
                    '--datarootdir=',
                    '--exec-prefix=',
                    #'',
                    #'',
                    '--host=',
                    '--build=',
                    '--target=',
                    'CC=',
                    'GCC=',
                    'CXX=',
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        return ret
