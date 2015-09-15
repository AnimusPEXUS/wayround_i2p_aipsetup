
import logging
import os.path
import glob

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.source_configure_reldir = 'unix'
        return None

    def define_actions(self):
        ret = super().define_actions()
        ret['links'] = self.builder_action_links
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
            
        for i in range(len(ret) - 1, -1, -1):
            for j in [
                    '--datarootdir=',
                    '--libdir=' # NOTE: tcl should be allways installed in 'lib'
                    ]:
                if ret[i].startswith(j):
                    del ret[i]
                    break
        ret += [
            '--enable-threads',
            '--enable-wince',
            ]
        ret += [
            # NOTE: tcl should be allways installed in 'lib'
            '--libdir={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'lib'
                    )
                )
            ]
        if self.get_arch_from_pkgi().startswith('x86_64'):
            ret += [
                '--enable-64bit',
                '--enable-64bit-vis',
                ]
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = super().builder_action_distribute(called_as, log)

        if ret == 0:
            ret = autotools.make_high(
                self.buildingsite_path,
                log=log,
                options=[],
                arguments=[
                    'install-private-headers',
                    'DESTDIR={}'.format(self.get_dst_dir())
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=self.separate_build_dir,
                source_configure_reldir=self.source_configure_reldir
                )
        return ret

    def builder_action_links(self, called_as, log):
        ret = 0

        pkg_name = self.get_package_info()['pkg_info']['name']

        bin_dir = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'bin'
            )

        bin_files = os.listdir(bin_dir)

        if pkg_name == 'tcl':
            for i in bin_files:
                if i.startswith('tclsh') and i != 'tclsh':

                    target_name = wayround_org.utils.path.join(
                        bin_dir,
                        'tclsh'
                        )

                    if (os.path.exists(target_name)
                            or os.path.islink(target_name)):

                        os.unlink(target_name)

                    os.symlink(i, target_name)

                    break

        if pkg_name == 'tk':
            for i in bin_files:
                if i.startswith('wish') and i != 'wish':

                    target_name = wayround_org.utils.path.join(
                        bin_dir,
                        'wish'
                        )

                    if (os.path.exists(target_name)
                            or os.path.islink(target_name)):

                        os.unlink(target_name)

                    os.symlink(i, target_name)

                    break
        return ret
