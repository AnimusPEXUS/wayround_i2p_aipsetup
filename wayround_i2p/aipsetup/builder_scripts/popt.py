

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            'pkgconfigdir={}'.format(
                wayround_i2p.utils.path.join(
                    self.calculate_install_libdir(),
                    'pkgconfig'
                    )
                ),
            ]
        return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += [
            'pkgconfigdir={}'.format(
                wayround_i2p.utils.path.join(
                    self.calculate_install_libdir(),
                    'pkgconfig'
                    )
                ),
            ]
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret += [
            'pkgconfigdir={}'.format(
                wayround_i2p.utils.path.join(
                    self.calculate_install_libdir(),
                    'pkgconfig'
                    )
                ),
            ]
        return ret
