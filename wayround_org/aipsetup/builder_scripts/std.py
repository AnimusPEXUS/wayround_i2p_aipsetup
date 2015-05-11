
import logging
import os.path
import subprocess
import collections
import inspect
import time

import wayround_org.utils.file
import wayround_org.utils.log

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools


class Builder:

    def __init__(self, buildingsite):

        self.buildingsite = buildingsite

        bs = wayround_org.aipsetup.build.BuildingSiteCtl(buildingsite)

        self.package_info = bs.read_package_info()

        self.src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(
            buildingsite
            )

        self.bld_dir = wayround_org.aipsetup.build.getDIR_BUILDING(
            buildingsite
            )

        self.dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(
            buildingsite
            )

        self.log_dir = wayround_org.aipsetup.build.getDIR_BUILD_LOGS(
            buildingsite
            )

        self.tar_dir = wayround_org.aipsetup.build.getDIR_TARBALL(buildingsite)

        self.separate_build_dir = False

        self.source_configure_reldir = '.'

        self.is_crossbuild = (
            self.package_info['constitution']['target']
            != self.package_info['constitution']['host']
            )

        self.custom_data = self.define_custom_data()

        self.action_dict = self.define_actions()

        return

    @property
    def target(self):
        return self.package_info['constitution']['target']

    @property
    def host(self):
        return self.package_info['constitution']['host']

    @property
    def build(self):
        return self.package_info['constitution']['build']

    def print_help(self):
        txt = ''
        for i in self.action_dict.keys():
            txt += '{:40}    {}\n'.format(
                i,
                inspect.getdoc(self.action_dict[i])
                )
        print(txt)
        return 0

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('autogen', self.builder_action_autogen),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def get_defined_actions(self):
        return self.action_dict

    def define_custom_data(self):
        return {}

    def builder_action_src_cleanup(self, log):
        """
        Standard sources cleanup
        """

        if os.path.isdir(self.src_dir):
            log.info("cleaningup source dir")
            wayround_org.utils.file.cleanup_dir(self.src_dir)

        return 0

    def builder_action_bld_cleanup(self, log):
        """
        Standard building dir cleanup
        """

        if os.path.isdir(self.bld_dir):
            log.info("cleaningup building dir")
            wayround_org.utils.file.cleanup_dir(self.bld_dir)

        return 0

    def builder_action_dst_cleanup(self, log):
        """
        Standard destdir cleanup
        """

        if os.path.isdir(self.dst_dir):
            log.info("cleaningup destination dir")
            wayround_org.utils.file.cleanup_dir(self.dst_dir)

        return 0

    def builder_action_extract(self, log):
        """
        Standard sources extraction actions
        """

        ret = autotools.extract_high(
            self.buildingsite,
            self.package_info['pkg_info']['basename'],
            unwrap_dir=True,
            rename_dir=False
            )

        return ret

    def builder_action_patch(self, log):
        return 0

    def builder_action_autogen(self, log):
        ret = 0
        if not os.path.isfile(
                wayround_org.utils.path.join(
                    self.src_dir,
                    self.source_configure_reldir,
                    'configure'
                    )
                ):
            if os.path.isfile(
                    wayround_org.utils.path.join(
                        self.src_dir,
                        self.source_configure_reldir,
                        'autogen.sh'
                        )
                    ):
                p = subprocess.Popen(
                    ['./autogen.sh'],
                    cwd=os.path.join(
                        self.src_dir,
                        self.source_configure_reldir
                        )
                    )
                ret = p.wait()
            elif os.path.isfile(
                    wayround_org.utils.path.join(
                        self.src_dir,
                        self.source_configure_reldir,
                        'bootstrap'
                        )
                    ):
                p = subprocess.Popen(
                    ['./bootstrap'],
                    cwd=os.path.join(
                        self.src_dir,
                        self.source_configure_reldir
                        )
                    )
                ret = p.wait()
            else:
                log.error(
                    "./configure not found and no generators found"
                    )
                ret = 2
        return ret

    def builder_action_configure(self, log):

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
                '--prefix=' +
                self.package_info['constitution']['paths']['usr'],
                '--mandir=' +
                self.package_info['constitution']['paths']['man'],
                '--sysconfdir=' +
                self.package_info['constitution']['paths']['config'],
                '--localstatedir=' +
                self.package_info['constitution']['paths']['var'],
                '--enable-shared',
                # '--host=' + self.package_info['constitution']['host'],
                # '--build=' + self.package_info['constitution']['build'],
                # '--target=' + self.package_info['constitution']['target']
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

    def builder_action_build(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'install',
                'DESTDIR=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
