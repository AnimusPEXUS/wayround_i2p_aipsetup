
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
        self.forced_target = True
        return None

    def define_actions(self):
        ret = super().define_actions()
        if self.is_crossbuilder:
            ret['edit_package_info'] = self.builder_action_edit_package_info
            ret.move_to_end('edit_package_info', False)
        return ret

    def builder_action_edit_package_info(self, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        if name in ['glibc', None]:

            self.package_info['pkg_info']['name'] = \
                'cb-glibc-{target}'.format(
                    target=self.target
                    )

            bs = self.control

            bs.write_package_info(self.package_info)

        return ret

    def builder_action_configure_define_options(self, log):

        with_headers = '/usr/include'
        
        """
        if self.is_crossbuilder:
            with_headers = '/usr_all/include'
        """

        ret = super().builder_action_configure_define_options(log)

        """
        if self.is_crossbuilder:
            prefix = os.path.join(
                '/', 'usr', 'crossbuilders', self.target
                )

            ret = [
                '--prefix=' + prefix,
                '--mandir=' + os.path.join(prefix, 'share', 'man'),
                #'--sysconfdir=' +
                #self.package_info['constitution']['paths']['config'],
                #'--localstatedir=' +
                #self.package_info['constitution']['paths']['var'],
                '--enable-shared'
                ] + autotools.calc_conf_hbt_options(self)
        """

        ret += [
            '--enable-obsolete-rpc',
            '--enable-kernel=3.19',
            '--enable-tls',
            '--with-elf',
            '--enable-multi-arch',
            '--enable-multilib',
            # this is from configure --help. configure looking for
            # linux/version.h file
            #'--with-headers=/usr/src/linux/include',
            '--with-headers=' + with_headers,
            '--enable-shared'
            ]

        return ret

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
