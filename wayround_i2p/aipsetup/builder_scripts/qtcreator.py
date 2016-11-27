

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.builder_scripts.std_qmake


class Builder(wayround_i2p.aipsetup.builder_scripts.std_qmake.Builder):

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)

        for i in range(len(ret) - 1, -1, -1):
            if ret[i].startswith('INSTALL_ROOT='):

                x = ret[i].split('=', 1)[1]

                ret[i] = wayround_i2p.utils.path.join(
                    x,
                    self.calculate_install_prefix()
                    )

                ret[i] = 'INSTALL_ROOT={}'.format(ret[i])

        return ret
