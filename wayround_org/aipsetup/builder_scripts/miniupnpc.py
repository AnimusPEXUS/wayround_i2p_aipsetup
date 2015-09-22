

import os.path
import shutil
import glob

import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std_cmake


class Builder(wayround_org.aipsetup.builder_scripts.std_cmake.Builder):

    def define_actions(self):
        ret = super().define_actions()
        ret['after_distribute'] = self.builder_action_after_distribute
        return ret

    def builder_action_after_distribute(self, called_as, log):

        hs = glob.glob(
            wayround_org.utils.path.join(
                self.get_src_dir(),
                '*.h'
                )
            )

        incl_dir = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(),
            'include',
            'miniupnpc'
            )

        os.makedirs(incl_dir, exist_ok=True)

        for i in hs:
            dst_fpn = wayround_org.utils.path.join(
                incl_dir,
                os.path.basename(i)
                )
            shutil.copy(i, dst_fpn)
        return 0
