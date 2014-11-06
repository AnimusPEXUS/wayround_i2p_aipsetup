
import logging
import os.path
import subprocess
import shutil

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.path
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        src_build_dir = org.wayround.utils.path.join(
            src_dir,
            'build'
            )

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        dst_classpath_dir = org.wayround.utils.path.join(
            dst_dir, 'usr', 'lib', 'java', 'classpath'
            )

        separate_build_dir = False

        source_configure_reldir = '.'

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

        if 'build' in actions and ret == 0:
            build_target = []
            # if pkg_info['pkg_nameinfo']['groups']['version'] == '1.3':
            #     build_target = []
            p = subprocess.Popen(
                [
                    'ant',
                    '-Dversion={}'.format(
                        pkg_info['pkg_nameinfo']['groups']['version']
                        )
                    ] + build_target,
                cwd=src_dir
                )
            ret = p.wait()

        if 'distribute' in actions and ret == 0:
            try:
                os.makedirs(dst_classpath_dir)
            except:
                pass

            shutil.copy(
                org.wayround.utils.path.join(
                    src_build_dir, 'hamcrest-all-{}.jar'.format(
                        pkg_info['pkg_nameinfo']['groups']['version']
                        )
                    ),
                dst_classpath_dir
                )

    return ret
