

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        return super().builder_action_configure_define_opts(called_as, log) + [
            '--with-bzip2=yes',
            '--with-png=yes',

            # NOTE: harfbuzz <-> freetype is the circular dep. so it
            #       might be required to build freetype without
            #       harfbuzz once before building harfbuzz on it's
            #       own.
            #
            # '--without-harfbuzz',
            ]
