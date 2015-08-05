

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-shadow',
            '--with-pam',
            '--with-bzlib',
            '--with-ldap=yes',
            '--with-sql=yes',
            '--without-pgsql',
            '--without-mysql',
            '--with-sqlite',
            '--with-zlib',
            '--with-ssl=openssl',
            '--with-storages=maildir,mbox,sdbox,mdbox,cydir',
            '--with-docs',
            ]
