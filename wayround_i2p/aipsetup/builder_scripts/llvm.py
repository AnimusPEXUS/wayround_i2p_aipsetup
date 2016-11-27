

import wayround_i2p.aipsetup.builder_scripts.std_cmake


class Builder(wayround_i2p.aipsetup.builder_scripts.std_cmake.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        return None

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        '''
           '--bindir=' +
            wayround_i2p.utils.path.join(
                self.calculate_install_prefix(),
                'bin'
                ),

            '--sbindir=' +
            wayround_i2p.utils.path.join(
                self.calculate_install_prefix(),
                'sbin'
                ),

        '''

        ret += [

            #'--enable-experimental-targets'  # enabling WebAssembly

            '-DLLVM_EXPERIMENTAL_TARGETS_TO_BUILD=WebAssembly',
            '-DLLVM_INSTALL_UTILS=on'

            ]

        return ret

    def builder_action_build_define_cpu_count(self, called_as, log):
        # NOTE: llvm building eats up too many resources, so keep it
        #       using only one core
        return 1
