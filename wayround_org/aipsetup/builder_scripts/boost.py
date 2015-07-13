
import copy
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
        e = copy.copy(os.environ)

        e['CXX'] = '{}-g++'.format(self.host_strong)
        e['CXXFLAGS'] = self.calculate_default_linker_program_gcc_parameter()

        ret = {
            'env': e,
            'BOOST_BUILD_PATH': self.src_dir,
            'user_config': os.path.join(self.src_dir, 'user-config.jam')
            }

        return ret

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('bootstrap', self.builder_action_bootstrap),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_configure(self, called_as, log):
        bitness = 32
        if self.host_strong.startswith('x86_64'):
            bitness = 64
        with open(self.custom_data['user_config'], 'w') as f:
            f.write("""
using gcc : : {compiler} : <compileflags>-m{bitness} <linkflags>-m{bitness} ;
""".format(
                compiler=wayround_org.utils.file.which(
                    '{}-g++'.format(self.host_strong),
                    self.host_multiarch_dir
                    ),
                bitness=bitness
                )
            )
        return 0

    def builder_action_bootstrap(self, called_as, log):
        p = subprocess.Popen(
            [
                'bash',
                './bootstrap.sh',
                '--prefix={}'.format(self.host_multiarch_dir),
                #                 '--with-python-version=3.3'
                ],
            cwd=self.src_dir,
            env=self.custom_data['env'],
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()
        return ret

    def builder_action_build(self, called_as, log):
        p = subprocess.Popen(
            [
                os.path.join(self.src_dir, 'b2'),
                # NOTE: this is not an error:
                #       prefix = self.dst_host_multiarch_dir
                '--prefix={}'.format(self.dst_host_multiarch_dir),
                #                    '--build-type=complete',
                #                    '--layout=versioned',
                #'--build-dir={}'.format(self.bld_dir),
                '--user-config={}'.format(self.custom_data['user_config']),
                'threading=multi',
                'link=shared',
                'stage',
                ],
            cwd=self.src_dir,
            env=self.custom_data['env'],
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret

    def builder_action_distribute(self, called_as, log):
        p = subprocess.Popen(
            [
                os.path.join(self.src_dir, 'b2'),
                '--prefix={}'.format(self.dst_host_multiarch_dir),
                #                    '--build-type=complete',
                #                    '--layout=versioned',
                #'--build-dir={}'.format(self.bld_dir),
                '--user-config={}'.format(self.custom_data['user_config']),
                'threading=multi',
                'link=shared',
                'install',
                ],
            cwd=self.src_dir,
            env=self.custom_data['env'],
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()
        return ret
