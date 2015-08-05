

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '--disable-gtk',
            '--enable-gtk3',
            '--enable-glib',
            '--enable-gobject',
            '--enable-python',
            '--enable-introspection',
            '--disable-mono',
            #'--disable-python-dbus',
            '--disable-pygtk',
            '--disable-qt3',
            '--enable-qt4',
            '--with-distro=lfs',
            #                    '--with-distro=' +
            #                        pkg_info['constitution']['system_title'],
            #                    '--with-dist-version=2.00',
            #                    '--without-systemdsystemunitdir',
            ]
        return ret
