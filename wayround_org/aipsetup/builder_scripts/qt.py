
import copy
import logging
import os.path
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std

# TODO: disable alsa, enable pulseaudio


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.apply_host_spec_compilers_options = True

        name = self.get_package_info()['pkg_info']['name']

        if not name in ['qt4', 'qt5']:
            raise Exception("Invalid package name")

        return {
            'qt_number_str': name[-1],
            'etc_profile_set_dir': wayround_org.utils.path.join(
                self.get_dst_dir(), 'etc', 'profile.d', 'SET'
                )
            }

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute),
            ('environments', self.builder_action_environments)
            ])

    def builder_action_configure(self, called_as, log):

        opts = [
            '-opensource',
            '-confirm-license',
            '-prefix', wayround_org.utils.path.join(
                self.calculate_install_prefix(),
                'opt',
                'qt',
                self.custom_data['qt_number_str']
                ),
            #'-openssl-linked',
            ]

        if self.custom_data['qt_number_str'] == '5':
            opts += [
                '-pulseaudio',
                '-no-alsa'
                ]

        p = subprocess.Popen(
            ['./configure'] + opts,
            env=copy.deepcopy(
                os.environ
                ).update(
                    self.all_automatic_flags_as_dict()
                    ),
            stdin=subprocess.PIPE,
            stdout=log.stdout,
            stderr=log.stderr,
            cwd=self.get_src_dir()
            )
        # p.communicate(input=b'yes\n')
        ret = p.wait()

        return ret

    #def builder_action_build_define_cpu_count(self, called_as, log):
    #    return 1

    def builder_action_distribute_define_args(self, called_as, log):
        return [
            'install',
            'INSTALL_ROOT={}'.format(self.get_dst_dir())
            ]

    def builder_action_environments(self, called_as, log):

        etc_profile_set_dir = self.custom_data['etc_profile_set_dir']
        qt_number_str = self.custom_data['qt_number_str']

        if not os.path.isdir(etc_profile_set_dir):
            try:
                os.makedirs(
                    etc_profile_set_dir,
                    exist_ok=True
                    )
            except:
                logging.error(
                    "Can't create dir: {}".format(
                        etc_profile_set_dir
                        )
                    )
                raise

        f = open(
            wayround_org.utils.path.join(
                etc_profile_set_dir,
                '009.qt{}.{}.{}.sh'.format(
                    qt_number_str,
                    self.get_host_from_pkgi(),
                    self.get_arch_from_pkgi()
                    )
                ),
            'w'
            )

        f.write("""\
#!/bin/bash
export PATH=$PATH:{arch_dir}/opt/qt/{qtnum}/bin

if [ "${{#PKG_CONFIG_PATH}}" -ne "0" ]; then
    PKG_CONFIG_PATH+=":"
fi
export PKG_CONFIG_PATH+="{arch_dir}/opt/qt/{qtnum}/lib/pkgconfig"
export PKG_CONFIG_PATH+=":{arch_dir}/opt/qt/{qtnum}/lib64/pkgconfig"
export PKG_CONFIG_PATH+=":{arch_dir}/opt/qt/{qtnum}/share/pkgconfig"

if [ "${{#LD_LIBRARY_PATH}}" -ne "0" ]; then
    LD_LIBRARY_PATH+=":"
fi
export LD_LIBRARY_PATH+="{arch_dir}/opt/qt/{qtnum}/lib"
export LD_LIBRARY_PATH+=":{arch_dir}/opt/qt/{qtnum}/lib64"

""".format(
                qtnum=qt_number_str,
                arch_dir=self.calculate_install_prefix()
                )
                )
        f.close()

        return 0
