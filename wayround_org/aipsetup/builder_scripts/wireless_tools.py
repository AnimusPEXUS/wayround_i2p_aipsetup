
import os.path
import subprocess

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True
        return

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        del ret['autogen']
        del ret['patch']
        del ret['build']
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            ['make',
             'all',
             'install',
             'PREFIX={}'.format(self.calculate_dst_install_prefix()),
             #'INSTALL_LIB={}'.format(self.get_dst_host_lib_dir()),
             ] + self.all_automatic_flags_as_list(),
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret
