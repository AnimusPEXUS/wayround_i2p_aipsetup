
import os.path

import wayround_i2p.aipsetup.build
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.utils.file


import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = {
            'apr_1_config': wayround_i2p.utils.file.which(
                'apr-1-config',
                self.calculate_install_prefix()
                )
            }
        if ret['apr_1_config'] is None:
            raise Exception("`apr-1-config' not installed on system")
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(
            called_as,
            log) + [
                '--with-apr=' + self.custom_data['apr_1_config'],
                '--with-berkeley-db={}'.format(
                    self.calculate_install_prefix()
                    ),
                ]
