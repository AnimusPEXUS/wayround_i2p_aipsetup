

import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file
import wayround_org.utils.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--disable-alsa',
            '--enable-pulse',
            '--enable-gui',
            '--enable-radio',
            '--enable-radio-capture',
            '--enable-radio-v4l2',
            '--enable-tv',
            '--enable-tv-v4l2',
            '--enable-vcd',
            '--enable-freetype',
            #                    '--disable-mmx',
            #                    '--enable-ass',
            #                    '--enable-gif',
            #                    '--enable-png',
            #                    '--enable-mng',
            #                    '--enable-jpeg',
            '--enable-real',
            '--enable-xvid-lavc',
            '--enable-x264-lavc',
            '--mandir={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'share',
                    'man'
                    )
                ),
            '--confdir={}'.format(
                wayround_org.utils.path.join(
                    '/etc/mplayer'
                    )
                )
            ]
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--sysconfdir=',
                    '--localstatedir=',
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

        return ret
