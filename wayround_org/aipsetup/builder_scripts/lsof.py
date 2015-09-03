

import os.path
import shutil
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {}

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_extract(self, called_as, log):

        ret = autotools.extract_high(
            self.buildingsite_path,
            self.get_package_info()['pkg_info']['basename'],
            log=log,
            unwrap_dir=True,
            rename_dir=False
            )

        tar = None

        for i in os.listdir(self.get_src_dir()):
            if i.endswith('.tar'):
                tar = i
                break

        if tar is None:
            log.error(".tar not found in 00.SOURCE")
            ret = 1
        else:

            tar_dir = tar[:-len('.tar')]

            log.info("Unpacking {}".format(tar))
            p = subprocess.Popen(
                ['tar', '-xf', tar],
                cwd=self.get_src_dir(),
                stdout=log.stdout,
                stderr=log.stderr
                )

            p_r = p.wait()

            if p_r != 0:
                log.error("Error `{}' while untarring".format(p_r))
                ret = 2
            else:
                if not tar_dir in os.listdir(self.get_src_dir()):
                    log.error("wrong tarball")
                    ret = 3
                else:
                    tar_dir = wayround_org.utils.path.join(
                        self.get_src_dir(),
                        tar_dir
                        )
                    lsof_file = wayround_org.utils.path.join(
                        tar_dir,
                        'lsof'
                        )
                    lsof_man_file = wayround_org.utils.path.join(
                        tar_dir,
                        'lsof.8'
                        )

                    self.custom_data['tar_dir'] = tar_dir
                    self.custom_data['lsof_file'] = lsof_file
                    self.custom_data['lsof_man_file'] = lsof_man_file

        return ret

    def builder_action_configure(self, called_as, log):
        # TODO: additional host oriented configuration required as you can see
        p = subprocess.Popen(
            ['./Configure', '-n', 'linux'],
            cwd=self.custom_data['tar_dir'],
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            ['make'],
            cwd=self.custom_data['tar_dir'],
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret

    def builder_action_distribute(self, called_as, log):

        ret = 0

        lsof_file = self.custom_data['lsof_file']
        lsof_man_file = self.custom_data['lsof_man_file']

        if not os.path.isfile(lsof_file):
            log.error("Can't find lsof executable")
            ret = 1
        else:

            if not os.path.isfile(lsof_man_file):
                log.error("Can't find lsof.8 man file")
                ret = 1
            else:
                dst_bin_dir = wayround_org.utils.path.join(
                    self.calculate_dst_install_prefix(),
                    'bin'
                    )

                os.makedirs(dst_bin_dir, exist_ok=True)

                shutil.copy(
                    lsof_file,
                    wayround_org.utils.path.join(
                        dst_bin_dir,
                        'lsof'
                        )
                    )

                dst_man_dir = wayround_org.utils.path.join(
                    self.calculate_dst_install_prefix(),
                    'share',
                    'man',
                    'man8'
                    )

                os.makedirs(dst_man_dir, exist_ok=True)

                shutil.copy(
                    lsof_man_file,
                    wayround_org.utils.path.join(dst_man_dir, 'lsof.8')
                    )

        return ret
