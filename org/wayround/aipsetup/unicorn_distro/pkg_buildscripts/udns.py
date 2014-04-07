
import glob
import logging
import os.path
import shutil

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
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

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

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
            ret = autotools.configure_high(
                buildingsite,
                options=[],
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

            if ret == 0:
                ret = autotools.make_high(
                    buildingsite,
                    options=[],
                    arguments=['shared'],
                    environment={},
                    environment_mode='copy',
                    use_separate_buildding_dir=separate_build_dir,
                    source_configure_reldir=source_configure_reldir
                    )

            if ret == 0:
                ret = autotools.make_high(
                    buildingsite,
                    options=[],
                    arguments=['static'],
                    environment={},
                    environment_mode='copy',
                    use_separate_buildding_dir=separate_build_dir,
                    source_configure_reldir=source_configure_reldir
                    )

        if 'distribute' in actions and ret == 0:

            dst_bin = os.path.join(dst_dir, 'usr', 'bin')
            dst_lib = os.path.join(dst_dir, 'usr', 'lib')
            dst_inc = os.path.join(dst_dir, 'usr', 'include')
            dst_man1 = os.path.join(dst_dir, 'usr', 'share', 'man', 'man1')
            dst_man3 = os.path.join(dst_dir, 'usr', 'share', 'man', 'man3')

            for i in [dst_bin, dst_lib, dst_inc, dst_man1, dst_man3]:
                if not os.path.isdir(i):
                    os.makedirs(i)

            for i in ['dnsget', 'ex-rdns', 'rblcheck']:
                for j in ['', '_s']:
                    shutil.copy(
                        os.path.join(src_dir, '{}{}'.format(i, j)),
                        dst_bin,
                        )

            for i in (
                glob.glob(os.path.join(src_dir, '*.so*')) +
                glob.glob(os.path.join(src_dir, '*.a'))
                ):

                b = os.path.basename(i)

                shutil.copy(
                    os.path.join(src_dir, b),
                    dst_lib
                    )

            shutil.copy(
                os.path.join(src_dir, 'udns.h'),
                dst_inc
                )

            for i in ['dnsget.1', 'rblcheck.1']:
                shutil.copy(
                    os.path.join(src_dir, i),
                    dst_man1,
                    )

            for i in ['udns.3']:
                shutil.copy(
                    os.path.join(src_dir, i),
                    dst_man3,
                    )

    return ret
