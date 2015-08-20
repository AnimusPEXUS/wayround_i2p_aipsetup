
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.forced_target = False

        self.apply_host_spec_compilers_options = True

        self.source_configure_reldir = 'js/src'

        return None

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    'CC=',
                    'CXX=',
                    'GCC=',
                    #'--host=',
                    #'--build=',
                    #'--target=',
                    #'--includedir='
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break

        # if self.get_package_info()['pkg_info']['name'] == 'mozjs24':
        #    ret += ['LIBRARY_NAME=mozjs-24']

        # if self.get_package_info()['pkg_info']['name'] == 'mozjs24':
        #    ret += [self.get_arch_from_pkgi()]

        return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        ret += self.all_automatic_flags_as_list()

        # if self.get_package_info()['pkg_info']['name'] == 'mozjs24':
        #    ret += ['LIBRARY_NAME=mozjs-24']

        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = super().builder_action_distribute_define_args(called_as, log)
        ret += []  # self.all_automatic_flags_as_list()

        # if self.get_package_info()['pkg_info']['name'] == 'mozjs24':
        #    ret += ['LIBRARY_NAME=mozjs-24']

        return ret
