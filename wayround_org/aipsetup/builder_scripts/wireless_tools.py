
import os.path
import subprocess

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        del ret['autogen']
        del ret['patch']
        del ret['build']
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            ['make',
             'all',
             'install',
             'PREFIX={}'.format(self.dst_host_multiarch_dir),
             'CC={}'.format(
                 wayround_org.utils.file.which(
                     '{}-gcc'.format(self.host_strong),
                     self.host_multiarch_dir
                     )
                 ),
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
