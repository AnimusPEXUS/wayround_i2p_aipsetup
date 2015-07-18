

import wayround_org.aipsetup.builder_scripts.std

import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def disabled_builder_action_configure_define_environment(
            self, called_as, log):
        ret = {
            'CC': '{}'.format(
                wayround_org.utils.file.which(
                    '{}-gcc'.format(self.host_strong),
                    self.host_multiarch_dir
                    )
                ),
            'LDFLAGS': '{}'.format(
                self.calculate_default_linker_program_gcc_parameter()
                )
            }
        return ret

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[
                'CC={}'.format(
                    wayround_org.utils.file.which(
                        '{}-gcc'.format(self.host_strong),
                        self.host_multiarch_dir
                    )
                ),
                'LDFLAGS={}'.format(
                    self.calculate_default_linker_program_gcc_parameter()
                )
                ],
            arguments=[],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
