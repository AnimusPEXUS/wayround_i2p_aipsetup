

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(log) + [
            '--with-x',
            # '--enable-selinux', #lib needed
            '--enable-libaudit',
            '--enable-dnotify',
            '--enable-inotify',
            # '--enable-kqueue', #BSD needed
            # '--enable-launchd', #MacOS needed
            '--enable-systemd',
            ]
