
import os.path
import collections

import wayround_org.aipsetup.build_scripts.std
import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder(wayround_org.aipsetup.build_scripts.std):

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('prepare_destdir', self.builder_action_prepare_destdir),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_prepare_destdir(self, called_as, log):
        ret = 0

        target_path = wayround_org.utils.path.join(self.dst_dir, 'usr')

        try:
            os.makedirs(
                target_path,
                mode=0o755,
                exist_ok=True
                )
        except:
            log.exception("Error creating directory: {}".format(target_path))
            ret = 1

        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'DESTDIR={}'.format(self.dst_dir),
                'prefix={}'.format(wayround_org.utils.path.join(self.dst_host_multiarh_dir)
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
