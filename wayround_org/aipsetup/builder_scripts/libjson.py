

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['configure'])
        del(ret['autogen'])
        del(ret['build'])
        del(ret['distribute'])

        ret['build_a'] = self.builder_action_build_a
        ret['distribute_a'] = self.builder_action_distribute_a

        ret['build_so'] = self.builder_action_build_so
        ret['distribute_so'] = self.builder_action_distribute_so

        return ret

    def builder_action_patch(self, called_as, log):
        f = open(os.path.join(self.src_dir, 'makefile'))
        lines = f.read().split('\n')
        f.close()

        for i in range(len(lines)):

            if lines[i] == '\tldconfig':
                lines[i] = '#\tldconfig'

            if lines[
                    i] == '\tcp -rv $(srcdir)/Dependencies/ $(include_path)/$(libname_hdr)/$(srcdir)':
                lines[
                    i] = '\tcp -rv $(srcdir)/../Dependencies/ $(include_path)/$(libname_hdr)/$(srcdir)'

        f = open(os.path.join(self.src_dir, 'makefile'), 'w')
        f.write('\n'.join(lines))
        f.close()
        return 0

    def builder_action_build_a(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'CXX={}-g++'.format(self.host_strong),
                'CC={}-gcc'.format(self.host_strong),
                'LDFLAGS={}'.format(
                    self.calculate_default_linker_program_gcc_parameter()
                    )
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_a(self, called_as, log):

        os.makedirs(
            os.path.join(self.dst_host_multiarch_dir, 'lib'),
            exist_ok=True
            )

        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'install',
                'prefix={}'.format(self.dst_host_multiarch_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_build_so(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'CXX={}-g++'.format(self.host_strong),
                'CC={}-gcc'.format(self.host_strong),
                'LDFLAGS={}'.format(
                    self.calculate_default_linker_program_gcc_parameter()
                    ),
                'SHARED=1'
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_so(self, called_as, log):

        os.makedirs(
            os.path.join(self.dst_host_multiarch_dir, 'lib'),
            exist_ok=True
            )

        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'install',
                'prefix={}'.format(self.dst_host_multiarch_dir),
                'SHARED=1'
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
