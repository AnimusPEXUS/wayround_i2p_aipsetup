
import subprocess

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    

    
    def builder_action_configure_define_options(self, called_as, log):

        nss_cflags = ''
        p = subprocess.Popen(
            ['pkg-config', '--cflags', 'nspr', 'nss'],
            stdout=subprocess.PIPE
            )
        pr = p.communicate()
        nss_cflags = str(pr[0], 'utf-8').strip()

        nss_libs = ''
        p = subprocess.Popen(
            ['pkg-config', '--libs', 'nspr', 'nss'],
            stdout=subprocess.PIPE
            )
        pr = p.communicate()
        nss_libs = str(pr[0], 'utf-8').strip()

        return super().builder_action_configure_define_options(called_as, log) + [
            'CFLAGS=' + nss_cflags,
            'LDFLAGS=' + nss_libs
            ]

    