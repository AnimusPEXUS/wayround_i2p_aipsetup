

import subprocess

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # /usr/lib/systemd/system
            #'--with-systemdsystemunitdir={}'.format(
            #    wayround_org.utils.path.join(
            #        self.calculate_install_prefix(),
            #        'systemd',
            #        'system'
            #        )
            #     )
            ]

        return ret
