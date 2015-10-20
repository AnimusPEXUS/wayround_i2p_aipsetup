

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    # FIXME: slag can't build with more than 1 j
    def builder_action_build_define_cpu_count(self, called_as, log):
        return 1
