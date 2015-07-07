

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

# TODO: host oriented configuration required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):

        p = subprocess.Popen(
            [
                './genconfig.sh',
                #'--ipv6',
                #'--igd2',
                #'--strict',
                #'--pcp-peer',
                #'--portinuse'
            ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=['-f', 'Makefile.linux'],
            arguments=[],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            options=['-f', 'Makefile.linux'],
            arguments=[
                'install',
                'DESTDIR=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
