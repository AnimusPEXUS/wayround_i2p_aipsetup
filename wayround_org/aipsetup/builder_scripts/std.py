
import logging
import os.path
import subprocess
import collections
import inspect

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


class Builder:

    def __init__(self, buildingsite):

        self.buildingsite = buildingsite

        self.action_dict = self.define_actions()

        bs = wayround_org.aipsetup.build.BuildingSiteCtl(buildingsite)

        self.package_info = bs.read_package_info()

        self.src_dir = wayround_org.aipsetup.build.getDIR_SOURCE(
            buildingsite
            )

        self.dst_dir = wayround_org.aipsetup.build.getDIR_DESTDIR(
            buildingsite
            )

        self.tar_dir = wayround_org.aipsetup.build.getDIR_TARBALL(buildingsite)

        self.separate_build_dir = False

        self.source_configure_reldir = '.'

        self.custom_data = self.define_custom_data()

        return

    def print_help(self):
        txt = ''
        for i in self.action_dict.keys():
            txt += '{:20}    {}\n'.format(
                i,
                inspect.getdoc(self.action_dict[i])
                )
        print(txt)
        return 0

    def define_actions(self):
        return collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('patch', self.builder_action_patch),
            ('autogen', self.builder_action_autogen),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distribute', self.builder_action_distribute)
            ])

    def define_custom_data(self):
        return {}

    def run_action(self, action=None):
        ret = 0

        actions = self.action_dict.keys()

        if action is not None and isinstance(action, str):
            if action.endswith('+'):
                actions = actions[actions.index(action[:-1]):]
            else:
                actions = [actions[actions.index(action)]]

        for i in actions:
            logging.info(
                "======== Starting '{}' action".format(i)
                )
            try:
                ret = self.action_dict[i]()
            except:
                logging.exception(
                    "======== Exception on '{}' action".format(i)
                    )
                ret = 100
            else:
                logging.info(
                    "======== Finished '{}' action with code {}".format(
                        i, ret
                        )
                    )
            if ret != 0:
                break

        return ret

    def builder_action_src_cleanup(self):
        """
        Standard sources cleanup
        """

        if os.path.isdir(self.src_dir):
            logging.info("cleaningup source dir")
            wayround_org.utils.file.cleanup_dir(self.src_dir)

        return 0

    def builder_action_dst_cleanup(self):
        """
        Standard destdir cleanup
        """

        if os.path.isdir(self.src_dir):
            logging.info("cleaningup destination dir")
            wayround_org.utils.file.cleanup_dir(self.dst_dir)

        return 0

    def builder_action_extract(self):
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

    def builder_action_patch(self):
        return 0

    def builder_action_autogen(self):
        ret = 0
        if not os.path.isfile(os.path.join(self.src_dir, 'configure')):
            if not os.path.isfile(os.path.join(self.src_dir, 'autogen.sh')):
                logging.error(
                    "./configure not found and autogen.sh is absent"
                    )
                ret = 2
            else:
                p = subprocess.Popen(['./autogen.sh'], cwd=self.src_dir)
                ret = p.wait()
        return ret

    def builder_action_configure(self):
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
                '--host=' + self.package_info['constitution']['host'],
                '--build=' + self.package_info['constitution']['build'],
                # '--target=' + self.package_info['constitution']['target']
                ],
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

    def builder_action_build(self):
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

    def builder_action_distribute(self):
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
