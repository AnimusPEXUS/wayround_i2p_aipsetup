
import subprocess

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.forced_autogen = False
        return

    def builder_action_configure_define_opts(self, called_as, log):

        '''
        envs = self.builder_action_configure_define_environment(
            called_as,
            log
            )

        pkg_config_paths = self.calculate_pkgconfig_search_paths()

        envs.update(
            {'PKG_CONFIG_PATH': ':'.join(pkg_config_paths)},
            )

        envs.update(self.builder_action_configure_define_PATH_dict())
        '''

        nss_cflags = ''
        p = subprocess.Popen(
            ['pkg-config', '--cflags', 'nspr', 'nss'],
            stdout=subprocess.PIPE,
            #env=envs
            )
        pr = p.communicate()
        nss_cflags = str(pr[0], 'utf-8').strip()

        nss_libs = ''
        p = subprocess.Popen(
            ['pkg-config', '--libs', 'nspr', 'nss'],
            stdout=subprocess.PIPE,
            #env=envs
            )
        pr = p.communicate()
        nss_libs = str(pr[0], 'utf-8').strip()

        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            'CFLAGS={}'.format(nss_cflags),
            'LDFLAGS={}'.format(nss_libs),
            '--with-suspend-resume=systemd',
            '--with-session-tracking=systemd',
            #'--with-systemdsystemunitdir={}'.format(
            #    wayround_org.utils.path.join(
            #        self.calculate_install_prefix(),
            #        'systemd',
            #        'system'
            #        )
            #    )
            ]

        return ret
