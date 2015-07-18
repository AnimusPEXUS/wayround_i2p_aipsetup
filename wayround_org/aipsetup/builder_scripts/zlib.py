

import os.path
import copy

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        ret = [
            '--prefix={}'.format(self.host_multiarch_dir),
            '--shared',
            ]

        if '64' in self.host:
            ret += ['--64']

        return ret

    def builder_action_configure_define_environment(self, called_as, log):

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
            options=[],
            arguments=[
                'prefix={}'.format(self.dst_host_multiarch_dir),
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'prefix={}'.format(self.dst_host_multiarch_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
