
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


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
                    # '--enable-cogl',
                    '--enable-directfb=auto',
                    # '--enable-drm',
                    '--enable-fc=auto',
                    '--enable-ft=auto',
                    '--enable-gl',
                    '--enable-gallium=auto',
#                    '--enable-glesv2',
                    '--enable-pdf=yes',
                    '--enable-png=yes',
                    '--enable-ps=yes',
#                    '--enable-qt',
                    '--enable-quartz-font=auto',
                    '--enable-quartz-image=auto',
                    '--enable-quartz=auto',
                    '--enable-script=yes',
                    '--enable-svg=yes',
                    '--enable-tee=yes',
                    '--enable-vg',
                    '--enable-wg=auto',
                    '--enable-xcb',
                    '--enable-xcb-shm',

                    '--enable-egl',
                    '--enable-glx',
                    # '--enable-wgl',

                    # xlib is deprecated
#                    '--enable-xlib',
#                    '--enable-xlib-xcb',
#                    '--enable-xlib-xrender',

                    '--disable-static',
                    '--enable-xml=yes',

                    '--with-x',

                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
#                    '--target=' + pkg_info['constitution']['target']
                    ],
                arguments=[],
                environment={
                    # 'CFLAGS': ' -ffat-lto-objects '
                    },
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

    return ret
