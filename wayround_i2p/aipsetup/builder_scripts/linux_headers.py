
import glob
import logging
import os.path
import shutil
import subprocess
import collections
import re

import wayround_i2p.utils.file
import wayround_i2p.utils.path
import wayround_i2p.utils.system_type

import wayround_i2p.aipsetup.build
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.aipsetup.builder_scripts.linux


class Builder(wayround_i2p.aipsetup.builder_scripts.linux.Builder):

    def define_actions(self):
        ret = self.define_actions()

        for i in ret.keys():
            if not i in [
                    'configure',
                    'build',
                    'distr_kernel',
                    'distr_modules',
                    'distr_firmware',
                    # 'distr_headers_all',
                    'distr_man',
                    'copy_source',
                    ]:
                del ret[i]

        return ret
