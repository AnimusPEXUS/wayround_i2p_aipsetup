#!/usr/bin/python

import glob
import logging
import os.path
import shutil

import org.wayround.utils.file

import org.wayround.aipsetup.buildingsite
import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.buildscript.build_script_wrap(
        buildingsite,
        [
         'extract', 'configure', 'build',
         'distr_kernel', 'distr_modules', 'distr_firmware', 'distr_headers',
         #'distr_man', 
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

        src_dir = org.wayround.aipsetup.buildingsite.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.buildingsite.getDIR_DESTDIR(buildingsite)

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
            logging.info("aipsetup3 build s build+")
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
                    logging.error("Can't find directory in {}".format(modules_dir))
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

        if 'distr_headers' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'headers_install',
                    'INSTALL_HDR_PATH=' + os.path.join(dst_dir, 'usr')
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

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
