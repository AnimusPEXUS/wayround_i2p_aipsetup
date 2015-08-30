

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            #'--with-tcl={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        self.calculate_main_multiarch_lib_dir_name()
            #        )
            #    ),
            'CFLAGS='
            '-DSQLITE_ENABLE_FTS3=1 '
            '-DSQLITE_ENABLE_COLUMN_METADATA=1 '
            '-DSQLITE_ENABLE_UNLOCK_NOTIFY=1 '
            '-DSQLITE_SECURE_DELETE=1 '
            ]
