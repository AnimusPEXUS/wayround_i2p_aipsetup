

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            '--disable-kparts3',
            '--disable-kparts4',
            '--disable-docbook',
            '--enable-media=ffmpeg',
            '--with-npapi-incl={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'include',
                    'mozilla'
                    )
                ),
            '--with-npapi-plugindir={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'lib',
                    'mozilla',
                    'plugins'
                    )
                )
            ]
