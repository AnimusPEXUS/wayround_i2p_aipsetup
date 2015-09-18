
import copy
import os.path
import subprocess
import collections
import pprint

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std

# BIG FAT WARNING: on x86_64 with multilib configured GCC boost libs
#                  MUST be installed into lib64 subdir of sysroot,
#                  else you will got some packages tending to be
#                  linked ageinst 32-bit libs under 32-bit lib dir: at
#                  least libtool do so for source-highlite package


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        e = self.builder_action_build_define_environment(None, None)

        print("env: {}".format(pprint.pformat(e)))

        e = wayround_org.utils.osutils.env_vars_edit(e, 'copy')

        # e.update(self.builder_action_configure_define_PATH_dict())

        e['CXX'] = '{}-g++'.format(self.get_host_from_pkgi())
        #e['CXXFLAGS'] = self.calculate_default_linker_program_gcc_parameter()

        ret = {
            'env': e,
            'BOOST_BUILD_PATH': self.get_src_dir(),
            'user_config': wayround_org.utils.path.join(
                self.get_src_dir(),
                'user-config.jam'
                ),
            'python': wayround_org.utils.file.which(
                'python2',
                self.calculate_install_prefix()
                )
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
        if self.get_arch_from_pkgi().startswith('x86_64'):
            bitness = 64

        with open(self.custom_data['user_config'], 'w') as f:
            f.write(
                """
using gcc : : {compiler} : <compileflags>-m{bitness} <linkflags>-m{bitness} ;
""".format(
                    compiler=wayround_org.utils.file.which(
                        '{}-g++'.format(self.get_host_from_pkgi()),
                        self.get_host_dir()
                        ),
                    bitness=bitness
                    )
            )
        return 0

    def builder_action_bootstrap(self, called_as, log):

        args = [
            'bash',
            './bootstrap.sh',
            '--prefix={}'.format(self.calculate_install_prefix()),
            '--libdir={}'.format(self.calculate_install_libdir()),
            '--with-python={}'.format(self.custom_data['python']),
            #                 '--with-python-version=3.3'
            ]

        log.info("cmd: {}".format(pprint.pformat(args)))

        p = subprocess.Popen(
            args,
            cwd=self.get_src_dir(),
            env=self.custom_data['env'],
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret

    def builder_action_build(self, called_as, log):

        args = [
            wayround_org.utils.path.join(self.get_src_dir(), 'b2'),
            # NOTE: this is not an error:
            #       prefix = self.calculate_dst_install_prefix()
            '--prefix={}'.format(self.calculate_dst_install_prefix()),
            '--libdir={}'.format(self.calculate_dst_install_libdir()),
            #                    '--build-type=complete',
            #                    '--layout=versioned',
            #'--build-dir={}'.format(self.bld_dir),

            # NOTE: boost configurer and it's docs is crappy shit..
            #       thanks to Sergey Popov from Gentoo for pointing
            #       on --user-config= option
            '--user-config={}'.format(self.custom_data['user_config']),
            #'--with-python={}'.format(self.custom_data['python']),
            'threading=multi',
            'link=shared',
            'stage',
            ]

        log.info(
            pprint.pformat(args)
            )

        p = subprocess.Popen(
            args,
            cwd=self.get_src_dir(),
            env=self.custom_data['env'],
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()

        return ret

    def builder_action_distribute(self, called_as, log):
        args = [
            wayround_org.utils.path.join(self.get_src_dir(), 'b2'),
            '--prefix={}'.format(self.calculate_dst_install_prefix()),
            '--libdir={}'.format(self.calculate_dst_install_libdir()),
            #                    '--build-type=complete',
            #                    '--layout=versioned',
            #'--build-dir={}'.format(self.bld_dir),
            '--user-config={}'.format(self.custom_data['user_config']),
            #'--with-python={}'.format(self.custom_data['python']),
            'threading=multi',
            'link=shared',
            'install',
            ]
        log.info(
            pprint.pformat(args)
            )
        p = subprocess.Popen(
            args,
            cwd=self.get_src_dir(),
            env=self.custom_data['env'],
            stdout=log.stdout,
            stderr=log.stderr
            )

        ret = p.wait()
        return ret
