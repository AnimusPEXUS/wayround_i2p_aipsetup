
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
        ['extract', 'patch', 'configure', 'build', 'distribute', 'ln'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)
        patch_dir = org.wayround.aipsetup.build.getDIR_PATCHES(buildingsite)
        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

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

        if 'patch' in actions and ret == 0:
            patches = os.listdir(patch_dir)

            if len(patches) == 0:
                print("provide patches")
                ret = 30
            else:

                patches2 = []

                for i in patches:
                    if not i.endswith('.sig'):
                        patches2.append(i)

                patches = patches2
                del patches2

                patches.sort()

                for i in patches:
                    logging.info("Patching using {}".format(i))
                    if subprocess.Popen(
                            ['patch',
                             '-i',
                             patch_dir + os.path.sep + i,
                             '-p0'],
                            cwd=src_dir
                            ).wait() != 0:
                        logging.error("Patch error")
                        ret = 1

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-multibyte',
                    '--with-curses',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    '--target=' + pkg_info['constitution']['target']
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
            ret = autotools.make_high(
                buildingsite,
                options=[],
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
                    'DESTDIR=' + (
                        org.wayround.aipsetup.build.getDIR_DESTDIR(
                            buildingsite
                            )
                        )
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'ln' in actions and ret == 0:

            tsl = org.wayround.utils.path.join(dst_dir, 'usr', 'bin', 'sh')

            if os.path.exists(tsl) or os.path.islink(tsl):
                os.unlink(tsl)

            os.symlink('bash', tsl)

    return ret
