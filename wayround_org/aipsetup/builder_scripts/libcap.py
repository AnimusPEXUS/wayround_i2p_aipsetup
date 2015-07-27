

import os.path
import subprocess
import glob
import shutil

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.utils.file


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
        del ret['build']
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    '''
    def patch_test_c(self):
        name = os.path.join(self.src_dir, 'pam_cap', 'test.c')

        with open(name) as f:
            t = f.read()

        t = t.replace('<security/', '<')

        with open(name, 'w') as f:
            f.write(t)

        return 0

    def patch_pam_cap_c(self):
        name = os.path.join(self.src_dir, 'pam_cap', 'pam_cap.c')

        with open(name) as f:
            t = f.read()

        t = t.replace('<security/', '<')

        with open(name, 'w') as f:
            f.write(t)

        return 0

    def builder_action_patch(self, called_as, log):

        self.patch_test_c()
        self.patch_pam_cap_c()

        return 0
    '''

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'all',
                'install',
                'prefix={}'.format(self.host_multiarch_dir),
                'exec_prefix={}'.format(self.host_multiarch_dir),
                'lib_prefix={}'.format(self.host_multiarch_dir),
                'inc_prefix={}'.format(self.host_multiarch_dir),
                'man_prefix={}'.format(self.host_multiarch_dir),
                'DESTDIR={}'.format(self.dst_dir),
                'RAISE_SETFCAP=no',
                'PAM_CAP=yes',
                'SYSTEM_HEADERS={}'.format(
                    os.path.join(
                        self.host_multiarch_dir,
                        'include'
                        )
                    ),
                'CFLAGS=-I{}'.format(
                    os.path.join(
                        self.host_multiarch_dir,
                        'include'
                        )
                    )
                ] + self.all_automatic_flags_as_list(),
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):

        wayround_org.utils.file.copytree(
            os.path.join(
                self.dst_host_multiarch_dir,
                'multiarch'
                ),
            os.path.join(
                self.dst_host_multiarch_dir,
                'lib'
                ),
            overwrite_files=True,
            clear_before_copy=False,
            dst_must_be_empty=True,
            )

        shutil.rmtree(
            os.path.join(
                self.dst_host_multiarch_dir,
                'multiarch'
                )
            )

        return 0
