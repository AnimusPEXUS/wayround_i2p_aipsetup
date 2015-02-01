
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
            ['extract', 'bootstrap', 'build_and_distribute'],
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

        python = 'python2'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'bootstrap' in actions and ret == 0:
            ret = subprocess.Popen(
                [python,
                 'bootstrap.py',
                 os.path.join(src_dir, 'build', 'scons')
                 ],
                cwd=src_dir
                ).wait()

        if 'build_and_distribute' in actions and ret == 0:
            ret = subprocess.Popen(
                [python,
                 'setup.py',
                 'install',
                 '--prefix=' + os.path.join(dst_dir, 'usr')
                 ],
                cwd=os.path.join(src_dir, 'build', 'scons')
                ).wait()

    return ret
