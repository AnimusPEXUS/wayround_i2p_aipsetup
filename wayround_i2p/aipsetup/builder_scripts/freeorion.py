

import wayround_i2p.aipsetup.builder_scripts.cmake


class Builder(wayround_i2p.aipsetup.builder_scripts.cmake.Builder):
    def define_custom_data(self):
        self.source_configure_reldir = 'FreeOrion'
