
import logging
import os.path
import subprocess
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        name = self.package_info['pkg_info']['name']

        if not name in ['qt4', 'qt5']:
            raise Exception("Invalid package name")

        return {
            'qt_number_str': name[-1],
            'etc_profile_set_dir': wayround_org.utils.path.join(
                self.dst_dir, 'etc', 'profile.d', 'SET'
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

    def builder_action_configure(self, log):

        p = subprocess.Popen(
            ['./configure'] +
            [
                '-opensource',
                '-confirm-license',
                '-prefix', '/usr/lib/qt{}_w_toolkit'.format(
                    self.custom_data['qt_number_str']
                    ),
                '-pulseaudio',
                '-no-alsa'
                ],
            stdin=subprocess.PIPE,
            cwd=self.src_dir
            )
        # p.communicate(input=b'yes\n')
        ret = p.wait()

        return ret

    def builder_action_distribute(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTALL_ROOT=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_environments(self, log):

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
                '009.qt{}'.format(qt_number_str)
                ),
            'w'
            )

        f.write("""\
#!/bin/bash
export PATH=$PATH:/usr/lib/qt{qtnum}_w_toolkit/bin

if [ "${{#PKG_CONFIG_PATH}}" -ne "0" ]; then
    PKG_CONFIG_PATH+=":"
fi
export PKG_CONFIG_PATH+="/usr/lib/qt{qtnum}_w_toolkit/lib/pkgconfig"

if [ "${{#LD_LIBRARY_PATH}}" -ne "0" ]; then
    LD_LIBRARY_PATH+=":"
fi
export LD_LIBRARY_PATH+="/usr/lib/qt{qtnum}_w_toolkit/lib"

""".format(qtnum=qt_number_str))
        f.close()

        return 0
