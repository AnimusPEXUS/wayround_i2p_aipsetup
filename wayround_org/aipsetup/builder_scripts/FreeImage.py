
import glob
import logging
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
                'CC={}-gcc'.format(self.host),
                'CXX={}-g++'.format(self.host),
                'DESTDIR={}'.format(self.host_multiarch_dir),
                'INCDIR={}'.format(
                    wayround_org.utils.path.join(
                        self.host_multiarch_dir,
                        'include'
                        )
                    ),
                'INSTALLDIR={}'.format(
                    wayround_org.utils.path.join(
                        self.host_multiarch_dir,
                        'lib'
                        )
                    )
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = 0

        os.makedirs(
            os.path.join(self.dst_host_multiarch_dir, 'include'),
            exist_ok=True
            )

        os.makedirs(
            os.path.join(self.dst_host_multiarch_dir, 'lib'),
            exist_ok=True
            )

        if ret == 0:

            libs = glob.glob(os.path.join(self.src_dir, 'Dist', '*.a'))
            libs += glob.glob(os.path.join(self.src_dir, 'Dist', '*.so'))

            headers = glob.glob(os.path.join(self.src_dir, 'Dist', '*.h'))

            for i in libs:
                i = os.path.basename(i)
                shutil.copy(
                    os.path.join(self.src_dir, 'Dist', i),
                    os.path.join(self.dst_host_multiarch_dir, 'lib', i)
                    )

            for i in headers:
                i = os.path.basename(i)
                shutil.copy(
                    os.path.join(self.src_dir, 'Dist', i),
                    os.path.join(self.dst_host_multiarch_dir, 'include', i)
                    )

        return
