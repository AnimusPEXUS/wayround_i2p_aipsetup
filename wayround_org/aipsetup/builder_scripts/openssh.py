
import os.path
import collections

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['rename_configs'] = self.builder_action_rename_configs
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-tcp-wrappers',
            '--with-pam',
            '--sysconfdir=/etc/ssh'
            ]

    def builder_action_rename_configs(self, called_as, log):
        os.rename(
            os.path.join(self.dst_dir, 'etc', 'ssh', 'sshd_config'),
            os.path.join(self.dst_dir, 'etc', 'ssh', 'sshd_config.origin')
            )
        os.rename(
            os.path.join(self.dst_dir, 'etc', 'ssh', 'ssh_config'),
            os.path.join(self.dst_dir, 'etc', 'ssh', 'ssh_config.origin')
            )
        return 0
