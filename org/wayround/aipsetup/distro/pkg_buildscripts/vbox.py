
import logging
import os.path
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute', 'copydist', 'SET'],
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

        etc_profile_set_dir = org.wayround.utils.path.join(
            dst_dir, 'etc', 'profile.d', 'SET'
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

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--disable-docs',
                    '--disable-java',
                    '--with-qt-dir=/usr/lib/qt4_w_toolkit',
#                    '--disable-hardening',
#                    '--out-path={}'.format(dst_dir)
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir,
                script_name='configure',
                run_script_not_bash=False,
                relative_call=False
                )

        if 'build' in actions and ret == 0:
            os.chmod(org.wayround.utils.path.join(src_dir, 'env.sh'), 0o755)
            p = subprocess.Popen(
                ['bash',
                 '-c',
                 '. ./env.sh ; kmk VBOX_PATH_APP_PRIVATE=/usr/lib/virtualbox'
                 ],
                cwd=src_dir
                )

            ret = p.wait()

        if 'distribute' in actions and ret == 0:
            os.chmod(org.wayround.utils.path.join(src_dir, 'env.sh'), 0o755)
            p = subprocess.Popen(
                ['bash',
                 '-c',
                 '. ./env.sh ; kmk install VBOX_PATH_APP_PRIVATE=/usr/lib/virtualbox'.format(
                    org.wayround.utils.path.relpath(dst_dir, src_dir)
                    )
                 ],
                cwd=src_dir
                )

            ret = p.wait()

        if 'copydist' in actions and ret == 0:

            work_dir = src_dir

            p = org.wayround.utils.path.join(work_dir, 'out')
            if os.path.isdir(p):
                work_dir = p

            dirs = os.listdir(p)

            errors = 0
            copied_something = False

            for i in dirs:

                work_dir = org.wayround.utils.path.join(
                    p, i, 'release', 'dist'
                    )

                if os.path.isdir(work_dir):

                    logging.info("Copying {}".format(work_dir))

                    res = org.wayround.utils.file.copytree(
                        work_dir,
                        org.wayround.utils.path.join(
                            dst_dir, 'usr', 'lib', 'virtualbox'
                            ),
                        overwrite_files=True,
                        clear_before_copy=False,
                        dst_must_be_empty=False
                        )

                    if res != 0:
                        errors += 1

                    copied_something = True
                else:
                    logging.error("`{}' not dir".format(work_dir))

            ret = int(errors > 0 or not copied_something)

            if ret != 0:
                logging.error("Some error copying dist tree")

        if 'SET' in actions and ret == 0:
            try:
                os.makedirs(etc_profile_set_dir)
            except:
                logging.error(
                    "Can't create dir: {}".format(etc_profile_set_dir)
                    )

            f = open(
                org.wayround.utils.path.join(
                    etc_profile_set_dir,
                    '009.virtualbox'
                    ),
                'w'
                )

            f.write("""\
#!/bin/bash
export PATH=$PATH:/usr/lib/virtualbox/bin
""")
            f.close()

    return ret
