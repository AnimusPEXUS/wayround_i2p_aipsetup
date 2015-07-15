

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        usr_share_mysql = '{}'.format(
            os.path.join(self.host_multiarch_dir, 'share', 'mysql')
            )
        return super().builder_action_configure_define_options(called_as, log) + [
            '-DCMAKE_INSTALL_PREFIX={}'.format(self.host_multiarch_dir),

            '-DMYSQL_DATADIR={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'share',
                    'mysql',
                    'data'
                    )
                ),

            '-DINSTALL_SBINDIR={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'bin'
                    )
                ),
            '-DINSTALL_LIBDIR={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'lib'
                    )
                ),
            '-DINSTALL_MANDIR={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'share',
                    'man'
                    )
                ),

            '-DINSTALL_DOCREADMEDIR={}'.format(usr_share_mysql),
            '-DINSTALL_INCLUDEDIR={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'include',
                    'mysql'
                    )
                ),

            '-DINSTALL_DOCDIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'docs'
                    )
                ),
            '-DINSTALL_INFODIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'docs'
                    )
                ),
            '-DINSTALL_MYSQLDATADIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'data'
                    )
                ),
            '-DINSTALL_MYSQLSHAREDIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'share'
                    )
                ),
            '-DINSTALL_MYSQLTESTDIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'mysql-test'
                    )
                ),
            '-DINSTALL_PLUGINDIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'lib',
                    'plugin'
                    )
                ),
            '-DINSTALL_SCRIPTDIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'scripts'
                    )
                ),
            '-DINSTALL_SHAREDIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    'share'
                    )
                ),
            '-DINSTALL_SQLBENCHDIR={}'.format(usr_share_mysql),
            '-DINSTALL_SUPPORTFILESDIR={}'.format(
                os.path.join(
                    usr_share_mysql,
                    support - files
                    )
                ),

            '-DWITH_SSL=yes',
            '-DWITH_READLINE=yes',
            '-DWITH_EXTRA_CHARSETS=all',
            '-DWITH_EMBEDDED_SERVER=yes',
            '-DWITH_CHARSET=utf8'
            ]
