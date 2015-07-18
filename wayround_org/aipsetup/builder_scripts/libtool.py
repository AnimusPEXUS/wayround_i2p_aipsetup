

import os.path
import glob

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        LT_SYS_LIBRARY_PATH = glob.glob('/multiarch/*/lib')

        for i in range(len(LT_SYS_LIBRARY_PATH) - 1, -1, -1):
            if '_primary' in LT_SYS_LIBRARY_PATH[i]:
                del LT_SYS_LIBRARY_PATH[i]

        return super().builder_action_configure_define_options(called_as, log) + [
            'LT_SYS_LIBRARY_PATH={}'.format(
                ' '.join(LT_SYS_LIBRARY_PATH)
                )
            ]
