

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--with-openssl',
            '--with-curl',
            '--with-expat',
            '--with-perl={}'.format(self.get_dst_host_dir())
            ]
        return ret
