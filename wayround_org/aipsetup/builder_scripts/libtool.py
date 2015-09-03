

import os.path
import glob

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            #'--with-sysroot={}'.format(self.calculate_install_prefix()),
            # 'LT_SYS_LIBRARY_PATH={}'.format(
            #     ':'.join(
            #         [
            #             wayround_org.utils.path.join(
            #                 self.get_host_dir(),
            #                 'lib64'
            #             ),
            #             wayround_org.utils.path.join(
            #                 self.get_host_dir(),
            #                 'lib'
            #             ),
            #         ]
            #     )
            # )
        ]
        return ret
