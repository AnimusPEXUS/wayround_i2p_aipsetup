

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
                '--prefix=/multiarch/{}'.format(self.host),
                ],
            arguments=['configure'],
            environment={
                'PYTHON': '/multiarch/{}/bin/python3'.format(self.host)
                },
            environment_mode='copy',
            log=log
            )
        return ret

    def builder_action_build(self, called_as, log):
        ret = waf.waf(
            self.src_dir,
            options=[
                '--prefix=/multiarch/{}'.format(self.host),
                ],
            arguments=['build'],
            environment={
                'PYTHON': '/multiarch/{}/bin/python3'.format(self.host)
                },
            environment_mode='copy',
            log=log
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        log = wayround_org.utils.log.Log(
            wayround_org.aipsetup.build.getDIR_BUILD_LOGS(buildingsite),
            'waf_configure'
            )

        ret = waf.waf(
            self.src_dir,
            options=[
                '--prefix=/multiarch/{}'.format(self.host),
                '--destdir=' + self.dst_dir
                ],
            arguments=[
                'install'
                ],
            environment={
                'PYTHON': '/multiarch/{}/bin/python3'.format(self.host)
                },
            environment_mode='copy',
            log=log
            )
        return ret
