
import logging
import os.path
import subprocess
import collections
import inspect
import time

import wayround_i2p.utils.file
import wayround_i2p.utils.log

import wayround_i2p.aipsetup.build
import wayround_i2p.aipsetup.builder_scripts.std
import wayround_i2p.aipsetup.buildtools.autotools as autotools


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTALL_ROOT={}'.format(self.get_dst_dir())
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
