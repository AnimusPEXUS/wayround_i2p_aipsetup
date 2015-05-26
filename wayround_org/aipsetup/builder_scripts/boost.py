
import logging
import os.path
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std

# FIXME: host/build/target fix required


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return {}

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('bootstrap', self.builder_action_bootstrap),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_bootstrap(self, log):
        p = subprocess.Popen(
            [
                'bash',
                './bootstrap.sh',
                '--prefix=/usr',
                #                 '--with-python-version=3.3'
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()
        return ret

    def builder_action_build(self, log):
        p = subprocess.Popen(
            [
                os.path.join(self.src_dir, 'bjam'),
                '--prefix=' + os.path.join(self.dst_dir, 'usr'),
                #                    '--build-type=complete',
                #                    '--layout=versioned',
                'threading=multi',
                'link=shared',
                'stage',
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret

    def builder_action_distribute(self, log):
        p = subprocess.Popen(
            [
                os.path.join(self.src_dir, 'bjam'),
                '--prefix=' + os.path.join(self.dst_dir, 'usr'),
                #                    '--build-type=complete',
                #                    '--layout=versioned',
                'threading=multi',
                'link=shared',
                'install',
                ],
            cwd=self.src_dir,
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()
        return ret
