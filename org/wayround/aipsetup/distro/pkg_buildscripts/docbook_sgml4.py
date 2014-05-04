
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.utils.archive


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        tar_dir = org.wayround.aipsetup.build.getDIR_TARBALL(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        if 'distribute' in actions and ret == 0:

            zip_file = os.listdir(tar_dir)

            xml_dir = os.path.join(dst_dir, 'usr', 'share', 'sgml', 'docbook')

            if not len(zip_file) == 1:
                ret = 1
                logging.error("zip file not found")
            else:
                zip_file = zip_file[0]

                os.makedirs(xml_dir)

                org.wayround.utils.archive.extract(
                    os.path.join(tar_dir, zip_file),
                    os.path.join(
                        xml_dir, 'docbook' + '-' +
                        pkg_info['pkg_nameinfo']['groups']['version']
                        )
                    )

    return ret
