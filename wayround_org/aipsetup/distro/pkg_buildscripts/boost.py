
import logging
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'bootstrap', 'build', 'distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

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

        if 'bootstrap' in actions and ret == 0:
            ret = subprocess.Popen(
                [
                 'bash',
                 './bootstrap.sh',
                 '--prefix=/usr',
#                 '--with-python-version=3.3'
                 ],
                cwd=src_dir
                ).wait()

        if 'build' in actions and ret == 0:

            log = wayround_org.utils.log.Log(
                wayround_org.aipsetup.build.getDIR_BUILD_LOGS(buildingsite),
                'build'
                )

            p = subprocess.Popen(
                [
                    os.path.join(src_dir, 'bjam'),
                    '--prefix=' + os.path.join(
                        wayround_org.aipsetup.build.getDIR_DESTDIR(
                            buildingsite
                            ),
                        'usr'
                        ),
#                    '--build-type=complete',
#                    '--layout=versioned',
                    'threading=multi',
                    'link=shared',
                    'stage',
                    ],
                    cwd=src_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    )

            wayround_org.utils.log.process_output_logger(p, log)

            p.wait()

            log.stop()

        if 'distribute' in actions and ret == 0:
            ret = subprocess.Popen(
                [
                    os.path.join(src_dir, 'bjam'),
                    '--prefix=' + os.path.join(
                        wayround_org.aipsetup.build.getDIR_DESTDIR(
                            buildingsite
                            ),
                        'usr'
                        ),
#                    '--build-type=complete',
#                    '--layout=versioned',
                    'threading=multi',
                    'link=shared',
                    'install',
                    ],
                    cwd=src_dir
                    ).wait()

    return ret
