
import logging
import os.path
import subprocess

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

        src_ant_dir = org.wayround.utils.path.join(
            src_dir,
            'apache-ant-{}'.format(
                pkg_info['pkg_nameinfo']['groups']['version']
                )
            )

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        dst_ant_dir = org.wayround.utils.path.join(
            dst_dir, 'usr', 'lib', 'java', 'apache-ant'
            )

        etc_dir = os.path.join(dst_dir, 'etc', 'profile.d', 'SET')

        apacheant009 = os.path.join(etc_dir, '009.apache-ant')

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
            p = subprocess.Popen(
                [
                    'ant',
                    '-Dversion={}'.format(
                        pkg_info['pkg_nameinfo']['groups']['version']
                        ),
                    # '-lib', '/usr/lib/java/classpath',
                    'dist'
                    ],
                cwd=src_dir
                )
            ret = p.wait()

        if 'distribute' in actions and ret == 0:
            try:
                os.makedirs(dst_ant_dir)
            except:
                pass

            org.wayround.utils.file.copytree(
                src_ant_dir,
                dst_ant_dir,
                overwrite_files=True,
                clear_before_copy=True,
                dst_must_be_empty=True
                )

            os.makedirs(etc_dir, exist_ok=True)

            fi = open(apacheant009, 'w')

            fi.write(
                """\
#!/bin/bash
export ANT_HOME='/usr/lib/java/apache-ant'
export PATH="$PATH:$ANT_HOME/bin"
"""
                )

            fi.close()

    return ret
