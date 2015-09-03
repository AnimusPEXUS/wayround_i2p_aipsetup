

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

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
        f = open(wayround_org.utils.path.join(self.get_src_dir(), 'makefile'))
        lines = f.read().split('\n')
        f.close()

        for i in range(len(lines)):

            if lines[i] == '\tldconfig':
                lines[i] = '#\tldconfig'

            if lines[
                    i] == '\tcp -rv $(srcdir)/Dependencies/ $(include_path)/$(libname_hdr)/$(srcdir)':
                lines[
                    i] = '\tcp -rv $(srcdir)/../Dependencies/ $(include_path)/$(libname_hdr)/$(srcdir)'

        f = open(wayround_org.utils.path.join(self.get_src_dir(), 'makefile'), 'w')
        f.write('\n'.join(lines))
        f.close()
        return 0

    def builder_action_build_a(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                ] + self.all_automatic_flags_as_list(),
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_a(self, called_as, log):

        os.makedirs(
            wayround_org.utils.path.join(
                self.calculate_dst_install_prefix()
                ),
            exist_ok=True
            )

        ret = autotools.make_high(
            self.buildingsite_path,
            options=[],
            arguments=[
                'install',
                'prefix={}'.format(self.calculate_dst_install_prefix())
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_build_so(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'SHARED=1'
                ] + self.all_automatic_flags_as_list(),
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_so(self, called_as, log):

        os.makedirs(
            wayround_org.utils.path.join(
                self.calculate_dst_install_libdir()
                ),
            exist_ok=True
            )

        ret = autotools.make_high(
            self.buildingsite_path,
            options=[],
            arguments=[
                'install',
                'prefix={}'.format(self.calculate_dst_install_prefix()),
                'SHARED=1'
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
