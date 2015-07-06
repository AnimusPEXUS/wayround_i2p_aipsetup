

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--enable-tempstore=yes',
            'CFLAGS=-DSQLITE_HAS_CODEC',
            'LDFLAGS=-lcrypto -lreadline -ltinfow'
            ]
