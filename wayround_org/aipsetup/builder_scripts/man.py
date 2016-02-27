
import os.path

import wayround_org.aipsetup.builder_scripts.std

# TODO: configure are not standard so additional attention to host and paths
#       required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return [
            '-d',
            '-prefix={}'.format(self.calculate_install_prefix())
            ]

    def define_actions(self):
        ret = super().define_actions()
        ret['fix_config'] = self.builder_action_fix_config
        return ret

    def builder_action_fix_config(self, called_as, log):

        # cfg_file = wayround_org.utils.path.join(
        #    self.get_dst_host_dir(), 'share', 'misc', 'man.conf'
        #    )

        cfg_file = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            #'multihost',
            # self.get_host_from_pkgi(),
            'share',
            'misc',
            'man.conf'
            )

        with open(cfg_file) as f:
            fl = f.read().splitlines()

        for i in range(len(fl)):

            if fl[i] == 'PAGER\t\t/bin/less -is':
                fl[i] = 'PAGER\t\t/bin/less -is -R'

        with open(cfg_file, 'w') as f:
            f.write('\n'.join(fl))

        return 0
