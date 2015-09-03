
import os.path
import subprocess
import collections

import wayround_org.aipsetup.builder_scripts.std

# TODO: add fixes and patches


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        # 'python2' value may go here
        return None

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('bootstrap', self.builder_action_bootstrap),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_bootstrap(self, called_as, log):
        p = subprocess.Popen(
            [
                'python2',
                'bootstrap.py',
                wayround_org.utils.path.join(self.get_src_dir(), 'build', 'scons')
                ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            [python,
             'setup.py',
             'install',
             '--prefix={}'.format(self.calculate_dst_install_prefix())
             ],
            cwd=wayround_org.utils.path.join(self.get_src_dir(), 'build', 'scons'),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret
