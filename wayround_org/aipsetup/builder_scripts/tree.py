
import logging
import os.path
import subprocess
import collections
import inspect

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

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

    def builder_action_build(self):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'install',
                'prefix=' + os.path.join(self.dst_dir, 'usr'),
                'BINDIR=' + os.path.join(self.dst_dir, 'usr', 'bin'),
                'MANDIR=' + os.path.join(
                    self.dst_dir,
                    'usr',
                    'share',
                    'man',
                    'man1'
                    )
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
