
import os.path

import wayround_i2p.aipsetup.build
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.std

import wayround_i2p.utils.file
import wayround_i2p.utils.path


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(
            called_as,
            log
            )
        ret += [
            #'--with-installbuilddir={}'.format(
            #    wayround_i2p.utils.path.join(
            #        self.get_host_dir(),
            #        'share',
            #        'apr',
            #        'build-1'
            #        )
            #    )
            ]
        return ret
