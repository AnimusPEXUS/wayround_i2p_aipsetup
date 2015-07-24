
import os.path

import wayround_org.aipsetup.builder_scripts.std

import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(
            called_as,
            log
            )

        ret += [
            '--with-python=3'
            ]

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

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'INCLUDES=-I{}'.format(
                    os.path.join(
                        self.host_multiarch_dir,
                        'include',
                        'ncursesw'
                    )
                )
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
