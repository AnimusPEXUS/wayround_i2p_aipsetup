
import logging
import os.path
import subprocess

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
            buildingsite,
            ['extract', 'configure', 'build', 'distribute', 'SET'],
            action,
            "help"
            )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        pkg_info, actions = r

        name = pkg_info['pkg_info']['name']

        if not name in ['qt4', 'qt5']:
            raise Exception("Invalid package name")

        number = name[-1]

        src_dir = org.wayround.aipsetup.build.getDIR_SOURCE(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        etc_profile_set_dir = org.wayround.utils.path.join(
            dst_dir, 'etc', 'profile.d', 'SET'
            )

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
            p = subprocess.Popen(
                ['./configure'] +
                    [
                    '-opensource',
                    '-prefix', '/usr/lib/qt{}_w_toolkit'.format(number)
                    ],
                stdin=subprocess.PIPE,
                cwd=src_dir
                )
            p.communicate(input=b'yes\n')
            ret = p.wait()

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
                    'INSTALL_ROOT=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

        if 'SET' in actions and ret == 0:
            if not os.path.isdir(etc_profile_set_dir):
                try:
                    os.makedirs(etc_profile_set_dir)
                except:
                    logging.error(
                        "Can't create dir: {}".format(etc_profile_set_dir)
                        )
                    raise

            f = open(
                org.wayround.utils.path.join(
                    etc_profile_set_dir,
                    '009.qt{}'.format(number)
                    ),
                'w'
                )

            f.write("""\
#!/bin/bash
export PATH=$PATH:/usr/lib/qt{qtnum}_w_toolkit/bin

if [ "${{#PKG_CONFIG_PATH}}" -ne "0" ]; then
    PKG_CONFIG_PATH+=":"
fi
export PKG_CONFIG_PATH+="/usr/lib/qt{qtnum}_w_toolkit/lib/pkgconfig"

if [ "${{#LD_LIBRARY_PATH}}" -ne "0" ]; then
    LD_LIBRARY_PATH+=":"
fi
export LD_LIBRARY_PATH+="/usr/lib/qt{qtnum}_w_toolkit/lib"

""".format(qtnum=number))
            f.close()

    return ret
