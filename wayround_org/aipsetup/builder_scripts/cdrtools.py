
import os.path

import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True
        return

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        del(ret['build'])
        return ret

    def builder_action_distribute_define_args(self, called_as, log):
        ret = [
            'all',
            'install',
            #'LDPATH=-L{}'.format(
            #    wayround_org.utils.path.join(self.get_host_dir(), 'lib')
            #    ),
            #'RUNPATH=-R$(INS_BASE)/lib -R{}'.format(
            #    wayround_org.utils.path.join(self.get_host_dir(), 'lib')
            #    ),
            'INS_BASE={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix()
                    )
                ),
            'DESTDIR={}'.format(self.get_dst_dir()),
            ] + self.all_automatic_flags_as_list(),
        return ret
