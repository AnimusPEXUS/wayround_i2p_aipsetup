
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

        pkg_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
            ret = autotools.extract_high(
                buildingsite,
                pkg_info['pkg_info']['basename'],
                unwrap_dir=False,
                rename_dir=False,
                more_when_one_extracted_ok=True
                )

        if 'distribute' in actions and ret == 0:

            os.makedirs(os.path.join(dst_dir, 'usr', 'include', 'rpc'))
            os.makedirs(os.path.join(dst_dir, 'usr', 'include', 'rpcsvc'))

            wayround_org.utils.file.copytree(
                os.path.join(src_dir, 'rpc'),
                os.path.join(dst_dir, 'usr', 'include', 'rpc'),
                dst_must_be_empty=False
                )

            wayround_org.utils.file.copytree(
                os.path.join(src_dir, 'rpcsvc'),
                os.path.join(dst_dir, 'usr', 'include', 'rpcsvc'),
                dst_must_be_empty=False
                )

    return ret
