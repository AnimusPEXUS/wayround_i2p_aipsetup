

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        for i in [
                'autogen',
                ]:
            del(ret[i])
        return ret

    def builder_action_configure(self, called_as, log):
        ret = subprocess.Popen(
            ['bash', '-c', 'xmkmf'],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            ).wait()
        return ret

    def builder_action_build(self, called_as, log):
        ret = subprocess.Popen(
            ['make', 'World'],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            ).wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'install.man',
                'DESTDIR=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
