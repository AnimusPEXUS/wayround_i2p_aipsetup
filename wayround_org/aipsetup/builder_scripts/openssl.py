

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
        del ret['build']
        return ret

    def builder_action_configure_define_options(self, called_as, log):
        platform = 'linux-generic32'
        if self.host_strong.startswith('x86_64'):
            platform = 'linux-x86_64'
        # super().builder_action_configure_define_options(called_as, log) +
        ret = [
            '--prefix={}'.format(self.host_multiarch_dir),
            '--openssldir=/etc/ssl',
            'shared',
            'zlib-dynamic',

            ] + [platform]
        """
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--mandir=',
                    '--sysconfdir=',
                    '--localstatedir=',
                    '--host=',
                    '--build=',
                    '--target='
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
        """
        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        ret = self.all_automatic_flags_as_dict()
        return ret

    def builder_action_configure_define_script_name(self, called_as, log):
        return 'Configure'

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'MANDIR={}/share/man'.format(self.host_multiarch_dir),
                # 'MANSUFFIX=ssl',
                'INSTALL_PREFIX=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
