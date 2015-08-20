

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        return ret

    '''
    def builder_action_configure(self, called_as, log):

        p = subprocess.Popen(
            [
                './genconfig.sh',
                #'--ipv6',
                #'--igd2',
                #'--strict',
                #'--pcp-peer',
                #'--portinuse'
            ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret
    '''

    def builder_action_build_define_args(self, called_as, log):
        return [
            '-f', 'Makefile.linux',
            ] + self.all_automatic_flags_as_list(),

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            '-f', 'Makefile.linux',
            'install',
            'DESTDIR={}'.format(self.get_dst_dir())
            ]
