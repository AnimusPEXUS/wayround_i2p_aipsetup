
import wayround_org.aipsetup.builder_scripts.acl


class Builder(wayround_org.aipsetup.builder_scripts.acl.Builder):

    def define_custom_data(self):
        return {'subset': 'attr'}
