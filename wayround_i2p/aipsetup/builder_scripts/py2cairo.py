

import os.path
import wayround_i2p.utils.path
import wayround_i2p.aipsetup.buildtools.waf as waf
import wayround_i2p.aipsetup.builder_scripts.pycairo


class Builder(wayround_i2p.aipsetup.builder_scripts.pycairo.Builder):

    def define_custom_data(self):
        ret = {
            'PYTHON': wayround_i2p.utils.file.which(
                'python2',
                self.get_host_dir()
                )
            }
        return ret
