
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
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

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        # TODO: add autoconf

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

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-texture-float',

                    '--enable-gles1',
                    '--enable-gles2',

                    '--enable-openvg=auto',

                    '--enable-osmesa',
                    '--with-osmesa-bits=32',

                    '--enable-xa',
                    '--enable-gbm',

                    #                    '--enable-egl',
                    '--enable-gallium-egl',
                    #                    '--enable-gallium-gbm',

                    '--enable-dri',
                    '--enable-dri3',

                    #                    '--enable-glx-tls',

                    '--enable-xorg',
                    '--with-egl-platforms=x11,drm,wayland,fbdev,null',
                    '--with-gallium-drivers=nouveau,svga,swrast',
                    '--with-dri-drivers=nouveau,i915,i965,r200,radeon,swrast',

                    #                    '--enable-d3d1x',
                    #                    '--enable-opencl',

                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    #                    '--host=i686-pc-linux-gnu',
                    #                    '--target=' + pkg_info['constitution']['target']
                    ],
                arguments=[],
                # environment={
                #     'CFLAGS': '-fno-lto'
                #     },
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
                        wayround_org.aipsetup.build.getDIR_DESTDIR(
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