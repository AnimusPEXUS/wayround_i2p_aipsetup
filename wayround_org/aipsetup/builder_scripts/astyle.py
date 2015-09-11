
import subprocess

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.source_configure_reldir = 'build/gcc'
        return

    def define_actions(self):

        ret = super().define_actions()

        for i in ['autogen', 'configure']:
            if i in ret:
                del ret[i]

        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            ['make'],
            cwd=wayround_org.utils.path.join(
                self.get_src_dir(),
                self.source_configure_reldir
                ),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            ['make',
                'install',
                'prefix={}'.format(self.calculate_dst_install_prefix())
             ],
            cwd=wayround_org.utils.path.join(
                self.get_src_dir(),
                self.source_configure_reldir
                ),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret
