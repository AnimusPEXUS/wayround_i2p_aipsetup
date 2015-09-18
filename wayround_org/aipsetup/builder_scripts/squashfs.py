

import os.path
import wayround_org.utils.path
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        ret = super().define_actions()
        for i in ['autogen', 'configure', 'build']:
            if i in ret:
                del ret[i]
        return ret

    def define_custom_data(self):
        self.source_configure_reldir = 'squashfs-tools'
        return

    def builder_action_distribute_define_args(self, called_as, log):
        ret = [
            'install',
            'GZIP_SUPPORT=1',
            'XZ_SUPPORT=1',
            'LZO_SUPPORT=1',
            'INSTALL_DIR={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_dst_install_prefix(),
                    'bin'
                    )
                )
            ]
        return ret
