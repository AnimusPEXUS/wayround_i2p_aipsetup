
import logging
import os.path
import subprocess
import tempfile

import org.wayround.aipsetup.build
import org.wayround.aipsetup.buildtools.autotools as autotools
import org.wayround.utils.archive
import org.wayround.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = org.wayround.aipsetup.build.build_script_wrap(
        buildingsite,
        # ['extract', 'exctract_install-tl', 'configure',
        #  'build', 'distribute', 'install-tl'],
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

        tar_dir = org.wayround.aipsetup.build.getDIR_TARBALL(buildingsite)

        dst_dir = org.wayround.aipsetup.build.getDIR_DESTDIR(buildingsite)

        install_tl_dir = os.path.join(buildingsite, 'install-tl')

        script = os.path.join(install_tl_dir, 'install-tl')

        separate_build_dir = True

        source_configure_reldir = '.'

        usr = pkg_info['constitution']['paths']['usr']

        tex_live_dir = os.path.join(usr, 'lib', 'texlive')

        dst_tex_live_dir = os.path.join(dst_dir, 'usr', 'lib', 'texlive')

        dst_tex_live_bin = os.path.join(dst_tex_live_dir, 'bin')

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

        if 'exctract_install-tl' in actions and ret == 0:
            tl_install = None
            lst = os.listdir(tar_dir)

            for i in lst:
                if i.startswith('install-tl'):
                    tl_install = i

            if not tl_install:
                logging.error("install-tl archive not found")

            log = org.wayround.utils.log.Log(
                org.wayround.aipsetup.build.getDIR_BUILD_LOGS(buildingsite),
                'extract'
                )

            tmpdir = tempfile.mkdtemp(
                dir=org.wayround.aipsetup.build.getDIR_TEMP(buildingsite)
                )

            ret = org.wayround.utils.archive.extract_low(
                log,
                tmpdir,
                os.path.join(tar_dir, tl_install),
                outdir=install_tl_dir,
                unwrap_dir=True,
                rename_dir=False
                )

            log.close()

        if 'configure' in actions and ret == 0:

            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--prefix=' + tex_live_dir,
                    '--sysconfdir=' +
                        pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                        pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--disable-native-texlive-build',
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
                    'DESTDIR=' + dst_dir
                    ],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=separate_build_dir,
                source_configure_reldir=source_configure_reldir
                )

            p_dir = os.path.join(dst_dir, 'etc', 'profile.d', 'SET')

            if not os.path.exists(p_dir):
                os.makedirs(p_dir)

            p_file = os.path.join(p_dir, '009.texlive')
            f = open(p_file, 'w')
            f.write(
                """\
#!/bin/bash

TEXPATH={prefix}

export PATH="$PATH:$TEXPATH/bin"

if [ -n "$LD_LIBRARY_PATH" ]
then
    export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:$TEXPATH/lib"
else
    export LD_LIBRARY_PATH="$TEXPATH/lib"
fi

""".format(host=pkg_info['constitution']['host'], prefix=tex_live_dir)
                )
            f.close()

        if 'install-tl' in actions and ret == 0:
            logging.info(
                "Starting start-tl script in dir `{}'".format(install_tl_dir)
                )
            p = subprocess.Popen(
                [
                    script,
                    '-repository='
                    'http://mirrors.wayround.org/www.ctan.org'
                    '/tex/systems/texlive/tlnet/tlpkg',
                    '-custom-bin={dst_tex_live_bin}'.format(
                        host=pkg_info['constitution']['paths']['usr'],
                        dst_tex_live_bin=dst_tex_live_bin
                        )
                    ],
                env={
                        'TEXLIVE_INSTALL_PREFIX': dst_tex_live_dir,
                        'TEXLIVE_INSTALL_TEXDIR': dst_tex_live_dir
                        },
                cwd=install_tl_dir
                )

            ret = p.wait()

    return ret
