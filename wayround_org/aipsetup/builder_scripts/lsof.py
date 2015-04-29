
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
        ['extract', 'configure', 'build', 'distribute'],
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

        tar_dir = None
        lsof_file = None
        lsof_man_file = None

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

            tar = None

            for i in os.listdir(src_dir):
                if i.endswith('.tar'):
                    tar = i
                    break

            if tar == None:
                logging.error(".tar not found in 00.SOURCE")
                ret = 1
            else:

                tar_dir = tar[:-len('.tar')]

                logging.info("Unpacking {}".format(tar))
                p = subprocess.Popen(['tar', '-xf', tar], cwd=src_dir)

                p_r = p.wait()

                if p_r != 0:
                    logging.error("Error `{}' while untarring".format(p_r))
                    ret = 1
                else:
                    if not tar_dir in os.listdir(src_dir):
                        logging.error("wrong tarball")
                        ret = 1
                    else:
                        tar_dir = os.path.join(src_dir, tar_dir)
                        lsof_file = os.path.join(tar_dir, 'lsof')
                        lsof_man_file = os.path.join(tar_dir, 'lsof.8')

        if 'configure' in actions and ret == 0:
            p = subprocess.Popen(['./Configure', '-n', 'linux'], cwd=tar_dir)
            ret = p.wait()

        if 'build' in actions and ret == 0:
            p = subprocess.Popen(['make'], cwd=tar_dir)
            ret = p.wait()

        if 'distribute' in actions and ret == 0:

            if not os.path.isfile(lsof_file):
                logging.error("Can't find lsof executable")
                ret = 1
            else:

                if not os.path.isfile(lsof_man_file):
                    logging.error("Can't find lsof.8 man file")
                    ret = 1
                else:
                    dst_bin_dir = os.path.join(dst_dir, 'usr', 'bin')

                    if not os.path.isdir(dst_bin_dir):
                        os.makedirs(dst_bin_dir)

                    shutil.copy(lsof_file, os.path.join(dst_bin_dir, 'lsof'))

                    dst_man_dir = os.path.join(
                        dst_dir, 'usr', 'share', 'man', 'man8'
                        )

                    if not os.path.isdir(dst_man_dir):
                        os.makedirs(dst_man_dir)

                    shutil.copy(
                        lsof_man_file, os.path.join(dst_man_dir, 'lsof.8')
                        )

    return ret
