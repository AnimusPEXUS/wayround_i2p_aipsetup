
import glob
import logging
import os.path
import shutil

import org.wayround.utils.file

import org.wayround.aipsetup.build
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


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

        separate_build_dir = False

        source_configure_reldir = 'wpa_supplicant'

        src_dir_p_sep = os.path.join(src_dir, source_configure_reldir)

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

            shutil.copyfile(
                os.path.join(src_dir_p_sep, 'defconfig'),
                os.path.join(src_dir_p_sep, '.config')
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[
                    'LIBDIR=/usr/lib',
                    'BINDIR=/usr/bin',
                    'PN531_PATH=/usr/src/nfc'
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'LIBDIR=/usr/lib',
                    'BINDIR=/usr/bin',
                    'PN531_PATH=/usr/src/nfc',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

            logging.info("Copying manuals")
            os.makedirs(os.path.join(dst_dir, 'usr', 'man', 'man8'))
            os.makedirs(os.path.join(dst_dir, 'usr', 'man', 'man5'))

            m8 = glob.glob(os.path.join(src_dir_p_sep, 'doc', 'docbook', '*.8'))
            m5 = glob.glob(os.path.join(src_dir_p_sep, 'doc', 'docbook', '*.5'))

            for i in m8:
                bn = os.path.basename(i)
                shutil.copyfile(i, os.path.join(dst_dir, 'usr', 'man', 'man8', bn))
                print(i)

            for i in m5:
                bn = os.path.basename(i)
                shutil.copyfile(i, os.path.join(dst_dir, 'usr', 'man', 'man5', bn))
                print(i)

    return ret
