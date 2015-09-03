

import os.path
import subprocess
import glob
import shutil

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std
import wayround_org.utils.file


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_compilers_options = True
        return

    def define_actions(self):
        ret = super().define_actions()
        del ret['configure']
        del ret['autogen']
        del ret['build']
        #ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    '''
    def patch_test_c(self):
        name = wayround_org.utils.path.join(self.get_src_dir(), 'pam_cap', 'test.c')

        with open(name) as f:
            t = f.read()

        t = t.replace('<security/', '<')

        with open(name, 'w') as f:
            f.write(t)

        return 0

    def patch_pam_cap_c(self):
        name = wayround_org.utils.path.join(self.get_src_dir(), 'pam_cap', 'pam_cap.c')

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

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'all',
            'install',
            'prefix={}'.format(self.calculate_install_prefix()),
            #'exec_prefix={}'.format(self.get_host_dir()),
            #'lib_prefix={}'.format(self.get_host_dir()),
            #'inc_prefix={}'.format(self.get_host_dir()),
            #'man_prefix={}'.format(self.get_host_dir()),
            'DESTDIR={}'.format(self.get_dst_dir()),
            #'PKGCONFIGDIR={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_dst_host_dir(),
            #       'lib',
            #        'pkgconfig'
            #        )
            #    ),
            'RAISE_SETFCAP=no',
            'PAM_CAP=yes',
            #'SYSTEM_HEADERS={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        'include'
            #        )
            #    ),
            #'CFLAGS=-I{}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_host_dir(),
            #        'include'
            #        )
            #    )
            ] + self.all_automatic_flags_as_list()

    def builder_action_after_distribute(self, called_as, log):

        raise Exception("tests required")

        wayround_org.utils.file.copytree(
            wayround_org.utils.path.join(
                self.get_dst_host_dir(),
                'multiarch'
                ),
            wayround_org.utils.path.join(
                self.get_dst_host_dir(),
                'lib' #self.calculate_main_multiarch_lib_dir_name()
                ),
            overwrite_files=True,
            clear_before_copy=False,
            dst_must_be_empty=True,
            )

        shutil.rmtree(
            wayround_org.utils.path.join(
                self.get_dst_host_dir(),
                'multiarch'
                )
            )

        return 10
