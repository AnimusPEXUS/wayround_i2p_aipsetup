
import logging
import os.path
import time
import collections

import wayround_org.utils.file

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


# For history
# RUN[$j]='echo "CFLAGS += -march=i486 -mtune=native" > configparms

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        ret = dict()
        return ret

    def builder_action_configure(self, log):

        prefix = self.package_info['constitution']['paths']['usr']
        mandir = self.package_info['constitution']['paths']['man']
        sysconfdir = self.package_info['constitution']['paths']['config']
        localstatedir = self.package_info['constitution']['paths']['var']

        headers_path = '/usr/include'

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
                '--enable-obsolete-rpc',
                '--enable-kernel=3.19',
                '--enable-tls',
                '--with-elf',
                '--enable-multi-arch',

                # this is from configure --help. configure looking for
                # linux/version.h file

                #'--with-headers=/usr/src/linux/include',

                '--with-headers=' + headers_path,

                '--enable-shared',

                '--prefix=' + prefix,
                '--mandir=' + mandir,
                '--sysconfdir=' + sysconfdir,
                '--localstatedir=' + localstatedir,

                #'--host=' + self.host,
                #'--build=' + self.build,
                #'--target=' + self.target
                ] + wayround_org.aipsetup.build.calc_conf_hbt_options(self),
            arguments=[],
            environment={},
            environment_mode='copy',
            source_configure_reldir=self.source_configure_reldir,
            use_separate_buildding_dir=self.separate_build_dir,
            script_name='configure',
            run_script_not_bash=False,
            relative_call=False
            )
        return ret
