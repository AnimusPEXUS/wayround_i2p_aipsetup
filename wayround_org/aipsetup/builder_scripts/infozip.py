
import os.path
import subprocess

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del ret['autogen']
        del ret['configure']
        return ret

    def builder_action_build(self, log):
        p = subprocess.Popen(
            ['make',
             '-f', 'unix/Makefile',
             'generic',
             'CFLAGS=" -march=i486 -mtune=i486 "'
             ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, log):
        p = subprocess.Popen(
            ['make',
             '-f', 'unix/Makefile',
             'install',
             'prefix={}/usr'.format(self.dst_dir)
             ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret
