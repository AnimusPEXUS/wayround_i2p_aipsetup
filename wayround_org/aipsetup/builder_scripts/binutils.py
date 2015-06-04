
import logging
import os.path
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        return None

    def builder_action_extract(self, log, rename_dir_additional_prefix=None):

        ret = super().builder_action_extract(
            log
            )

        if ret == 0:

            for i in ['gmp', 'mpc', 'mpfr', 'isl', 'cloog']:

                if autotools.extract_high(
                        self.buildingsite,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    log.error("Can't extract component: {}".format(i))
                    ret = 2

        return ret

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
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
            '--enable-gold',
            ]
