

import os.path
import subprocess
import glob
import shutil

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.utils.file

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        del ret['autogen']
        del ret['build']
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'all',
                'install',
                'prefix={}'.format(self.host_multiarch_dir),
                'exec_prefix={}'.format(self.host_multiarch_dir),
                'lib_prefix={}'.format(self.host_multiarch_dir),
                'inc_prefix={}'.format(self.host_multiarch_dir),
                'man_prefix={}'.format(self.host_multiarch_dir),
                'DESTDIR={}'.format(self.dst_dir),
                'RAISE_SETFCAP=no',
                'CC={}-gcc'.format(self.host_strong),
                'CXX={}-g++'.format(self.host_strong),
                'LDFLAGS={}'.format(
                    self.calculate_default_linker_program_gcc_parameter()
                    )
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):

        wayround_org.utils.file.copytree(
            os.path.join(
                self.dst_host_multiarch_dir,
                'multiarch'
                ),
            os.path.join(
                self.dst_host_multiarch_dir,
                'lib'
                ),
            overwrite_files=True,
            clear_before_copy=False,
            dst_must_be_empty=True,
            )

        shutil.rmtree(
            os.path.join(
                self.dst_host_multiarch_dir,
                'multiarch'
                )
            )

        return 0
