
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

        source_configure_reldir = 'build_unix'

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
                    '--enable-sql',
                    '--enable-compat185',
                    '--enable-cxx',
                    '--enable-tcl',
                    '--with-tcl=/usr/lib',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        pkg_info['constitution']['paths']['var'],
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
                script_name='../dist/configure',
                run_script_not_bash=False,
#                relative_call=False,
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
            dis_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(
                                buildingsite
                                )

            doc_dir = os.path.join(dis_dir, 'usr', 'share', 'doc', 'db')

            try:
                os.makedirs(
                    doc_dir,
                    mode=0o755
                    )
            except:
                logging.exception("Error")
                ret = 20
            else:

                ret = autotools.make_high(
                    buildingsite,
                    options=[],
                    arguments=[
                        'install',
                        'DESTDIR=' + dis_dir,
                        'docdir=/usr/share/doc/db'
                        # it's not a mistake docdir
                        # must be eq to /usr/share/doc/db
                        ],
                    environment={},
                    environment_mode='copy',
                    use_separate_buildding_dir=separate_build_dir,
                    source_configure_reldir=source_configure_reldir
                    )

    return ret
