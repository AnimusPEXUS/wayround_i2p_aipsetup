
import logging
import os.path
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = dict()
        return ret

    def builder_action_configure(self, log):

        prefix = self.package_info['constitution']['paths']['usr']
        mandir = self.package_info['constitution']['paths']['man']
        sysconfdir = self.package_info['constitution']['paths']['config']
        localstatedir = self.package_info['constitution']['paths']['var']

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
                #'--enable-targets='
                #'i486-pc-linux-gnu,'
                # 'i586-pc-linux-gnu,'
                # 'i686-pc-linux-gnu,'
                # 'i786-pc-linux-gnu,'
                # 'ia64-pc-linux-gnu,'
                #'x86_64-pc-linux-gnu,'
                #'aarch64-linux-gnu',

                '--enable-targets=all',

                # WARNING: enabling this will cause problem on building native
                #          GCC
                #'--with-sysroot',

                #                    '--disable-libada',
                #                    '--enable-bootstrap',
                '--enable-64-bit-bfd',
                '--disable-werror',
                '--enable-libada',
                '--enable-libssp',
                '--enable-objc-gc',

                '--enable-lto',
                '--enable-ld',
                #'--enable-gold',

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
