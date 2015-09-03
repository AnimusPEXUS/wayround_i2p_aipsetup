

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            #'--with-systemd={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_lib_dir(),
            #        'systemd',
            #        'system'
            #        )
            #    ),
            'SERVERBIN={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_dst_install_libdir(),
                    'cups'
                    )
                ),
            ]
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'BUILDROOT={}'.format(self.get_dst_dir()),
            'SERVERBIN={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_dst_install_libdir(),
                    'cups'
                    )
                )
            ]
