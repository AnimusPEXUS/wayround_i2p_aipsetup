

import os.path

import wayround_org.utils.path
import wayround_org.utils.pkgconfig
import wayround_org.utils.file

import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        ret = {
            'etc_dir': wayround_org.utils.path.join(
                '/etc', 'httpd'
                )
            }
        ret['dst_etc_dir'] = wayround_org.utils.path.join(
            self.get_dst_dir(),
            ret['etc_dir']
            )

        return ret

    def define_actions(self):
        ret = super().define_actions()
        del(ret['distribute'])
        ret['after_build'] = self.builder_action_after_build
        ret['distribute'] = self.builder_action_distribute
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)

        curses_cflags = wayround_org.utils.pkgconfig.pkgconfig(
            'ncurses', '--cflags'
            )

        curses_libs = wayround_org.utils.pkgconfig.pkgconfig(
            'ncurses', '--libs'
            )

        ret += [
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
            #'--enable-embed',
            '--enable-fpm',
            '--enable-fastcgi',
            '--with-apxs2={}'.format(
                wayround_org.utils.file.which(
                    'apxs',
                    self.get_host_dir()
                    )
                ),
            'CFLAGS={}'.format(curses_cflags),
            'LDFLAGS={}'.format(curses_libs),
            ]
        return ret

    def builder_action_after_build(self, called_as, log):

        os.makedirs(
            self.custom_data['dst_etc_dir'],
            exist_ok=True
            )

        f = open(
            wayround_org.utils.path.join(
                self.custom_data['dst_etc_dir'],
                'httpd.conf'
                ),
            'w'
            )
        f.write('\n\nLoadModule rewrite_module modules/mod_rewrite.so\n\n')
        f.close()
        '''
        print(
            "warning. this php building module is not complete yet.\n"
            "please, remove files and dir starting with `.' in dir 04.DESTDIR\n"
            "after what you can procede with 'aipsetup build pack'"
            )
        '''
        return 0

    def builder_action_distribute_define_args(self, called_as, log):
        ret = ['install',
               'INSTALL_ROOT={}'.format(self.get_dst_dir())]
        return ret

    def builder_action_after_distribute(self, called_as, log):
        os.rename(
            wayround_org.utils.path.join(
                self.custom_data['dst_etc_dir'],
                'httpd.conf'
                ),
            wayround_org.utils.path.join(
                self.custom_data['dst_etc_dir'],
                'httpd.php.conf'
                )
            )

        os.unlink(
            wayround_org.utils.path.join(
                self.custom_data['dst_etc_dir'],
                'httpd.conf.bak'
                )
            )
        lst = os.listdir(
            self.get_dst_dir()
            )

        for i in lst:
            if i.startswith('.'):
                wayround_org.utils.file.remove_if_exists(
                    wayround_org.utils.path.join(
                        self.get_dst_dir(),
                        i
                        )
                    )

        return 0
