

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.waf as waf
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        return ret

    def builder_action_configure(self, called_as, log):
        ret = waf.waf(
            self.src_dir,
            options=[
                '--prefix=' +
                self.package_info['constitution']['paths']['usr'],
                ],
            arguments=['configure'],
            environment={'PYTHON': '/usr/bin/python2'},
            environment_mode='copy',
            log=log
            )
        return ret

    def builder_action_build(self, called_as, log):
        ret = waf.waf(
            self.src_dir,
            options=[
                '--prefix=' +
                self.package_info['constitution']['paths']['usr'],
                ],
            arguments=['build'],
            environment={'PYTHON': '/usr/bin/python2'},
            environment_mode='copy',
            log=log
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = waf.waf(
            self.src_dir,
            options=[
                '--prefix=' +
                self.package_info['constitution']['paths']['usr'],
                '--destdir=' + self.dst_dir
                ],
            arguments=['install'],
            environment={'PYTHON': '/usr/bin/python2'},
            environment_mode='copy',
            log=log
            )
        return ret
