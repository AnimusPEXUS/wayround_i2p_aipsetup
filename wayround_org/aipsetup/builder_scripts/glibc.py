
import logging
import os.path
import time
import collections

import wayround_org.utils.file
import wayround_org.utils.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


# For history
# RUN[$j]='echo "CFLAGS += -march=i486 -mtune=native" > configparms

class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.separate_build_dir = True
        return None

    def builder_action_configure_define_options(self, log):

        with_headers = '/usr/include'
        if self.is_crossbuild:
            with_headers = wayround_org.utils.path.join(
                self.target_host_root,
                with_headers
                )

        return super().builder_action_configure_define_options(log) + [
            '--enable-obsolete-rpc',
            '--enable-kernel=3.19',
            '--enable-tls',
            '--with-elf',
            '--enable-multi-arch',
            # this is from configure --help. configure looking for
            # linux/version.h file
            #'--with-headers=/usr/src/linux/include',
            '--with-headers=' + with_headers,
            '--enable-shared'
            ]

    def builder_action_distribute(self, log):
        
        ret = super().builder_action_distribute(log)

        if ret == 0:

            try:
                os.rename(
		    os.path.join(self.dst_dir, 'etc', 'ld.so.cache'),
		    os.path.join(self.dst_dir, 'etc', 'ld.so.cache.distr')
                    )
            except:
                log.exception("Can't rename ld.so.cache file")

        return ret
