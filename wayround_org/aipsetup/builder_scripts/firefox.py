
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'configure', 'build', 'distribute'
             ],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        self.package_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = True

        source_configure_reldir = '.'

        if 'extract' in actions and ret == 0:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                if wayround_org.utils.file.cleanup_dir(src_dir) != 0:
                    logging.error("Some error while cleaning up source dir")
                    ret = 1

            if ret == 0:

                ret = autotools.extract_high(
                    buildingsite,
                    self.package_info['pkg_info']['basename'],
                    unwrap_dir=True,
                    rename_dir=False
                    )

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-application=browser',
                    '--enable-default-toolkit=cairo-gtk3',
                    '--enable-freetype2',
                    '--enable-shared',
#                    '--enable-shared-js',
                    '--enable-xft',
                    '--with-pthreads',
                    '--enable-webrtc',
                    '--enable-optimize', # -O3 -fno-keep-inline-dllexport
                    '--enable-gstreamer=1.0',
                    '--with-system-nspr',
                    '--with-system-nss',
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
                    '--mandir=' + self.package_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        self.package_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        self.package_info['constitution']['paths']['var'],
                    '--host=' + self.package_info['constitution']['host'],
                    '--build=' + self.package_info['constitution']['build']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir,
                script_name='configure',
                run_script_not_bash=True,
                relative_call=True
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

    return ret
