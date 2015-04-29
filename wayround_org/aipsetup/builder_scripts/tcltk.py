
import logging
import os.path
import glob

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'configure', 'build', 'distribute', 'ln'],
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

        separate_build_dir = False

        source_configure_reldir = 'unix'

        if 'extract' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                wayround_org.utils.file.cleanup_dir(src_dir)
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
                    '--enable-threads',
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
                    '--mandir=' + self.package_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        self.package_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        self.package_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + self.package_info['constitution']['host'],
                    '--build=' + self.package_info['constitution']['build'],
#                    '--target=' + self.package_info['constitution']['target']
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

            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install-private-headers',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'ln' in actions and ret == 0:

            ret = 0

            pkg_name = self.package_info['pkg_info']['name']

            bin_dir = wayround_org.utils.path.join(dst_dir, 'usr', 'bin')

            bin_files = os.listdir(bin_dir)

            if pkg_name == 'tcl':
                for i in bin_files:
                    if i.startswith('tclsh') and i != 'tclsh':

                        target_name = wayround_org.utils.path.join(
                            bin_dir, 'tclsh'
                            )

                        if (os.path.exists(target_name)
                            or os.path.islink(target_name)):

                            os.unlink(target_name)

                        os.symlink(i, target_name)

                        break

            if pkg_name == 'tk':
                for i in bin_files:
                    if i.startswith('wish') and i != 'wish':

                        target_name = wayround_org.utils.path.join(
                            bin_dir, 'wish'
                            )

                        if (os.path.exists(target_name)
                            or os.path.islink(target_name)):

                            os.unlink(target_name)

                        os.symlink(i, target_name)

                        break

    return ret
