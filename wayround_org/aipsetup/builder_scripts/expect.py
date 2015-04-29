
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.archive
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

        self.package_info, actions = r

        src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(buildingsite)

        tar_dir = wayround_org.aipsetup.build.getDIR_TARBALL(buildingsite)

        dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(buildingsite)

        separate_build_dir = False

        source_configure_reldir = '.'

        if 'extract' in actions:

            files = os.listdir(tar_dir)

            tcl_found = False
            tk_found = False
            for i in files:
                if i.startswith('tcl'):
                    tcl_found = i

                if i.startswith('tk'):
                    tk_found = i

            if not tcl_found:
                logging.error(
                    "Tcl and Tk source tarballs must be in tarballs dir"
                    )
                ret = 20
            else:

                if os.path.isdir(src_dir):
                    logging.info("cleaningup source dir")
                    wayround_org.utils.file.cleanup_dir(src_dir)

                logging.info("Extracting Tcl")
                wayround_org.utils.archive.extract(
                    os.path.join(tar_dir, tcl_found), buildingsite
                    )

                logging.info("Extracting Tk")
                wayround_org.utils.archive.extract(
                    os.path.join(tar_dir, tk_found), buildingsite
                    )

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
                    '--enable-64bit',
                    '--enable-64bit-vis',
                    '--enable-wince',
                    '--with-tcl=/usr/lib',
                    '--with-tk=/usr/lib',
                    '--prefix=' + self.package_info['constitution']['paths']['usr'],
                    '--mandir=' + self.package_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        self.package_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        self.package_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + self.package_info['constitution']['host']
#                    '--build=' + self.package_info['constitution']['build'],
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

    return ret
