

import wayround_i2p.aipsetup.builder_scripts.std_cmake


class Builder(wayround_i2p.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_build_define_cpu_count(self, called_as, log):
        return 1
