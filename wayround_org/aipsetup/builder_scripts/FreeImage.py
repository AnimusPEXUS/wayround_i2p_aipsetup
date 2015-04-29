
import glob
import logging
import os.path
import shutil
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'build', 'dist'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        self.package_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                self.package_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'build' in actions and ret == 0:
            ret = subprocess.Popen(
                ['make'],
                cwd=src_dir
                )

        if 'dist' in actions and ret == 0:

            try:
                os.makedirs(
                    os.path.join(dst_dir, 'usr', 'include')
                    )
            except:
                pass

            try:
                os.makedirs(
                    os.path.join(dst_dir, 'usr', 'lib')
                    )
            except:
                pass

            libs = glob.glob(os.path.join(src_dir, 'Dist', '*.a'))
            libs += glob.glob(os.path.join(src_dir, 'Dist', '*.so'))

            headers = glob.glob(os.path.join(src_dir, 'Dist', '*.h'))

            for i in libs:
                i = os.path.basename(i)
                shutil.copy(
                    os.path.join(src_dir, 'Dist', i),
                    os.path.join(dst_dir, 'usr', 'lib', i)
                    )

            for i in headers:
                i = os.path.basename(i)
                shutil.copy(
                    os.path.join(src_dir, 'Dist', i),
                    os.path.join(dst_dir, 'usr', 'include', i)
                    )

#            ret = subprocess.Popen(
#                ['make', 'install', 'DESTDIR=' + dst_dir],
#                cwd=src_dir
#                )

    return ret
