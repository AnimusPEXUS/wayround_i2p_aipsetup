
import wayround_org.utils.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-openssl',
            '--with-curl',
            '--with-expat',
            #'sharedir={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        'share'
            #        )
            #    )
            ]

        return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += [
            #'sharedir={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        'share'
            #        )
            #    )
            ]
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret += [
            #'sharedir={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        'share'
            #        )
            #    )
            ]
        return ret
