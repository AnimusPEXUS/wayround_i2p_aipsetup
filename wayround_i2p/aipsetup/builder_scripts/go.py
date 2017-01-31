
import os.path

import subprocess
import collections

import wayround_i2p.utils.path
import wayround_i2p.utils.osutils

import wayround_i2p.aipsetup.builder_scripts.std


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

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

        cwd = wayround_i2p.utils.path.join(
            self.get_src_dir(),
            'src'
            )
        log.info("CWD: {}".format(cwd))
        p = subprocess.Popen(
            ['bash', './bootstrap.bash'],
            cwd=cwd,
            env=wayround_i2p.utils.osutils.env_vars_edit(
                {
                    # os.environ['GOROOT'],
                    'GOROOT_BOOTSTRAP': '/multihost/x86_64-pc-linux-gnu/lib64/go1.7.3',
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

        godir_path = wayround_i2p.utils.path.join(
            self.buildingsite_path,
            go_dir
            )

        dir_path = wayround_i2p.utils.path.join(
            self.get_host_lib_dir(),
            gogo_version_str
            )

        dst_dir_path = wayround_i2p.utils.path.join(
            self.get_dst_dir(),
            dir_path
            )

        os.makedirs(dst_dir_path, exist_ok=True)

        for i in os.listdir(godir_path):

            j = wayround_i2p.utils.path.join(godir_path, i)

            wayround_i2p.utils.file.copy_file_or_directory(
                j,
                wayround_i2p.utils.path.join(dst_dir_path, i),
                dst_must_be_empty=False
                )

        dst_etc_dir = wayround_i2p.utils.path.join(
            self.get_dst_dir(),
            'etc',
            'profile.d',
            'SET'
            )

        etc_file_path = wayround_i2p.utils.path.join(
            dst_etc_dir,
            '009.{}.{}.{}.sh'.format(
                gogo_version_str,
                self.get_host_from_pkgi(),
                self.get_arch_from_pkgi()
                )
            )

        os.makedirs(dst_etc_dir, exist_ok=True)

        # NOTE: set-file is needed only in primary install.
        #       also, go should be 'only primary install' in package settings.
        if self.get_host_from_pkgi() == self.get_arch_from_pkgi():

            with open(etc_file_path, 'w') as f:

                f.write("""\
#!/bin/env bash

export GOROOT="{goroot}"

export PATH+=":$GOROOT/bin"

TEMP_PATH="$HOME/gopath_clean"

export GOPATH="$TEMP_PATH"
export PATH+=":$TEMP_PATH/bin"

TEMP_PATH="$HOME/gopath_work"

export GOPATH+=":$TEMP_PATH"
export PATH+=":$TEMP_PATH/bin"

unset TEMP_GOPATH

""".format(
                    goroot=dir_path
                    )
                    )

        return ret
