
import logging
import os.path

import wayround_org.aipsetup.build
from wayround_org.aipsetup.buildtools import autotools
from wayround_org.aipsetup.buildtools import cmake
import wayround_org.utils.file


def main(buildingsite, action=None):

    ret = 0

    r = wayround_org.aipsetup.build.build_script_wrap(
        buildingsite,
        ['extract', 'cmake', 'build', 'distribute'],
        action,
        "help"
        )

    if not isinstance(r, tuple):
        logging.error("Error")
        ret = r

    else:

        self.package_info, actions = r

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
                self.package_info['pkg_info']['basename'],
                unwrap_dir=True,
                rename_dir=False
                )

        if 'cmake' in actions and ret == 0:

            usr_share_mysql = '/usr/share/mysql'

            ret = cmake.cmake_high(
                buildingsite,
                options=[
                    '-DCMAKE_INSTALL_PREFIX=/usr',

                    '-DMYSQL_DATADIR=/usr/share/mysql/data',

                    '-DINSTALL_SBINDIR=/usr/bin',
                    '-DINSTALL_LIBDIR=/usr/lib',
                    '-DINSTALL_MANDIR=/usr/share/man',

                    '-DINSTALL_DOCREADMEDIR=/usr/share/mysql',
                    '-DINSTALL_INCLUDEDIR=/usr/include/mysql',

                    '-DINSTALL_DOCDIR={}/docs'.format(usr_share_mysql),
                    '-DINSTALL_INFODIR={}/docs'.format(usr_share_mysql),
                    '-DINSTALL_MYSQLDATADIR={}/data'.format(usr_share_mysql),
                    '-DINSTALL_MYSQLSHAREDIR={}/share'.format(usr_share_mysql),
                    '-DINSTALL_MYSQLTESTDIR={}/mysql-test'.format(
                        usr_share_mysql
                        ),
                    '-DINSTALL_PLUGINDIR={}/lib/plugin'.format(
                        usr_share_mysql
                        ),
                    '-DINSTALL_SCRIPTDIR={}/scripts'.format(usr_share_mysql),
                    '-DINSTALL_SHAREDIR={}/share'.format(usr_share_mysql),
                    '-DINSTALL_SQLBENCHDIR={}'.format(usr_share_mysql),
                    '-DINSTALL_SUPPORTFILESDIR={}/support-files'.format(
                        usr_share_mysql
                        ),

                    '-DWITH_SSL=yes',
                    '-DWITH_READLINE=yes',
                    '-DWITH_EXTRA_CHARSETS=all',
                    '-DWITH_EMBEDDED_SERVER=yes',
                    '-DWITH_CHARSET=utf8'
                    ],
                arguments=[],
                environment={},
                environment_mode='copy',
                source_subdir=source_configure_reldir,
                build_in_separate_dir=separate_build_dir
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
