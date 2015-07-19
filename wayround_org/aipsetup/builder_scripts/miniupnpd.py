

import os.path
import subprocess

import wayround_org.utils.path
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
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret
    '''

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[
                '-f', 'Makefile.linux',
                ] + self.all_automatic_flags_as_list(),
            arguments=[],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=['-f', 'Makefile.linux'],
            arguments=[
                'install',
                'DESTDIR={}'.format(self.dst_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
