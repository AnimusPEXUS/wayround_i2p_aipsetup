

import os.path
import subprocess

import wayround_i2p.utils.path
import wayround_i2p.utils.file
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        pkg_config = wayround_i2p.utils.file.which(
            'pkg-config',
            self.get_host_dir()
            )

        nss_cflags = ''
        p = subprocess.Popen(
            [pkg_config, '--cflags', 'nspr', 'nss'], stdout=subprocess.PIPE)
        pr = p.communicate()
        nss_cflags = str(pr[0], 'utf-8').strip()

        nss_libs = ''
        p = subprocess.Popen(
            [pkg_config, '--libs', 'nspr', 'nss'], stdout=subprocess.PIPE)
        pr = p.communicate()
        nss_libs = str(pr[0], 'utf-8').strip()

        ret = {
            'NSS_CFLAGS': nss_cflags,
            'NSS_LIBS': nss_libs
            }
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            'NSS_CFLAGS={}'.format(self.custom_data['NSS_CFLAGS']),
            'NSS_LIBS={}'.format(self.custom_data['NSS_LIBS'])
            ]
        return ret
