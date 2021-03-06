

import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--enable-tempstore=yes',
            # '--with-readline-lib=',
            '--disable-readline',
            'CFLAGS=-DSQLITE_HAS_CODEC',
            #'LDFLAGS=-lcrypto -lreadline -ltinfow',
            'LDFLAGS=-lcrypto',
            ]
