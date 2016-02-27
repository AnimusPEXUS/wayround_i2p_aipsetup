
import os.path

import subprocess
import collections

import wayround_org.utils.path
import wayround_org.utils.osutils

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = {
            'os_name': 'linux',
            'arch': 'amd64'
            }
        return ret

    def define_actions(self):
        ret = collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('bootstrap', self.builder_action_bootstrap),
            ('distribute', self.builder_action_distribute)
            ])
        return ret

    def builder_action_bootstrap(self, called_as, log):

        os_name = self.custom_data['os_name']
        arch = self.custom_data['arch']

        cwd = wayround_org.utils.path.join(
            self.get_src_dir(),
            'src'
            )
        log.info("CWD: {}".format(cwd))
        p = subprocess.Popen(
            ['bash', './bootstrap.bash'],
            cwd=cwd,
            env=wayround_org.utils.osutils.env_vars_edit(
                {
                    'GOROOT_BOOTSTRAP': os.environ['GOROOT'],
                    #'GOROOT_BOOTSTRAP': self.get_host_dir(),
                    'GOOS': os_name,
                    'GOARCH': arch
                    }
                ),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()

        return ret

    def builder_action_distribute(self, called_as, log):

        ret = 0

        os_name = self.custom_data['os_name']
        arch = self.custom_data['arch']

        go_version_str =\
            self.get_package_info()['pkg_nameinfo']['groups']['version']
        gogo_version_str = 'go{}'.format(go_version_str)

        go_dir = 'go-{}-{}-bootstrap'.format(os_name, arch)

        godir_path = wayround_org.utils.path.join(
            self.buildingsite_path,
            go_dir
            )

        dir_path = wayround_org.utils.path.join(
            self.get_host_lib_dir(),
            gogo_version_str
            )

        dst_dir_path = wayround_org.utils.path.join(
            self.get_dst_dir(),
            dir_path
            )

        os.makedirs(dst_dir_path, exist_ok=True)

        for i in os.listdir(godir_path):

            j = wayround_org.utils.path.join(godir_path, i)

            wayround_org.utils.file.copy_file_or_directory(
                j,
                wayround_org.utils.path.join(dst_dir_path, i),
                dst_must_be_empty=False
                )

        dst_etc_dir = wayround_org.utils.path.join(
            self.get_dst_dir(),
            'etc',
            'profile.d',
            'SET'
            )

        etc_file_path = wayround_org.utils.path.join(
            dst_etc_dir,
            '009.{}.{}.{}.sh'.format(
                gogo_version_str,
                self.get_host_from_pkgi(),
                self.get_arch_from_pkgi()
                )
            )

        os.makedirs(dst_etc_dir, exist_ok=True)

        with open(etc_file_path, 'w') as f:
            f.write("""\
#!/bin/bash

export GOROOT='{goroot}'
export PATH+=":$GOROOT/bin"
export GOPATH="$HOME/gopath"
export PATH+=":$GOPATH/bin"

""".format(goroot=dir_path))

        return ret
