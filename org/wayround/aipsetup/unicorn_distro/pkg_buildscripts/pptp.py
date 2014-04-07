
import logging
import os.path

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'patch_0', 'build', 'distribute'],
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

        if 'patch_0' in actions and ret == 0:

            try:
                mf = open(os.path.join(src_dir, 'Makefile'))

                _l = mf.read().splitlines()

                mf.close()

                for i in range(len(_l)):

                    if _l[i].startswith(
                        "\tinstall -o root -m 555 pptp $(BINDIR)"
                        ):
                        _l[i] = "\tinstall pptp $(BINDIR)"

                    if _l[i].startswith(
                        "\tinstall -o root -m 555 pptpsetup $(BINDIR)"
                        ):
                        _l[i] = "\tinstall pptpsetup $(BINDIR)"

                mf = open(os.path.join(src_dir, 'Makefile'), 'w')
                mf.write('\n'.join(_l))
                mf.close()
            except:
                logging.exception("Can't patch Makefile")
                ret = 40

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
