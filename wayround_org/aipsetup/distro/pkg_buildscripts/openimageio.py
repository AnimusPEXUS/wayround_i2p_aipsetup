
import logging
import os.path

import wayround_org.aipsetup.build
from wayround_org.aipsetup.buildtools import autotools
from wayround_org.aipsetup.buildtools import cmake
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'cmake', 'build', 'distribute'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = True

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

        if 'cmake' in actions and ret == 0:
            ret = cmake.cmake_high(
                buildingsite,
                options=[
                    '-DCMAKE_INSTALL_PREFIX=' +
                        pkg_info['constitution']['paths']['usr'],
                    '-DSTOP_ON_WARNING=OFF',
#                    '-DCMAKE_SYSTEM_PROCESSOR=i486',
#                    '-DCMAKE_LIBRARY_ARCHITECTURE=i486',
#                    '-DCMAKE_HOST_SYSTEM_PROCESSOR=i486',
                    '-DCMAKE_CXX_FLAGS= -march=i686 -mtune=i686 ',
                    '-DCMAKE_C_FLAGS= -march=i686 -mtune=i686 ',
#                    '-DCMAKE_LIBRARY_ARCHITECTURE=i486',
#                    '--mandir=' + pkg_info['constitution']['paths']['man'],
#                    '--sysconfdir=' +
#                        pkg_info['constitution']['paths']['config'],
#                    '--localstatedir=' +
#                        pkg_info['constitution']['paths']['var'],
#                    '--enable-shared',
#                    '--host=' + pkg_info['constitution']['host'],
#                    '--build=' + pkg_info['constitution']['build'],
#                    '--target=' + pkg_info['constitution']['target']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_subdir=source_configure_reldir,
                build_in_separate_dir=separate_build_dir
                )

        if 'build' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[
                    ],
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
