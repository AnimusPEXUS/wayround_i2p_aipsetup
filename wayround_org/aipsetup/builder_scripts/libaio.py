

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.utils.pkgconfig
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()

        del ret['autogen']
        del ret['configure']

        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            ['make', 
            'prefix={}'.format(self.calculate_install_prefix())
            ] + self.all_automatic_flags_as_list(),
            cwd=self.get_src_dir()
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            ['make', 'install', 'prefix={}'.format(
                self.calculate_dst_install_prefix())],
            cwd=self.get_src_dir()
            )
        ret = p.wait()
        return ret
