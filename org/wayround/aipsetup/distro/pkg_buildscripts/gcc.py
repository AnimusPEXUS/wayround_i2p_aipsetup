
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
        ['extract', 'configure', 'build',
         'before_checks', 'checks', 'distribute'],
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
        cc_file = os.path.join(dst_dir, 'usr', 'bin', 'cc')

        libcpp_file = os.path.join(dst_dir, 'usr', 'lib', 'cpp')

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
                    # experimental options
                    # '--enable-targets=all',
                    '--enable-tls',
                    '--enable-nls',

                    '--disable-lto',

                    # normal options
                    '--enable-__cxa_atexit',
                    '--with-arch-32=i486',
                    '--with-tune=generic',
                    '--enable-languages=all,go,objc,obj-c++,ada',
                    '--enable-bootstrap',
                    '--enable-threads=posix',
                    '--enable-multiarch',
                    '--enable-multilib',
                    '--enable-checking=release',
                    '--with-gmp=/usr',
                    '--with-mpfr=/usr',
                    # '--with-build-time-tools=
                    # /home/agu/_sda3/_UNICORN/b/gnat/
                    # gnat-gpl-2014-x86-linux-bin',
                    '--enable-shared',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    '--target=' + pkg_info['constitution']['target']
                    ],
                arguments=[],
                environment={
                    # 'CC': '/home/agu/_sda3/_UNICORN/b/gnat/
                    #  gnat-gpl-2014-x86-linux-bin/bin/gcc',
                    # 'CXX': '/home/agu/_sda3/_UNICORN/b/
                    # gnat/gnat-gpl-2014-x86-linux-bin/bin/g++',
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

        if 'before_checks' in actions and ret == 0:
            print(
                "stop: checks! If You want them (it's good if You do)\n"
                "then continue build with command: aipsetup3 build continue checks+\n"
                "else continue build with command: aipsetup3 build continue distribute+\n"
                )
            ret = 1

        if 'checks' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=['-k'],
                arguments=['check'],
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

            if not os.path.exists(cc_file):
                os.symlink('gcc', cc_file)

            if (not os.path.exists(libcpp_file)
                    and not os.path.islink(libcpp_file)):
                os.symlink('../bin/cpp', libcpp_file)

    return ret
