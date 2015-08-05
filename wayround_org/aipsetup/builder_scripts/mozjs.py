
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.forced_target = False

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
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

        # if self.package_info['pkg_info']['name'] == 'mozjs24':
        #    ret += ['LIBRARY_NAME=mozjs-24']

        # if self.package_info['pkg_info']['name'] == 'mozjs24':
        #    ret += [self.host_strong]

        return ret

    '''
    def builder_action_make_define_environment(self, called_as, log):
        return self.all_automatic_flags_as_dict()
    '''
    
    '''
    def builder_action_build(self, called_as, log):
        
        log.info("performing patch")
    '''

    def builder_action_build_define_add_args(self, called_as, log):
        ret = self.all_automatic_flags_as_list()

        # if self.package_info['pkg_info']['name'] == 'mozjs24':
        #    ret += ['LIBRARY_NAME=mozjs-24']

        return ret

    def builder_action_distribute_define_add_args(self, called_as, log):
        ret = []  # self.all_automatic_flags_as_list()

        # if self.package_info['pkg_info']['name'] == 'mozjs24':
        #    ret += ['LIBRARY_NAME=mozjs-24']

        return ret
