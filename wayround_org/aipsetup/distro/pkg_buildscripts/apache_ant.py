
import logging
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.path
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
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

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        src_ant_dir = wayround_org.utils.path.join(
            src_dir,
            'apache-ant-{}'.format(
                pkg_info['pkg_nameinfo']['groups']['version']
                )
            )

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        dst_ant_dir = wayround_org.utils.path.join(
            dst_dir, 'usr', 'lib', 'java', 'apache-ant'
            )

        etc_dir = os.path.join(dst_dir, 'etc', 'profile.d', 'SET')

        apacheant009 = os.path.join(etc_dir, '009.apache-ant')

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
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

            wayround_org.utils.file.copytree(
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
