

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)

        for i in [
                '--includedir=',
                '--mandir=',
                '--sysconfdir=',
                '--localstatedir=',
                '--enable-shared',
                '--host=',
                '--build=',
                '--tarbet=',
                'CC=',
                'CXX=',
                'GCC=',
                'LDFLAGS=',
                ]:
            for j in range(len(ret) - 1, -1, -1):
                if ret[j].startswith(i):
                    del ret[j]

        # ret += self.all_automatic_flags_as_list()

        return ret

    #def builder_action_configure_define_environment(self, called_as, log):
    #    ret = self.all_automatic_flags_as_dict()
    #    return ret

    # def builder_action_build_define_environment(self, called_as, log):
    #    ret = super().builder_action_build_define_environment(called_as, log)
    #    ret.update(self.all_automatic_flags_as_dict())
    #    return ret

    def builder_action_build_define_args(self, called_as, log):
        ret = super().builder_action_build_define_args(called_as, log)
        #ret += self.all_automatic_flags_as_list()
        ret += [
            #'V=1'
            'GCC={}'.format(self.calculate_CC_string())
            ]
        return ret

    # def builder_action_distribute_define_environment(self, called_as, log):
    #    ret = super().builder_action_build_define_environment(called_as, log)
    #    ret.update(self.all_automatic_flags_as_dict())
    #    return ret
