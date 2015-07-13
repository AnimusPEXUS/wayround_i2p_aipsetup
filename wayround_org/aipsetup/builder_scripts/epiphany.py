

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.utils.file
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        pkg_config = wayround_org.utils.file.which(
            'pkg-config',
            self.host_multiarch_dir
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

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            'NSS_CFLAGS=' + self.custom_data['NSS_CFLAGS'],
            'NSS_LIBS=' + self.custom_data['NSS_LIBS']
            ]
