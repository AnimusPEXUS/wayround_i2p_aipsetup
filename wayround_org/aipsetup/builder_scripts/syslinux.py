

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        del ret['autogen']
        del ret['patch']
        del ret['build']
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'bios', 'efi32', 'efi64',
                'installer',
                'install',
                'INSTALLROOT={}'.format(self.dst_dir),
                'CC={}'.format(
                    wayround_org.utils.file.which(
                        '{}-gcc'.format(self.host_strong),
                        self.host_multiarch_dir
                        )
                    ),
                #'LDFLAGS={}'.format(
                #    self.calculate_default_linker_program_ld_parameter()
                #    )
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
