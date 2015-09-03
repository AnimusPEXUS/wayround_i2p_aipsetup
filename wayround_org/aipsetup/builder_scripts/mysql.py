

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        # TODO: tests required
        usr_share_mysql = '{}'.format(
            wayround_org.utils.path.join(
                self.calculate_install_prefix(), 'share', 'mysql'
                )
            )
        return super().builder_action_configure_define_opts(called_as, log) + [
            # '-DCMAKE_INSTALL_PREFIX={}'.format(self.get_host_dir()),

            '-DMYSQL_DATADIR={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'share',
                    'mysql',
                    'data'
                    )
                ),

            '-DINSTALL_SBINDIR={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'bin'
                    )
                ),
            '-DINSTALL_LIBDIR={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_libdir(),
                    )
                ),
            '-DINSTALL_MANDIR={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'share',
                    'man'
                    )
                ),

            '-DINSTALL_DOCREADMEDIR={}'.format(usr_share_mysql),
            '-DINSTALL_INCLUDEDIR={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'include',
                    'mysql'
                    )
                ),

            '-DINSTALL_DOCDIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'docs'
                    )
                ),
            '-DINSTALL_INFODIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'docs'
                    )
                ),
            '-DINSTALL_MYSQLDATADIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'data'
                    )
                ),
            '-DINSTALL_MYSQLSHAREDIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'share'
                    )
                ),
            '-DINSTALL_MYSQLTESTDIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'mysql-test'
                    )
                ),
            '-DINSTALL_PLUGINDIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'lib',
                    'plugin'
                    )
                ),
            '-DINSTALL_SCRIPTDIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'scripts'
                    )
                ),
            '-DINSTALL_SHAREDIR={}'.format(
                wayround_org.utils.path.join(
                    usr_share_mysql,
                    'share'
                    )
                ),
            '-DINSTALL_SQLBENCHDIR={}'.format(usr_share_mysql),
            '-DINSTALL_SUPPORTFILESDIR={}'.format(
                wayround_org.utils.path.join(
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
