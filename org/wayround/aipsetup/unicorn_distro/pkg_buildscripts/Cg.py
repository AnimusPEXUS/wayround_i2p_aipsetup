
import logging
import os.path
import shutil

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
                unwrap_dir=True,
                rename_dir=False
                )

        if 'distribute' in actions and ret == 0:
            try:
                os.mkdir(os.path.join(dst_dir, 'usr'), mode=0o755)
            except:
                logging.exception("Error making usr dir in dist")
                ret = 4
            else:

                for i in ['bin', 'include', 'lib']:
                    if ret != 0:
                        break

                    try:
                        shutil.move(
                            os.path.join(src_dir, i),
                            os.path.join(dst_dir, 'usr')
                            )
                    except:
                        logging.exception(
                            "Error moving `{}' dir into dist".format(i)
                            )
                        ret = 5

    return ret
