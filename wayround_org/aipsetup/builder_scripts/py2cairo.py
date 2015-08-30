

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.waf as waf
import wayround_org.aipsetup.builder_scripts.pycairo


class Builder(wayround_org.aipsetup.builder_scripts.pycairo.Builder):

    def define_custom_data(self):
        ret = {
            'PYTHON': wayround_org.utils.file.which(
                'python2',
                self.get_host_dir()
                )
            }
        return ret
