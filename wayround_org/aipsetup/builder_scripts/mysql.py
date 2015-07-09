

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std_cmake

# TODO: path fixes required


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        usr_share_mysql = '/usr/share/mysql'
        return super().builder_action_configure_define_options(called_as, log) + [
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
            ]
