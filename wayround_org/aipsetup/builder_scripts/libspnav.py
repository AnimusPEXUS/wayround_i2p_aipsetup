

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_distribute(self, called_as, log):
        arch_dir = self.get_dst_host_dir()
        for i in [
                self.get_dst_host_lib_dir(),
                wayround_org.utils.path.join(
                    self.get_dst_host_arch_dir(),
                    'include'
                    )
                ]:
            os.makedirs(i, exist_ok=True)

        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=[],
            arguments=[
                'install',
                'PREFIX={}'.format(self.get_dst_host_dir())
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
