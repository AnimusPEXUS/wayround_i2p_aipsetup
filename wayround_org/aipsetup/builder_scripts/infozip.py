
import logging
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'build', 'distribute'],
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
            p = subprocess.Popen(
                ['make',
                 '-f', 'unix/Makefile',
                 'generic',
                 'CFLAGS=" -march=i486 -mtune=i486 "'
                 ],
                cwd=src_dir
                )
            ret = p.wait()

        if 'distribute' in actions and ret == 0:
            p = subprocess.Popen(
                ['make',
                 '-f', 'unix/Makefile',
                 'install',
                 'prefix={}/usr'.format(dst_dir)
                 ],
                cwd=src_dir
                )
            ret = p.wait()

    return ret
