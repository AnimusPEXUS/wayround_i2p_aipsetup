

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--disable-kparts3',
            '--disable-kparts4',
            '--disable-docbook',
            '--enable-media=ffmpeg',
            '--with-npapi-incl={}'.format(
                wayround_i2p.utils.path.join(
                    self.calculate_install_prefix(),
                    'include',
                    'mozilla'
                    )
                ),
            '--with-npapi-plugindir={}'.format(
                wayround_i2p.utils.path.join(
                    self.calculate_install_prefix(),
                    'lib', # TODO: not sure.. maybe lib64 on x86_64 
                           #       systems
                    'mozilla',
                    'plugins'
                    )
                )
            ]
