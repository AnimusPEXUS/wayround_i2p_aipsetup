
import os.path
import subprocess
import collections

import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        src_ant_dir = wayround_org.utils.path.join(
            self.get_src_dir(),
            'dist'
            #'apache-ant-{}'.format(
            #    self.get_package_info()['pkg_nameinfo']['groups']['version']
            #    )
            )

        ant_dir = wayround_org.utils.path.join(
            self.calculate_install_prefix(),
            'opt',
            'java',
            'apache-ant'
            )

        dst_ant_dir = wayround_org.utils.path.join(
            self.get_dst_dir(),
            ant_dir
            )

        etc_dir = wayround_org.utils.path.join(
            self.get_dst_dir(),
            'etc',
            'profile.d',
            'SET'
            )

        apacheant009 = wayround_org.utils.path.join(
            etc_dir,
            '009.apache-ant.{}.{}.sh'.format(
                self.get_host_from_pkgi(),
                self.get_arch_from_pkgi()
                )
            )

        ret = {
            'src_ant_dir': src_ant_dir,
            'ant_dir': ant_dir,
            'dst_ant_dir': dst_ant_dir,
            'etc_dir': etc_dir,
            'apacheant009': apacheant009
            }

        return ret

    def define_actions(self):
        ret = collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('bootstrap', self.builder_action_bootstrap),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])
        return ret

    def builder_action_bootstrap(self, called_as, log):
        p = subprocess.Popen(
            [
                './bootstrap.sh'
                ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            [
                './bootstrap/bin/ant'
                ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = 0
        os.makedirs(
            self.custom_data['dst_ant_dir'],
            exist_ok=True
            )

        if wayround_org.utils.file.copytree(
            self.custom_data['src_ant_dir'],
            self.custom_data['dst_ant_dir'],
            overwrite_files=True,
            clear_before_copy=True,
            dst_must_be_empty=True
            ) != 0:
            ret += 1

        os.makedirs(
            self.custom_data['etc_dir'],
            exist_ok=True
            )

        fi = open(self.custom_data['apacheant009'], 'w')

        fi.write(
"""\
#!/bin/bash
export ANT_HOME='{ant_dir}'
export PATH="$PATH:$ANT_HOME/bin"
""".format(ant_dir=self.custom_data['ant_dir'])
            )

        fi.close()

        return ret
