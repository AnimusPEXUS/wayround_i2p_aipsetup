

import subprocess

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        ret = []

        ret += [
            'PREFIX={}'.format(self.calculate_install_prefix())
            ]
    
        return ret

    def builder_action_configure(self, called_as, log):
        envs = {}
        if hasattr(self, 'builder_action_configure_define_environment'):
            envs = self.builder_action_configure_define_environment(
                called_as,
                log
                )

        opts = []
        if hasattr(self, 'builder_action_configure_define_opts'):
            opts = self.builder_action_configure_define_opts(
                called_as,
                log
                )

        args = []
        if hasattr(self, 'builder_action_configure_define_args'):
            args = self.builder_action_configure_define_args(
                called_as,
                log
                )

        env = wayround_org.utils.osutils.env_vars_edit(
            envs,
            'copy'
            )

        if len(environment) > 0:
            log.info(
                "Environment modifications:"
                )

            for i in sorted(list(environment.keys())):
                log.info("    {}:".format(i))
                log.info("        {}".format(environment[i]))

        p = subprocess.Popen(
            ['qmake']+ opts + args,
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr,
            env=env
            )
        ret = p.wait()
        return ret

    #def builder_action_build_define_cpu_count(self, called_as, log):
    #    return 1

    def builder_action_distribute_define_args(self, called_as, log):
        ret = [
            'install',
            'INSTALL_ROOT={}'.format(self.get_dst_dir())
            ]
        return ret
