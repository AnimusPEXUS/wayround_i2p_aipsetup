
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
             '--prefix={}'.format(self.calculate_install_prefix())],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        return ['install',
                'DESTDIR={}'.format(self.calculate_dst_install_prefix())]
