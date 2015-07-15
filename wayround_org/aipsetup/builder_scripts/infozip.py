
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

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            ['make',
             '-f', 'unix/Makefile',
             'generic',
             # 'CFLAGS= -march=i486 -mtune=i486 ',
             'CC={}-gcc'.format(self.host_strong),
             'LDFLAGS={}'.format(
                 self.calculate_default_linker_program_gcc_parameter()
                 )
             ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            ['make',
             '-f', 'unix/Makefile',
             'install',
             'prefix={}'.format(self.dst_host_multiarch_dir)
             ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret
