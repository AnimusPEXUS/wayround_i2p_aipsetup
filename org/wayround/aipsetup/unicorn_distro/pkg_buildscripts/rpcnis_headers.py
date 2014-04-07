
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
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

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                org.wayround.utils.file.cleanup_dir(src_dir)
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

            org.wayround.utils.file.copytree(
                os.path.join(src_dir, 'rpc'),
                os.path.join(dst_dir, 'usr', 'include', 'rpc'),
                dst_must_be_empty=False
                )

            org.wayround.utils.file.copytree(
                os.path.join(src_dir, 'rpcsvc'),
                os.path.join(dst_dir, 'usr', 'include', 'rpcsvc'),
                dst_must_be_empty=False
                )

    return ret
