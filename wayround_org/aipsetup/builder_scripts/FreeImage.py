
import glob
import os.path
import shutil
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std

import wayround_org.utils.file
import wayround_org.utils.path


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = True
        return

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            [
                'make',
                'DESTDIR={}'.format(self.calculate_install_prefix()),
                #'INCDIR={}'.format(
                #    wayround_org.utils.path.join(
                #        self.get_host_dir(),
                #        'include'
                #        )
                #    ),
                #'INSTALLDIR={}'.format(
                #    wayround_org.utils.path.join(
                #        self.get_host_dir(),
                #	'lib'
                #        #self.calculate_main_multiarch_lib_dir_name()
                #        )
                #    )
                ] + self.all_automatic_flags_as_list(),
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = 0

        os.makedirs(
            wayround_org.utils.path.join(
                self.calculate_dst_install_prefix(),
                'include'
                ),
            exist_ok=True
            )

        os.makedirs(
            wayround_org.utils.path.join(
                self.calculate_dst_install_libdir(),
                ),
            exist_ok=True
            )

        if ret == 0:

            libs = glob.glob(wayround_org.utils.path.join(
                self.get_src_dir(), 'Dist', '*.a')
                )
            libs += glob.glob(wayround_org.utils.path.join(
                self.get_src_dir(), 'Dist', '*.so')
                )

            headers = glob.glob(wayround_org.utils.path.join(
                self.get_src_dir(), 'Dist', '*.h')
                )

            for i in libs:
                i = os.path.basename(i)
                shutil.copy(
                    wayround_org.utils.path.join(
                        self.get_src_dir(), 'Dist', i
                        ),
                    wayround_org.utils.path.join(
                        self.calculate_dst_install_libdir(),
                        i
                        )
                    )

            for i in headers:
                i = os.path.basename(i)
                shutil.copy(
                    wayround_org.utils.path.join(
                        self.get_src_dir(), 'Dist', i
                        ),
                    wayround_org.utils.path.join(
                        self.calculate_dst_install_prefix(), 'include', i
                        )
                    )

        return
