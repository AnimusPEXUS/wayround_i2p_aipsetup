
import wayround_org.aipsetup.build_scripts.std


class Builder(wayround_org.aipsetup.build_scripts.std):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(log) + [
            '--enable-udev-acl',
            '--enable-pam-module',
            ]
