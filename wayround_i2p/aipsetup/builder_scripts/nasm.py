

import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'INSTALLROOT={}'.format(self.get_dst_dir())
            ]
