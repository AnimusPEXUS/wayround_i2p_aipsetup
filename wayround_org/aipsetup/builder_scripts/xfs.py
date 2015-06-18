

import logging
import os.path
import collections

import wayround_org.utils.path
import wayround_org.aipsetup.builder_scripts.std
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    """
    """

    """
    def define_custom_data(self):
        return {'subset': 'acl'}
    """

    """
    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('autogen', self.builder_action_autogen),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])
    """

    def builder_action_configure_define_options(self, called_as, log):
        copts = []
        if self.is_crossbuild:
            copts +=[
                #'--with-sysroot={}'.format(
                #    wayround_org.utils.path.join(
                #        self.target_host_root,
                #        '/usr'
                #        )
                #    )
                ]
        return super().builder_action_configure_define_options(log) + copts

    def builder_action_configure(self, called_as, log):
        log.info(
            "Detected (and accepted) basename is: [{}]".format(
                self.package_info['pkg_info']['basename']
                )
            )
        return super().builder_action_configure(log)

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
            + ['DESTDIR=' + self.dst_dir],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
