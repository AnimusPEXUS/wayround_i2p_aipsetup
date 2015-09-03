
import os.path
import collections

import wayround_org.aipsetup.buildtools.autotools as autotools

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        return collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'prefix={}'.format(self.calculate_dst_install_prefix()),
            #'BINDIR={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_dst_host_dir(),
            #        'bin'
            #        )
            #    ),
            #'MANDIR={}'.format(
            #    wayround_org.utils.path.join(
            #        self.get_dst_host_arch_dir(),
            #        'share',
            #        'man',
            #        'man1'
            #        )
            #    )
            ]
