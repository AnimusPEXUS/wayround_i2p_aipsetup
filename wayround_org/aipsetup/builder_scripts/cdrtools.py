
import os.path

import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        del(ret['build'])
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'all',
                'install',
                'LDPATH=-L{}'.format(
                    os.path.join(self.host_multiarch_dir, 'lib')
                    ),
                'RUNPATH=-R$(INS_BASE)/lib -R{}'.format(
                    os.path.join(self.host_multiarch_dir, 'lib')
                    ),
                'INS_BASE={}'.format(os.path.join(self.host_multiarch_dir)),
                'DESTDIR={}'.format(self.dst_dir),
                'CC={}'.format(
                    wayround_org.utils.file.which(
                        '{}-gcc'.format(self.host_strong),
                        self.host_multiarch_dir
                        )
                    ),
                # TODO: enable this without breaking the build
                #'LDFLAGS={}'.format(
                #    self.calculate_default_linker_program_gcc_parameter()
                #    )
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
