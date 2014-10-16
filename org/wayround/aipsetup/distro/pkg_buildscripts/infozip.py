
import logging
import os.path
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
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