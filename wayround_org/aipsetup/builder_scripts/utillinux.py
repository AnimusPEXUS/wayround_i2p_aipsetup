
import os.path

import wayround_org.aipsetup.builder_scripts.std

import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(
            called_as,
            log
            )

        ret += ['--with-python=3']

        if not self.is_crossbuild and not self.is_crossbuilder:
            ret += [
                ]
        else:
            ret += [
                '--without-python',
                '--without-ncurses',
                '--without-systemd',
                ]

        return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += [
            'INCLUDES=-I{}'.format(
                wayround_org.utils.path.join(
                    self.host_multiarch_dir,
                    'include',
                    'ncursesw'
                    )
                )
            ]
        return ret
