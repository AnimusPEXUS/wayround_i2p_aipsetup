
import subprocess
import glob
import shutil


import os.path
import wayround_org.utils.path
import wayround_org.utils.pkgconfig
import wayround_org.utils.osutils
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        ret = {
            'plugin_dir': wayround_org.utils.path.join(
                self.calculate_install_prefix(),
                '/opt/unbit/uwsgi/plugins'
                )
            }
        ret['dst_plugin_dir'] = wayround_org.utils.path.join(
            self.get_dst_dir(),
            ret['plugin_dir']
            )

        return ret

    def define_actions(self):
        ret = super().define_actions()
        del ret['autogen']
        # del ret['configure']
        # del ret['distribute']
        return ret

    def builder_action_configure(self, called_as, log):

        cfg_filename = wayround_org.utils.path.join(
            self.get_src_dir(),
            'buildconf',
            'wayround_org.ini'
            )

        # plugin_dir = {plugin_dir}
        cfg = """\
[uwsgi]
main_plugin = php
inherit = base
plugins = php,python,gevent,http

""".format(
            # plugin_dir=self.custom_data['plugin_dir']
            )

        cfg_filename_f = open(cfg_filename, 'w')
        cfg_filename_f.write(cfg)
        cfg_filename_f.close()

        return 0

    def builder_action_build(self, called_as, log):

        php_cflags = []
        php_ldflags = [
            '-L{}/modules'.format(self.calculate_install_prefix()),
            '-lphp5'
            ]

        '''
        ldflags = 'LDFLAGS={}'.format(
            ' '.join(php_ldflags)
            )
        '''
        apr_ldflags = wayround_org.utils.pkgconfig.pkgconfig(
            'apr-1',
            '--libs'
            ).split()

        apr_util_ldflags = wayround_org.utils.pkgconfig.pkgconfig(
            'apr-util-1',
            '--libs'
            ).split()

        #env = {'LDFLAGS': ' '.join(
        #    apr_ldflags + apr_util_ldflags + php_ldflags
        #    )}

        #print("env: {}".format(env))

        #env = wayround_org.utils.osutils.env_vars_edit(env)

        p = subprocess.Popen(
            ['python3', './uwsgiconfig.py', '--build',
                'wayround_org.ini'
                # 'php.ini'
             ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr,
            # env=env
            )

        p.wait()

        return 0

    def builder_action_distribute(self, called_as, log):
        # self.custom_data['plugin_dir']
        dst_bin_dir = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'bin'
            )

        os.makedirs(
            self.custom_data['dst_plugin_dir'],
            exist_ok=True
            )

        os.makedirs(
            dst_bin_dir,
            exist_ok=True
            )

        plugins = glob.glob(
            wayround_org.utils.path.join(
                self.get_src_dir(),
                '*_plugin.so'
                )
            )

        for i in plugins:
            i_dst = wayround_org.utils.path.join(
                self.custom_data['dst_plugin_dir'],
                os.path.basename(i)
                )

            shutil.copy2(i, i_dst)

        shutil.copy2(
            wayround_org.utils.path.join(
                self.get_src_dir(),
                'uwsgi'
                ),
            wayround_org.utils.path.join(
                dst_bin_dir,
                'uwsgi'
                )
            )

        return 0
