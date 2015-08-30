
import os.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--enable-nls',
            '--datarootdir={}'.format(
                wayround_org.utils.path.join(
                    self.get_host_dir(),
                    'share',
                    'kbd'
                    )
                )
            ]
