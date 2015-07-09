

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['distribute'])
        ret['after_build'] = self.builder_action_after_build
        ret['distribute'] = self.builder_action_distribute
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
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
            '--with-apxs={}'.format(
                wayround_org.utils.file.which(
                    'apxs',
                    '/multiarch/{}'.format(self.host)
                    )
                )
            ]

    def builder_action_after_build(self, called_as, log):

        os.makedirs(
            os.path.join(self.dst_dir, 'daemons', 'httpd', 'etc'),
            exist_ok=True
            )

        f = open(
            os.path.join(
                self.dst_dir, 'daemons', 'httpd', 'etc', 'httpd.conf'
                ),
            'w'
            )
        f.write('\n\nLoadModule rewrite_module modules/mod_rewrite.so\n\n')
        f.close()
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTALL_ROOT=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_after_distribute(self, called_as, log):
        os.rename(
            os.path.join(
                self.dst_dir,
                'daemons',
                'httpd',
                'etc',
                'httpd.conf'),
            os.path.join(
                self.dst_dir, 'daemons', 'httpd', 'etc', 'httpd.php.conf'
                )
            )

        os.unlink(
            os.path.join(
                self.dst_dir, 'daemons', 'httpd', 'etc',
                'httpd.conf.bak'
                )
            )
        return ret
