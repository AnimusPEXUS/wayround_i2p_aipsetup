
import os.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, log):
        return ['-d']

    def define_actions(self):
        ret = super().define_actions()
        ret['fix_config'] = self.builder_action_fix_config
        return ret

    def builder_action_fix_config(self, log):

        cfg_file = os.path.join(
            self.dst_dir, 'usr', 'share', 'misc', 'man.conf'
            )

        with open(cfg_file) as f:
            fl = f.read().splitlines()

        for i in range(len(fl)):

            if fl[i] == 'PAGER\t\t/bin/less -is':
                fl[i] = 'PAGER\t\t/bin/less -is -R'

        with open(cfg_file, 'w') as f:
            f.write('\n'.join(fl))

        return 0
