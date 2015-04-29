
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
        ['extract', 'configure', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        self.package_info, actions = r

        num = self.package_info['pkg_info']['name'][-1]

        if num == '4':
            num = '2'
        elif num == '5':
            num = '3'
        else:
            raise Exception("Unsupported eric")

        python = 'python{}'.format(num)

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

        if 'distribute' in actions and ret == 0:
            ddd = wayround_org.utils.path.join(dst_dir)
            p = subprocess.Popen(
                [python, './install.py', '-i', ddd],
                cwd=src_dir
                )
            ret = p.wait()

    return ret
