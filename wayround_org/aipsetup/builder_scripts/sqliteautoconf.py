

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
            '--with-tcl=/usr/lib',
            'CFLAGS= -DSQLITE_ENABLE_FTS3=1 '
            '-DSQLITE_ENABLE_COLUMN_METADATA=1 '
            '-DSQLITE_ENABLE_UNLOCK_NOTIFY=1 '
            '-DSQLITE_SECURE_DELETE=1 '
            ]
