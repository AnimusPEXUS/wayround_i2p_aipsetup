
import glob
import logging
import os.path
import shutil
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file
import org.wayround.utils.path


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        [
         'extract', 'configure',

         'build',

         'distr_kernel',
         'distr_modules',
         'distr_firmware',
         'distr_headers_internal',
         'distr_headers_normal',
         'distr_headers_internal_repeat',
         'distr_arch_headers_internal',
         'remove_install_files_from_includes',
         'distr_man',
         'copy_source'
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

        src_arch_dir = org.wayround.utils.path.join(src_dir, 'arch')

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        dst_boot_dir = org.wayround.utils.path.join(dst_dir, 'boot')

        dst_man_dir = org.wayround.utils.path.join(
            dst_dir, 'usr', 'share', 'man', 'man9'
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
            logging.info("You now need to configure kernel by your needs and")
            logging.info("continue building procedure with command")
            logging.info("'aipsetup3 build continue build+'")
            ret = 1

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

        if 'distr_kernel' in actions and ret == 0:

            if not os.path.exists(dst_boot_dir):
                os.makedirs(dst_boot_dir)

            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'INSTALL_PATH=' + dst_boot_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

            if ret == 0:

                os.rename(
                    org.wayround.utils.path.join(dst_boot_dir, 'vmlinuz'),
                    org.wayround.utils.path.join(
                        dst_boot_dir, 'vmlinuz-{}'.format(
                            pkg_info['pkg_nameinfo']['groups']['version']
                            )
                        )
                    )

        if 'distr_modules' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'modules_install',
                    'INSTALL_MOD_PATH=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

            if ret == 0:

                modules_dir = \
                    org.wayround.utils.path.join(dst_dir, 'lib', 'modules')

                files = os.listdir(modules_dir)

                if len(files) != 1:
                    logging.error(
                        "Can't find directory in {}".format(modules_dir)
                        )
                    ret = 1
                else:
                    modules_dir = \
                        org.wayround.utils.path.join(modules_dir, files[0])

                    for i in ['build', 'source']:

                        new_link = org.wayround.utils.path.join(modules_dir, i)

                        org.wayround.utils.file.remove_if_exists(new_link)

                        os.symlink(
                            org.wayround.utils.path.join(
                                os.path.sep + 'usr',
                            'src',
                            'linux-{}'.format(
                                pkg_info['pkg_nameinfo']['groups']['version']
                                )
                                ),
                            new_link
                            )

                del(files)

        if 'distr_firmware' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'firmware_install',
                    'INSTALL_MOD_PATH=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distr_headers_internal' in actions and ret == 0:

            org.wayround.utils.file.copytree(
                org.wayround.utils.path.join(src_dir, 'include'),
                org.wayround.utils.path.join(dst_dir, 'usr', 'include'),
                overwrite_files=False,
                clear_before_copy=False,
                dst_must_be_empty=False
                )

        if 'distr_headers_normal' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'headers_install_all',
                    'INSTALL_HDR_PATH=' +
                        org.wayround.utils.path.join(dst_dir, 'usr')
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'distr_headers_internal_repeat' in actions and ret == 0:

            org.wayround.utils.file.copytree(
                org.wayround.utils.path.join(src_dir, 'include'),
                org.wayround.utils.path.join(dst_dir, 'usr', 'include'),
                overwrite_files=False,
                clear_before_copy=False,
                dst_must_be_empty=False
                )

        if 'distr_arch_headers_internal' in actions and ret == 0:

            archs = os.listdir(src_arch_dir)
            archs.sort()
            for i in archs[:]:
                fp = org.wayround.utils.path.join(src_arch_dir, i)
                if not os.path.isdir(fp) or os.path.islink(fp):
                    archs.remove(i)

            for i in archs:
                fp = org.wayround.utils.path.join(
                    src_arch_dir, i, 'include', 'asm'
                    )

                if os.path.isdir(fp):

                    org.wayround.utils.file.copytree(
                        fp,
                        org.wayround.utils.path.join(
                            dst_dir, 'usr', 'include', 'asm-{}'.format(i)
                            ),
                        overwrite_files=False,
                        clear_before_copy=False,
                        dst_must_be_empty=False
                        )

            print("""
Please make correct 04.DESTDIR/usr/include/asm by 'ln -s' manually.

Continue with command
'aipsetup3 build continue remove_install_files_from_includes+'
""")

            ret = 1

        if 'remove_install_files_from_includes' in actions and ret == 0:
            p = subprocess.Popen(
                ['find',
                 '(', '-name', '.install',
                 '-o', '-name', '..install.cmd',
                 '-o', '-name', '.check',
                 '-o', '-name', '..check.cmd',
                 '-o', '-name', 'Kbuild',
                 ')',
                 '-delete'],
                cwd=org.wayround.utils.path.join(dst_dir, 'usr', 'include')
                )
            p.wait()

        if 'distr_man' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'mandocs'
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

            if ret == 0:

                if not os.path.isdir(dst_man_dir):
                    os.makedirs(dst_man_dir)

                man_files = glob.glob(
                    org.wayround.utils.path.join(
                        src_dir, 'Documentation', 'DocBook', 'man', '*.9.gz'
                        )
                    )

                man_files.sort()

                logging.info("Copying {} man file(s)".format(len(man_files)))

                for i in man_files:
                    base = os.path.basename(i)
                    logging.info("copying {}".format(base))
                    shutil.copy(
                        org.wayround.utils.path.join(i),
                        org.wayround.utils.path.join(dst_man_dir, base)
                        )

        if 'copy_source' in actions and ret == 0:

            try:
                ret = org.wayround.utils.file.copytree(
                    src_dir,
                    org.wayround.utils.path.join(
                        dst_dir,
                        'usr',
                        'src',
                        'linux-{}'.format(
                            pkg_info['pkg_nameinfo']['groups']['version']
                            )
                        ),
                    overwrite_files=True,
                    clear_before_copy=True,
                    dst_must_be_empty=False
                    )
            except:
                logging.exception("Some error")
                ret = 2
            else:
                if ret == 0:
                    try:
                        new_link = org.wayround.utils.path.join(
                            dst_dir,
                            'usr',
                            'src',
                            'linux'
                            )

                        org.wayround.utils.file.remove_if_exists(new_link)

                        os.symlink(
                            '.{}linux-{}'.format(
                                os.path.sep,
                                pkg_info['pkg_nameinfo']['groups']['version']
                                ),
                            new_link
                            )
                    except:
                        logging.exception("Some error")
                        ret = 3

    return ret
