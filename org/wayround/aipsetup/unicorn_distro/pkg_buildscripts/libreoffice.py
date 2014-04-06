
import glob
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute', 'afterdistribute'],
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
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--disable-gtk',
                    '--without-junit',
#                    '--with-system-headers',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
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
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'afterdistribute' in actions and ret == 0:

            gid = glob.glob(org.wayround.utils.path.join(dst_dir, 'gid*'))

            lbo_dir = org.wayround.utils.path.join(
                dst_dir, 'usr', 'lib', 'libreoffice'
                )
            gid_dir = org.wayround.utils.path.join(lbo_dir, 'gid')
            lbo_lnk = org.wayround.utils.path.join(
                dst_dir, 'usr', 'bin', 'soffice'
                )

            try:
                os.makedirs(gid_dir)
            except:
                pass

            if not os.path.isdir(gid_dir):
                ret = 3
                logging.error(
                    "Can't create required dir: `{}'".format(gid_dir)
                    )

            else:
                logging.info("Moving gid* files")
                for i in gid:
                    os.rename(
                        i,
                        org.wayround.utils.path.join(
                            gid_dir, os.path.basename(i)
                            )
                        )

                logging.info("Creating link")
                os.makedirs(
                    org.wayround.utils.path.join(dst_dir, 'usr', 'bin')
                    )
                os.symlink(
                    org.wayround.utils.path.relpath(
                        org.wayround.utils.path.join(
                            lbo_dir, 'program', 'soffice'
                            ),
                        os.path.dirname(lbo_lnk)
                        ),
                    lbo_lnk
                    )

    return ret
