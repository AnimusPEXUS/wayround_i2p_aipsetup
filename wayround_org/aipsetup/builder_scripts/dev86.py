
import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        return ret

    def define_custom_data(self):
        ret = {
            'dst_usr_dir': wayround_org.utils.path.join(
                self.dst_dir,
                'multiarch',
                self.host
                ),
            'CC': '{}-gcc'.format(self.host)
            }
        return ret

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'CC=' + self.custom_data['CC']
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
                'PREFIX=',
                'DESTDIR=' + self.custom_data['dst_usr_dir'],
                'DIST=' + self.custom_data['dst_usr_dir'],
                'BINDIR=/bin',
                'LIBDIR=/lib/bcc',
                'INCLDIR=/lib/bcc',
                'ASLDDIR=/bin',
                'MANDIR=/share/man',
                #'INDAT=', 'INEXE='
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
