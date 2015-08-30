

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-x',
            # '--enable-selinux', #lib needed
            '--enable-libaudit',
            '--enable-dnotify',
            '--enable-inotify',
            # '--enable-kqueue', #BSD needed
            # '--enable-launchd', #MacOS needed

            # NOTE: cyrcular dep with systemd. 
            #       build without systemd may be required once
            '--enable-systemd', 
            #'--disable-systemd',

            # NOTE: cyrcular dep with dbus-glib
            # NOTE: dbus-glib is deprecated
            # '--without-dbus-glib'
            ]
