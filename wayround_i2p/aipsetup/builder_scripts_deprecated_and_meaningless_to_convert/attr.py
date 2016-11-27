
import wayround_i2p.aipsetup.builder_scripts.acl


class Builder(wayround_i2p.aipsetup.builder_scripts.acl.Builder):

    def define_custom_data(self):
        return {'subset': 'attr'}
