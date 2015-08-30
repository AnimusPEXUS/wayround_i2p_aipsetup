

import wayround_org.utils.path
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            '-DOPENJPEG_INSTALL_LIB_DIR={}'.format(
                self.calculate_main_multiarch_lib_dir_name()
                ),
            ]
        return ret
