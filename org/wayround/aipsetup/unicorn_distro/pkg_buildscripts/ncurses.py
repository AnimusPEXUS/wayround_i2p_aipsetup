#!/usr/bin/python

import os.path
import logging
import subprocess
import glob

import org.wayround.utils.file
import org.wayround.utils.archive

import org.wayround.aipsetup.build
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'patch', 'configure', 'build', 'distribute', 'links'],
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

        pth_dir = org.wayround.aipsetup.build.getDIR_PATCHES(buildingsite)

        dst_lib_dir = os.path.join(dst_dir, 'usr', 'lib')

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

            pth_files = os.listdir(pth_dir)

            rolling = None

            patches = []

            for i in pth_files:
                if i.find('-patch.sh.') != -1 and not i.endswith('.asc'):
                    rolling = i
                    break

            for i in pth_files:
                if i.find('.patch.') != -1 and not i.endswith('.asc'):
                    patches.append(i)

            patches.sort()

            if rolling:

                compressor = (
                    org.wayround.utils.archive.determine_compressor_by_filename(
                        rolling
                        )
                    )

                p = subprocess.Popen([compressor, '-d', rolling], cwd=pth_dir)
                if p.wait() != 0:

                    ret = 1

                else:
                    rolling = rolling[
                        0:
                        - len(
                            org.wayround.utils.archive.determine_extension_by_filename(rolling)
                            )
                        ]

                    p = subprocess.Popen(['bash', os.path.join(pth_dir, rolling)], cwd=src_dir)
                    p.wait()


            if ret == 0:

                for i in patches:

                    compressor = (
                        org.wayround.utils.archive.determine_compressor_by_filename(
                            i
                            )
                        )

                    p = subprocess.Popen([compressor, '-d', i], cwd=pth_dir)
                    if p.wait() != 0:

                        ret = 1

                    else:
                        i = i[
                            0:
                            - len(
                                org.wayround.utils.archive.determine_extension_by_filename(i)
                                )
                            ]

                        p = subprocess.Popen(['patch', '-p1', '-i', os.path.join(pth_dir, i)], cwd=src_dir)
                        p.wait()


        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-shared',
                    '--with-shared',
                    '--enable-widec',
                    '--with-gpm',
                    '--with-ticlib',
                    '--with-termlib',
                    '--enable-const',
                    '--enable-ext-colors',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' + pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' + pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
#                    '--target=' + pkg_info['constitution']['target']
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

        if 'links' in actions and ret == 0:

            for s in [
                ('*w.so*', 'w.so', '.so'),
                ('*w_g.so*', 'w_g.so', '_g.so'),
                ('*w.a*', 'w.a', '.a'),
                ('*w_g.a*', 'w_g.a', '_g.a')
                ]:

                files = glob.glob(os.path.join(dst_lib_dir, s[0]))

                for i in files:
                    o_name = os.path.basename(i)
                    l_name = o_name.replace(s[1], s[2])

                    os.symlink(o_name, os.path.join(dst_lib_dir, l_name))


    return ret