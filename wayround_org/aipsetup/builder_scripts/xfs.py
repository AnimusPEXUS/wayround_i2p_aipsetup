

import logging
import os.path
import collections

import wayround_org.utils.path
import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure(self, called_as, log):
        log.info(
            "Detected (and accepted) basename is: [{}]".format(
                self.package_info['pkg_info']['basename']
                )
            )
        return super().builder_action_configure(called_as, log)

    def builder_action_distribute(self, called_as, log):

        opt_args = []

        if (not self.package_info['pkg_info']['basename']
                in ['xfsprogs', 'xfsdump', 'dmapi']):
            opt_args.append('install-lib')

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=['install', 'install-dev']
            + opt_args
            + ['DESTDIR={}'.format(self.dst_dir)],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
