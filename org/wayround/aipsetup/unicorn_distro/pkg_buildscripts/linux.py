
import glob
import logging
import os.path
import shutil
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        [
         'extract', 'configure', 'build',

         'distr_kernel', 'distr_modules', 'distr_firmware',
         'distr_headers_internal',
         'distr_headers',
         'remove_install_files_from_includes',
#         'distr_man',
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

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        dst_boot_dir = os.path.join(dst_dir, 'boot')

        dst_man_dir = os.path.join(dst_dir, 'usr', 'share', 'man', 'man9')

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
                    os.path.join(dst_boot_dir, 'vmlinuz'),
                    os.path.join(
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

                modules_dir = os.path.join(dst_dir, 'lib', 'modules')

                files = os.listdir(modules_dir)

                if len(files) != 1:
                    logging.error(
                        "Can't find directory in {}".format(modules_dir)
                        )
                    ret = 1
                else:
                    modules_dir = os.path.join(modules_dir, files[0])

                    for i in ['build', 'source']:

                        new_link = os.path.join(modules_dir, i)

                        org.wayround.utils.file.remove_if_exists(new_link)

                        os.symlink(
                            os.path.join(
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
                os.path.join(src_dir, 'include'),
                os.path.join(dst_dir, 'usr', 'include'),
                overwrite_files=False,
                clear_before_copy=False,
                dst_must_be_empty=False
                )

        if 'distr_headers' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'headers_install_all',
                    'INSTALL_HDR_PATH=' + os.path.join(dst_dir, 'usr')
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
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
                cwd=os.path.join(dst_dir, 'usr', 'include')
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
                    os.path.join(
                        src_dir, 'Documentation', 'DocBook', 'man', '*.9.gz'
                        )
                    )

                logging.info("Copying {} man file(s)".format(len(man_files)))

                for i in man_files:
                    base = os.path.basename(i)
                    logging.info("copying {}".format(base))
                    shutil.copy(
                        os.path.join(src_dir, i),
                        os.path.join(dst_man_dir, base)
                        )

        if 'copy_source' in actions and ret == 0:

            try:
                ret = org.wayround.utils.file.copytree(
                    src_dir,
                    os.path.join(
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
                        new_link = os.path.join(
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
