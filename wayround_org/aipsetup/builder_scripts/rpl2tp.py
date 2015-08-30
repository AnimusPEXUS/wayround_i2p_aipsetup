

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.forced_autogen=True
        
        return None

    def builder_action_distribute_define_args(self, called_as, log):
        ret = [
            'install',
            'RPM_INSTALL_ROOT={}'.format(
                self.get_dst_dir()
            )
        ]
        return ret

