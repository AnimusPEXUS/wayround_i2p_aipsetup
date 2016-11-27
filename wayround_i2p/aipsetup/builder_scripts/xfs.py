

import logging
import os.path
import collections

import wayround_i2p.utils.path
import wayround_i2p.aipsetup.builder_scripts.std
import wayround_i2p.aipsetup.buildtools.autotools as autotools
import wayround_i2p.utils.file


class Builder(wayround_i2p.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure(self, called_as, log):
        log.info(
            "Detected (and accepted) basename is: [{}]".format(
                self.get_package_info()['pkg_info']['basename']
                )
            )
        return super().builder_action_configure(called_as, log)

    def builder_action_distribute_define_args(self, called_as, log):
        opt_args = []

        if (not self.get_package_info()['pkg_info']['basename']
                in ['xfsprogs', 'xfsdump', 'dmapi']):
            opt_args.append('install-lib')

        ret = ['install', 'install-dev'] + \
            opt_args + \
            ['DESTDIR={}'.format(self.get_dst_dir())]
        return ret
