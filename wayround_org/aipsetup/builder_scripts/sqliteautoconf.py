

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--with-tcl={}'.format(
                os.path.join(self.host_multiarch_dir, 'lib')
                ),
            'CFLAGS= -DSQLITE_ENABLE_FTS3=1 '
            '-DSQLITE_ENABLE_COLUMN_METADATA=1 '
            '-DSQLITE_ENABLE_UNLOCK_NOTIFY=1 '
            '-DSQLITE_SECURE_DELETE=1 '
            ]
