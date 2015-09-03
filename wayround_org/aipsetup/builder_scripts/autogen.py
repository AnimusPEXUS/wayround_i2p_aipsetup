

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):

        # NOTE: this configuration based on autogen 5.18.4 error
        #       records in log.. guile related configuration is insane :-/
        #       and --with-libguile= usage is probably incorrect

        guile_prefix = self.calculate_install_prefix()

        guile_config = wayround_org.utils.path.join(
            guile_prefix,
            'bin',
            'guile-config'
            )

        guile_cflags = str(
            subprocess.check_output([guile_config, 'compile']),
            'utf-8'
            )
        guile_libs = str(
            subprocess.check_output([guile_config, 'link']),
            'utf-8'
            )

        ret = super().builder_action_configure_define_opts(called_as, log)

        ret += [
            '--with-libguile={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix()
                    )
                ),
            ]

        ret += [
            '--with-libguile-cflags={}'.format(guile_cflags),
            '--with-libguile-libs={}'.format(guile_libs),
            ]

        return ret
