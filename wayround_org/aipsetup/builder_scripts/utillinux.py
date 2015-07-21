
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(
            called_as,
            log
            )

        ret += [
            '--with-sysroot={}'.format(self.host_multiarch_dir),

            # TODO: investigate and enable python
            '--without-python',
            #'--with-python=3'
            ]

        if not self.is_crossbuild and not self.is_crossbuilder:
            ret += [
                ]
        else:
            ret += [
                '--without-python',
                '--without-ncurses',
                '--without-systemd',
                ]

        return ret
