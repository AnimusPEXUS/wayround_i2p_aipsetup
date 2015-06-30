

import os.path

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        del ret['autogen']
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'prefix=' + os.path.join('/usr'),
                'exec_prefix='+ os.path.join('/usr'),
                'lib_prefix='+ os.path.join('/usr'),
                'inc_prefix=' + os.path.join('/usr'),
                'man_prefix=' + os.path.join('/usr'),
                'DESTDIR=' + self.dst_dir,
                'RAISE_SETFCAP=no'
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):
        
        os.rename(
            os.path.join(
                self.dst_dir,
                'usr',
                'multiarch'
                ),
            os.path.join(
                self.dst_dir,
                'usr',
                'lib'
                )
            )
        
        return 0