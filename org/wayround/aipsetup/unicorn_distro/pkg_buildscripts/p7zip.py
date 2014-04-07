
import logging
import os.path
import shutil
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute'],
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

        if 'configure' in actions and ret == 0:
            shutil.copy(
                os.path.join(src_dir, 'makefile.linux_any_cpu'),
                os.path.join(src_dir, 'makefile.machine')
                )

        if 'build' in actions and ret == 0:
            p = subprocess.Popen(['make', 'all3'], cwd=src_dir)
            ret = p.wait()

        if 'distribute' in actions and ret == 0:

            fn = os.path.join(src_dir, 'install.sh')

            f = open(fn)
            lines = f.read().splitlines()
            f.close()

            for i in range(len(lines)):

                if lines[i] == 'DEST_HOME=/usr/local':
                    lines[i] = 'DEST_HOME=/usr'

                if lines[i] == 'DEST_DIR=':
                    lines[i] = 'DEST_DIR={}'.format(dst_dir)

            f = open(fn, 'w')
            f.write('\n'.join(lines))
            f.close()

            p = subprocess.Popen(
                ['make',
                 'install',
                 'DEST_HOME=/usr',
                 'DEST_DIR={}'.format(dst_dir)
                 ],
                cwd=src_dir
                )
            ret = p.wait()

    return ret
