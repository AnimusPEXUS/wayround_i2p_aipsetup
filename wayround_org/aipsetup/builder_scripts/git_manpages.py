
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'distribute'],
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

        man_dir = os.path.join(dst_dir, 'usr', 'share', 'man')

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                self.package_info['pkg_info']['basename'],
                unwrap_dir=False,
                rename_dir=False,
                more_when_one_extracted_ok=True
                )

        if 'distribute' in actions and ret == 0:

            mans = os.listdir(src_dir)

            for i in mans:

                m = os.path.join(man_dir, i)
                sm = os.path.join(src_dir, i)

                os.makedirs(m)

                wayround_org.utils.file.copytree(
                    src_dir=sm,
                    dst_dir=m,
                    overwrite_files=True,
                    clear_before_copy=False,
                    dst_must_be_empty=False
                    )

    return ret
