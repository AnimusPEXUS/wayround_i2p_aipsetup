

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        del(ret['autogen'])
        del(ret['configure'])
        del(ret['build'])
        return ret

    def builder_action_distribute(self, called_as, log):
        os.makedirs(
            wayround_org.utils.path.join(
                self.self.calculate_dst_install_prefix(),
                'include',
                'rpc'
                )
            )
        os.makedirs(
            wayround_org.utils.path.join(
                self.calculate_dst_install_prefix(),
                'include',
                'rpcsvc'
                )
            )

        wayround_org.utils.file.copytree(
            wayround_org.utils.path.join(
                self.get_src_dir(),
                'rpc'
                ),
            wayround_org.utils.path.join(
                self.self.calculate_dst_install_prefix(),
                'include',
                'rpc'
                ),
            dst_must_be_empty=False
            )

        wayround_org.utils.file.copytree(
            wayround_org.utils.path.join(
                self.get_src_dir(), 'rpcsvc'
                ),
            wayround_org.utils.path.join(
                self.self.calculate_dst_install_prefix(),
                'include',
                'rpcsvc'
                ),
            dst_must_be_empty=False
            )
        return ret
