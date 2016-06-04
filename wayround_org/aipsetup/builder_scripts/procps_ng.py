
import subprocess

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

curses_options = [
    'NCURSES_CFLAGS={}'.format(
        subprocess.Popen(
            ['pkg-config', '--cflags', 'ncurses'],
            stdout=subprocess.PIPE
            ).communicate()[0].decode('utf-8').strip()
        ),
    'NCURSES_LIBS={}'.format(
        subprocess.Popen(
            ['pkg-config', '--libs', 'ncurses'],
            stdout=subprocess.PIPE
            ).communicate()[0].decode('utf-8').strip()
        ),
    'NCURSESW_CFLAGS={}'.format(
        subprocess.Popen(
            ['pkg-config', '--cflags', 'ncursesw'],
            stdout=subprocess.PIPE
            ).communicate()[0].decode('utf-8').strip()
        ),
    'NCURSESW_LIBS={}'.format(
        subprocess.Popen(
            ['pkg-config', '--libs', 'ncursesw'],
            stdout=subprocess.PIPE
            ).communicate()[0].decode('utf-8').strip()
        ),
    'CFLAGS={}'.format(
        subprocess.Popen(
            ['pkg-config', '--cflags', 'ncursesw'],
            stdout=subprocess.PIPE
            ).communicate()[0].decode('utf-8').strip()
        ),
    ]

#curses_options = []


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-systemd',
            ]

        # TODO: this should not be used
        ret += curses_options
        return ret

    def builder_action_build_define_opts(self, called_as, log):
        ret = super().builder_action_build_define_opts(called_as, log)

        # TODO: this should not be used
        #       ret += curses_options
        return ret
