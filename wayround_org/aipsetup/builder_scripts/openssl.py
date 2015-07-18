

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

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
        ret = {
            'CC': '{}'.format(
                wayround_org.utils.file.which(
                    '{}-gcc'.format(self.host_strong),
                    self.host_multiarch_dir
                    )
                ),
            # 'CFLAGS': '-m32',
            'LDFLAGS': '{}'.format(
                self.calculate_default_linker_program_gcc_parameter()
                )
            }
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
                'MANDIR=/usr/share/man',
                # 'MANSUFFIX=ssl',
                'INSTALL_PREFIX=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
