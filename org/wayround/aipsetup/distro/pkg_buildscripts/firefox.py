
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract',
             'configure', 'build', 'distribute'
             ],
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

        separate_build_dir_xul = True

        source_configure_reldir = '.'

        if 'extract' in actions and ret == 0:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                if org.wayround.utils.file.cleanup_dir(src_dir) != 0:
                    logging.error("Some error while cleaning up source dir")
                    ret = 1

            if ret == 0:

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
                    '--enable-application=browser',
                    '--enable-default-toolkit=cairo-gtk2',
                    '--enable-freetype2',
                    '--enable-shared',
#                    '--enable-shared-js',
                    '--enable-xft',
                    '--with-pthreads',
                    '--disable-webrtc',
                    '--disable-optimize',
                    '--with-system-nspr',
                    '--with-system-nss',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        pkg_info['constitution']['paths']['var'],
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir_xul,
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
                use_separate_buildding_dir=separate_build_dir_xul,
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
                use_separate_buildding_dir=separate_build_dir_xul,
                source_configure_reldir=source_configure_reldir
                )

    return ret
