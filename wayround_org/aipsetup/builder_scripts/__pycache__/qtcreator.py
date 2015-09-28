

import subprocess

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):
        # TODO: env, opts, args etc..
        p = subprocess.Popen(
            ['qmake', 
                'PREFIX={}'.format(self.calculate_install_prefix()),
                'IDE_BUILD_TREE={}'.format(self.calculate_install_prefix()),
                ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    #def builder_action_build_define_cpu_count(self, called_as, log):
    #    return 1

    def builder_action_distribute_define_args(self, called_as, log):
        ret = [
            'install',
            'INSTALL_ROOT={}'.format(self.get_dst_dir())
            ]
        return ret
