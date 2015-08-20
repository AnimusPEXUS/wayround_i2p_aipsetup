
import os

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'DESTDIR={}'.format(self.get_dst_dir()),
            'INSTUSR={}'.format(str(os.getuid())),
            'INSTGRP={}'.format(str(os.getgid())),
            'MANGRP={}'.format(str(os.getgid()))
            ]
