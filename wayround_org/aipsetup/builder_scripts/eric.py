

import os.path
import subprocess

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        num = self.get_package_info()['pkg_info']['name'][-1]

        if num == '4':
            num = '2'
        elif num == '5':
            num = '3'
        else:
            raise Exception("Unsupported eric")

        python = 'python{}'.format(num)

        ret = {
            'python': python
            }
        return ret

    def define_actions(self):
        ret = super().define_actions()
        for i in ['configure', 'build', 'autogen']:
            del ret[i]
        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            [
                self.custom_data['python'],
                './install.py',
                '-i',
                self.get_dst_dir()
                ],
            cwd=self.get_src_dir(),
            stdout=log.stdout,
            stderr=log.stderr
            )
        ret = p.wait()
        return ret
