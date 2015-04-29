
import logging
import os.path
import subprocess

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'autogen', 'configure', 'build',
         'afterbuild',
         'distribute',
         'afterbuild2'],
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

        source_configure_reldir = '.'

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

        if 'autogen' in actions and ret == 0:
            if not os.path.isfile(os.path.join(src_dir, 'configure')):
                if not os.path.isfile(os.path.join(src_dir, 'autogen.sh')):
                    logging.error(
                        "./configure not found and autogen.sh is absent"
                        )
                    ret = 2
                else:
                    p = subprocess.Popen(['./autogen.sh'], cwd=src_dir)
                    ret = p.wait()

        if 'configure' in actions and ret == 0:
            ret = autotools.configure_high(
                buildingsite,
                options=[
                    '--enable-ftp',
                    '--with-openssl',
                    '--enable-mbstring',
                    '--with-sqlite',
                    '--enable-sqlite-utf8',
                    '--with-pdo-sqlite',
                    '--with-gd',
                    '--with-jpeg-dir',
                    '--with-png-dir',
                    '--with-zlib-dir',
                    '--with-ttf',
                    '--with-freetype-dir',
                    '--with-pdo-pgsql',
                    '--with-pgsql',
                    '--with-mysql',
                    '--with-ncurses',
                    '--with-pdo-mysql',
                    '--with-mysqli',
                    '--with-readline',
                    '--enable-fastcgi',
                    '--with-apxs2=/usr/bin/apxs',

                    '--prefix=' + pkg_info['constitution']['paths']['usr'],
                    '--mandir=' + pkg_info['constitution']['paths']['man'],
                    '--sysconfdir=' +
                    pkg_info['constitution']['paths']['config'],
                    '--localstatedir=' +
                    pkg_info['constitution']['paths']['var'],
                    '--enable-shared',
                    '--host=' + pkg_info['constitution']['host'],
                    '--build=' + pkg_info['constitution']['build'],
                    # '--target=' + pkg_info['constitution']['target']
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

        if 'afterbuild' in actions and ret == 0:

            try:
                os.makedirs(os.path.join(dst_dir, 'daemons', 'httpd', 'etc'))
            except:
                logging.exception("can't make dir")

            f = open(
                os.path.join(dst_dir, 'daemons', 'httpd', 'etc', 'httpd.conf'),
                'w'
                )
            f.write('\n\nLoadModule rewrite_module modules/mod_rewrite.so\n\n')
            f.close()

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

        if 'afterbuild2' in actions and ret == 0:

            os.rename(
                os.path.join(dst_dir, 'daemons', 'httpd', 'etc', 'httpd.conf'),
                os.path.join(
                    dst_dir, 'daemons', 'httpd', 'etc', 'httpd.php.conf'
                    )
                )

            os.unlink(
                os.path.join(
                    dst_dir, 'daemons', 'httpd', 'etc',
                    'httpd.conf.bak'
                    )
                )

    return ret
