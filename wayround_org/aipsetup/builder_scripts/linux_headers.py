
import glob
import logging
import os.path
import shutil
import subprocess
import collections
import re

import wayround_org.utils.file
import wayround_org.utils.path
import wayround_org.utils.system_type

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.linux


class Builder(wayround_org.aipsetup.builder_scripts.linux.Builder):

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
