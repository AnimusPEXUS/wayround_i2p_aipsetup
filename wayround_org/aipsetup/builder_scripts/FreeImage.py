
import glob
import logging
import os.path
import shutil
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file
import wayround_org.aipsetup.builder_scripts.std


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

    def builder_action_build(self, log):
        p = subprocess.Popen(
            ['make'],
            cwd=self.src_dir
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, log):
        ret = 0

        try:
            os.makedirs(
                os.path.join(self.dst_dir, 'usr', 'include'),
                exist_ok=True
                )
        except:
            log.exception("Can't create dir")
            ret = 2

        try:
            os.makedirs(
                os.path.join(self.dst_dir, 'usr', 'lib'),
                exist_ok=True
                )
        except:
            log.exception("Can't create dir")
            ret = 2

        if ret == 0:

            libs = glob.glob(os.path.join(self.src_dir, 'Dist', '*.a'))
            libs += glob.glob(os.path.join(self.src_dir, 'Dist', '*.so'))

            headers = glob.glob(os.path.join(self.src_dir, 'Dist', '*.h'))

            for i in libs:
                i = os.path.basename(i)
                shutil.copy(
                    os.path.join(self.src_dir, 'Dist', i),
                    os.path.join(self.dst_dir, 'usr', 'lib', i)
                    )

            for i in headers:
                i = os.path.basename(i)
                shutil.copy(
                    os.path.join(self.src_dir, 'Dist', i),
                    os.path.join(self.dst_dir, 'usr', 'include', i)
                    )

        return
