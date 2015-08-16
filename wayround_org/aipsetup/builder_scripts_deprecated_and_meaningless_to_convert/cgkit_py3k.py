
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        [
            'extract', 'scons', 'distribute'
            ],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                log.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'scons' in actions and ret == 0:

            ret = subprocess.Popen(
                ['scons'],
                cwd=wayround_org.utils.path.join(src_dir, 'supportlib')
                ).wait()

        if 'distribute' in actions and ret == 0:
            ret = subprocess.Popen(
                ['python3', 'setup.py', 'install',
                 '--root={}'.format(wayround_org.utils.path.join(dst_dir))],
                cwd=src_dir
                ).wait()

    return ret
