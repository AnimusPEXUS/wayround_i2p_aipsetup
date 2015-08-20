

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--disable-libuuid',
            '--disable-uuidd',
            '--disable-libblkid',
            '--enable-elf-shlibs',
            '--disable-fsck'
            ]

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'install-libs',
            'DESTDIR={}'.format(self.get_dst_dir())
            ]
