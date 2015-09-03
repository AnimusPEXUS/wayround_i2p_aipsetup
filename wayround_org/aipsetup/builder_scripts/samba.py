

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['afetr_distribute'] = self.builder_action_afetr_distribute
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-pam',
            '--with-pam_smbpass',
            '--enable-fhs',
            '--with-systemd',
            #                    '--with-swatdir=/usr/share/samba/swat',
            '--sysconfdir=/etc/samba',
            #                    '--libexecdir=/usr/libexec',
            #'--libdir={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(), 
            #        'lib'
            #        )
            #    ),
            '--with-configdir=/etc/samba',
            '--with-privatedir=/etc/samba/private',
            #                    '--includedir=/usr/include',
            #                    '--datarootdir=/usr/share',
            ]

    def builder_action_afetr_distribute(self, called_as, log):
        for i in ['examples', 'docs']:

            wayround_org.utils.file.copytree(
                wayround_org.utils.path.join(self.get_src_dir(), i),
                wayround_org.utils.path.join(
                    self.calculate_dst_install_prefix(), 'share', 'samba', i
                    ),
                overwrite_files=True,
                clear_before_copy=False,
                dst_must_be_empty=False
                )
        return 0
