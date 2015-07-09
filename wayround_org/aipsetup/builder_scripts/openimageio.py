

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '-DSTOP_ON_WARNING=OFF',
            ]
