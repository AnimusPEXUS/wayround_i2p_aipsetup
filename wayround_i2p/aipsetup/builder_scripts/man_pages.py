
import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del ret['autogen']
        del ret['configure']
        del ret['build']
        return ret
