
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract_sm',
             'configure_sm', 'build_sm', 'distribute_sm'
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

        separate_build_dir_sm = True

        source_configure_reldir = '.'

        if 'extract_sm' in actions:
            if os.path.isdir(src_dir):
                logging.info("cleaningup source dir")
                if org.wayround.utils.file.cleanup_dir(src_dir) != 0:
                    logging.error("Some error while cleaning up source dir")
                    ret = 1

            if ret == 0:

                ret = autotools.extract_high(
                    buildingsite,
                    pkg_info['pkg_info']['basename'],
                    unwrap_dir=True,
                    rename_dir=False
                    )

        if 'configure_sm' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-application=suite',
                    '--enable-calendar',
                    '--enable-default-toolkit=cairo-gtk3',
                    '--enable-freetype2',
                    '--enable-safe-browsing',
                    '--enable-shared',
                    '--enable-shared-js',
                    '--enable-storage',
                    '--enable-xft',
                    '--disable-optimize',
                    # '--disable-webrtc',
                    '--enable-gstreamer=1.0',
                    '--with-pthreads',
                    '--with-system-nspr',
                    '--with-system-nss',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' + \
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' + \
                        pkg_info['constitution']['paths']['var'],
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir_sm,
                script_name='configure',
                run_script_not_bash=False,
                relative_call=False
                )

        if 'build_sm' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir_sm,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute_sm' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir_sm,
                source_configure_reldir=source_configure_reldir
                )

            # NPAPI now with xulrunner only

#            inc_dir = os.path.join(dst_dir, 'usr', 'include')
#
#            lst = os.listdir(inc_dir)
#
##            sea_inc_dir = None
#
#            if not len(lst) == 1:
#                logging.error(
#                    "Can't find seamonkey includes dir in {}".format(inc_dir)
#                    )
#                ret = 30
#            else:
#                pass
##                sea_inc_dir = lst[0]
#
#
##                os.symlink(sea_inc_dir, os.path.join(inc_dir, 'npapi'))

    return ret
