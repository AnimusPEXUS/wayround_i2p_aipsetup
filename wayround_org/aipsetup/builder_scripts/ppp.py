
import os.path

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        thr = {}
        if self.is_crossbuild:
            thr['CFLAGS'] = ' -I{}'.format(
                os.path.join(self.target_host_root, 'usr', 'include')
                )
            thr['LDFLAGS'] = '-L{}'.format(
                os.path.join(self.target_host_root, 'usr', 'lib')
                )
        return {
            'thr': thr
            }

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
            '--with-pydebug'
            ]

    def builder_action_build(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'CHAPMS=1', 
                'USE_CRYPT=1', 
                'CC={}-gcc'.format(self.host),
                'INCLUDE_DIRS+= -I../include '+self.custom_data['thr']['CFLAGS'],
                #'LDFLAGS+= '+self.custom_data['thr']['LDFLAGS']
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTROOT=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
