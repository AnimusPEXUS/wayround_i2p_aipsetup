
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file
import wayround_org.utils.path


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'configure', 'build', 'distribute', 'fixlinks'],
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

        separate_build_dir = False

        source_configure_reldir = 'js/src'

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
                    '--with-x',
                    '--with-pthreads',
                    '--with-system-nspr',
#                    '--enable-readline',
                    '--enable-threadsafe',
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

        if 'fixlinks' in actions and ret == 0:
            for i in ['libmozjs185.so', 'libmozjs185.so.1.0']:

                iff = wayround_org.utils.path.join(dst_dir, 'usr', 'lib', i)

                try:
                    os.unlink(iff)
                except:
                    pass

                os.symlink('./libmozjs185.so.1.0.0', iff)

    return ret
