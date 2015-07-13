
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

import wayround_org.utils.file
import wayround_org.utils.path


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        ret = super().builder_action_configure_define_options(
            called_as,
            log)
        ret += [
            '--with-installbuilddir={}'.format(
                wayround_org.utils.path.join(
                    self.host_multiarch_dir,
                    'share',
                    'apr',
                    'build-1'
                    )
                )
            ]
        return ret
