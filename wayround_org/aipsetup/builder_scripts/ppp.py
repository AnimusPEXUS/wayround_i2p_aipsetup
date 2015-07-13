
import os.path

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        thr = {
            'CFLAGS': '',
            'LDFLAGS': '',
            'CC': [],
            }
        if self.is_crossbuild:
            thr['CFLAGS'] = ' -I{}'.format(
                os.path.join(self.host_multiarch_dir, 'include')
                )
            thr['LDFLAGS'] = '-L{}'.format(
                os.path.join(self.host_multiarch_dir, 'lib')
                )
            #thr['CC'] = ['CC={}-gcc'.format(self.host_strong)]
        return {
            'thr': thr
            }

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--with-pydebug'
            ]

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'CHAPMS=1',
                'USE_CRYPT=1',
                'INCLUDE_DIRS+= -I../include ' +
                self.custom_data['thr']['CFLAGS'],
                #'LDFLAGS+= '+self.custom_data['thr']['LDFLAGS']
                ]# + self.custom_data['thr']['CC'],
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
                'INSTROOT={}'.format(self.dst_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
