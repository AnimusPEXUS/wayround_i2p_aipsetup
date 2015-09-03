

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.waf as waf
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = {
            'PYTHON': wayround_org.utils.file.which(
                'python3',
                self.get_host_dir()
                )
            }
        return ret

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):
        ret = waf.waf(
            self.get_src_dir(),
            options=[
                '--prefix={}'.format(self.calculate_install_prefix()),
                ],
            arguments=['configure'],
            environment={'PYTHON': self.custom_data['PYTHON']},
            environment_mode='copy',
            log=log
            )
        return ret

    def builder_action_build(self, called_as, log):
        ret = waf.waf(
            self.get_src_dir(),
            options=[
                '--prefix={}'.format(self.calculate_install_prefix()),
                ],
            arguments=['build'],
            environment={'PYTHON': self.custom_data['PYTHON']},
            environment_mode='copy',
            log=log
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = waf.waf(
            self.get_src_dir(),
            options=[
                '--prefix={}'.format(self.calculate_install_prefix()),
                '--destdir={}'.format(self.get_dst_dir())
                ],
            arguments=['install'],
            environment={'PYTHON': self.custom_data['PYTHON']},
            environment_mode='copy',
            log=log
            )
        return ret
