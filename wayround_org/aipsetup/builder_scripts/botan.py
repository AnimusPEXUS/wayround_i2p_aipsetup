
import subprocess

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.utils.path

import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):

        p = subprocess.Popen(
            ['./configure.py',
             '--prefix={}'.format(self.host_multiarch_dir)],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'DESTDIR={}'.format(self.dst_host_multiarch_dir),
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log
                ),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
