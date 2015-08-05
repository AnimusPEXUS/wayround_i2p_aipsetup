

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--enable-bittorrent',
            '--enable-metalink',
            '--enable-epoll',
            '--with-gnutls',
            '--with-openssl',
            '--with-sqlite3',
            '--with-libxml2',
            '--with-libexpat',
            ]
        return ret
