
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file
import org.wayround.utils.path


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract_sm',
             'configure_sm', 'build_sm', 'distribute_sm',
             'extract_xul',
             'configure_xul', 'build_xul', 'distribute_xul',

             'reduce_destdir_share', 'reduce_destdir_include',
             'reduce_destdir_lib1', 'reduce_destdir_lib2'
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
        separate_build_dir_xul = True

        ###### SEAMONKEY PART ###### (XULRUNNER LOWER)

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
                    '--enable-optimize',
                    '--enable-safe-browsing',
                    '--enable-shared',
                    '--enable-shared-js',
                    '--enable-storage',
                    '--enable-xft',
                    '--with-pthreads',
                    '--with-system-nspr',
                    '--with-system-nss',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
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

            inc_dir = os.path.join(dst_dir, 'usr', 'include')

            lst = os.listdir(inc_dir)

            sea_inc_dir = None

            if not len(lst) == 1:
                logging.error(
                    "Can't find seamonkey includes dir in {}".format(inc_dir)
                    )
                ret = 30
            else:
                sea_inc_dir = lst[0]

                os.symlink(sea_inc_dir, os.path.join(inc_dir, 'npapi'))

        ###### XULRUNNER PART ######

        source_configure_reldir = './mozilla'

        if 'extract_xul' in actions and ret == 0:
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

        if 'configure_xul' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-application=xulrunner',
                    '--enable-default-toolkit=cairo-gtk3',
                    '--enable-freetype2',
                    '--enable-optimize',
                    '--enable-shared',
                    '--enable-shared-js',
                    '--enable-xft',
                    '--with-pthreads',
                    '--with-system-nspr',
                    '--with-system-nss',
                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        pkg_info['constitution']['paths']['var'],
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build']
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_configure_reldir=source_configure_reldir,
                use_separate_buildding_dir=separate_build_dir_xul,
                script_name='configure',
                run_script_not_bash=False,
                relative_call=False
                )

        if 'build_xul' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir_xul,
                source_configure_reldir=source_configure_reldir
                )

        if 'distribute_xul' in actions and ret == 0:
            ret = autotools.make_high(
                buildingsite,
                options=[],
                arguments=[
                    'install',
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir_xul,
                source_configure_reldir=source_configure_reldir
                )

        if 'reduce_destdir_share' in actions and ret == 0:
            idl_path = org.wayround.utils.path.join(
                dst_dir, 'usr', 'share', 'idl'
                )

            idl_dirs = os.listdir(idl_path)

            sm_dir = None
            for i in idl_dirs:
                if i.startswith('seamonkey-'):
                    sm_dir = i

            xul_dir = None
            for i in idl_dirs:
                if i.startswith('xulrunner-'):
                    xul_dir = i

            if not sm_dir or not xul_dir:
                logging.error(
                    "Can't find required dirs in `{}'".format(idl_path)
                    )
                ret = 3
            else:

                idl_sm_path = org.wayround.utils.path.join(idl_path, sm_dir)
                idl_xul_path = org.wayround.utils.path.join(idl_path, xul_dir)

                org.wayround.utils.file.checksumed_dir_redue(
                    idl_sm_path, idl_xul_path
                    )

        if 'reduce_destdir_include' in actions and ret == 0:
            include_path = org.wayround.utils.path.join(
                dst_dir, 'usr', 'include'
                )

            include_dirs = os.listdir(include_path)

            sm_dir = None
            for i in include_dirs:
                if i.startswith('seamonkey-'):
                    sm_dir = i

            xul_dir = None
            for i in include_dirs:
                if i.startswith('xulrunner-'):
                    xul_dir = i

            if not sm_dir or not xul_dir:
                logging.error(
                    "Can't find required dirs in `{}'".format(include_path)
                    )
                ret = 3
            else:

                include_sm_path = org.wayround.utils.path.join(
                    include_path,
                    sm_dir
                    )
                include_xul_path = org.wayround.utils.path.join(
                    include_path,
                    xul_dir
                    )

                org.wayround.utils.file.checksumed_dir_redue(
                    include_sm_path, include_xul_path
                    )

        if 'reduce_destdir_lib1' in actions and ret == 0:
            include_path = org.wayround.utils.path.join(
                dst_dir, 'usr', 'lib'
                )

            include_dirs = os.listdir(include_path)

            sm_dir = None
            for i in include_dirs:
                if i.startswith('seamonkey-') and not 'devel' in i:
                    sm_dir = i

            xul_dir = None
            for i in include_dirs:
                if i.startswith('xulrunner-') and not 'devel' in i:
                    xul_dir = i

            if not sm_dir or not xul_dir:
                logging.error(
                    "Can't find required dirs in `{}'".format(include_path)
                    )
                ret = 3
            else:

                include_sm_path = org.wayround.utils.path.join(
                    include_path,
                    sm_dir
                    )
                include_xul_path = org.wayround.utils.path.join(
                    include_path,
                    xul_dir
                    )

                org.wayround.utils.file.checksumed_dir_redue(
                    include_sm_path, include_xul_path
                    )

        if 'reduce_destdir_lib2' in actions and ret == 0:
            include_path = org.wayround.utils.path.join(
                dst_dir, 'usr', 'lib'
                )

            include_dirs = os.listdir(include_path)

            sm_dir = None
            for i in include_dirs:
                if i.startswith('seamonkey-') and 'devel' in i:
                    sm_dir = i

            xul_dir = None
            for i in include_dirs:
                if i.startswith('xulrunner-') and 'devel' in i:
                    xul_dir = i

            if not sm_dir or not xul_dir:
                logging.error(
                    "Can't find required dirs in `{}'".format(include_path)
                    )
                ret = 3
            else:

                include_sm_path = org.wayround.utils.path.join(
                    include_path,
                    sm_dir
                    )
                include_xul_path = org.wayround.utils.path.join(
                    include_path,
                    xul_dir
                    )

                org.wayround.utils.file.checksumed_dir_redue(
                    include_sm_path, include_xul_path
                    )

    return ret
