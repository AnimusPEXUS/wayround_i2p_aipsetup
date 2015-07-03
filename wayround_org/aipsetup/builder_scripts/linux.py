
import glob
import logging
import os.path
import shutil
import subprocess
import collections
import re

import wayround_org.utils.file
import wayround_org.utils.path
import wayround_org.utils.system_type

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):

        self.usr_list_item = ['usr']
        if self.is_crossbuilder:
            self.usr_list_item[0] = ''

        ret = dict()
        ret['src_arch_dir'] = wayround_org.utils.path.join(
            self.src_dir, 'arch'
            )
        ret['dst_boot_dir'] = wayround_org.utils.path.join(
            self.dst_dir, 'boot'
            )
        ret['dst_man_dir'] = wayround_org.utils.path.join(
            self.dst_dir, self.usr_list_item[0], 'share', 'man', 'man9'
            )

        crossbuild_arch_params = []

        target = self.package_info['constitution']['target']

        st = wayround_org.utils.system_type.SystemType(target)
        cpu = st.cpu

        # print("cpu: {}".format(cpu))
        linux_headers_arch = None
        if re.match(r'^i[4-6]86$', cpu) or re.match(r'^x86(_32)?$', cpu):
            linux_headers_arch = 'x86'
        elif re.match(r'^x86_64$', cpu):
            linux_headers_arch = 'x86_64'
        else:
            logging.error("Don't know which linux ARCH apply")
            ret = 3

        if self.is_crossbuild or self.is_crossbuilder:
            crossbuild_arch_params += [
                'ARCH=' + linux_headers_arch,
                'CROSS_COMPILE={}-'.format(self.host)
                ]

        ret['crossbuild_arch_params'] = crossbuild_arch_params

        return ret

    def define_actions(self):

        ret = collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distr_kernel', self.builder_action_distr_kernel),
            ('distr_modules', self.builder_action_distr_modules),
            ('distr_firmware', self.builder_action_distr_firmware),

            ('distr_headers_all', self.builder_action_distr_headers_all),

            ('distr_man', self.builder_action_distr_man),
            ('copy_source', self.builder_action_copy_source)
            ])

        if self.is_crossbuilder:

            logging.info(
                "Crosscompiler building detected. only headers will be built"
                )

            ret = collections.OrderedDict([
                ('src_cleanup', self.builder_action_src_cleanup),
                ('dst_cleanup', self.builder_action_dst_cleanup),
                ('extract', self.builder_action_extract),

                ('distr_headers_all', self.builder_action_distr_headers_all),
                ])

        ret['edit_package_info'] = self.builder_action_edit_package_info
        ret.move_to_end('edit_package_info', False)

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        pi = self.package_info

        if self.is_crossbuilder:
            pi['pkg_info']['name'] = 'cb-linux-headers-{}'.format(self.target)
        else:
            pi['pkg_info']['name'] = 'linux'

        # pi['pkg_info']['skip_interpreter_editing'] = True

        self.control.write_package_info(pi)

        return ret

    def builder_action_dst_cleanup(self, called_as, log):
        """
        Standard destdir cleanup
        """
        if self.is_crossbuild:
            logging.info(
                "Destination directory cleanup skipped doe to "
                "'crossbuilder_mode'"
                )
        else:

            if os.path.isdir(self.src_dir):
                logging.info("cleaningup destination dir")
                wayround_org.utils.file.cleanup_dir(self.dst_dir)

        return 0

    def builder_action_configure(self, called_as, log):
        log.info("""
You now need to configure kernel by your needs and
continue building procedure with command
'aipsetup build continue build+'
""")
        return 1

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[] + self.custom_data['crossbuild_arch_params'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distr_kernel(self, called_as, log):
        if not os.path.exists(self.custom_data['dst_boot_dir']):
            os.makedirs(self.custom_data['dst_boot_dir'])

        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'INSTALL_PATH=' + self.custom_data['dst_boot_dir']
                ] + self.custom_data['crossbuild_arch_params'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        if ret == 0:

            p1 = wayround_org.utils.path.join(
                self.custom_data['dst_boot_dir'],
                'vmlinuz'
                )

            p2 = wayround_org.utils.path.join(
                self.custom_data['dst_boot_dir'],
                'vmlinuz-{}-{}'.format(
                    self.package_info['pkg_nameinfo']['groups']['version'],
                    self.host
                    )
                )

            log.info("Renaming: `{}' to `{}'".format(p1, p2))

            os.rename(p1, p2)
        return ret

    def builder_action_distr_modules(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'modules_install',
                'INSTALL_MOD_PATH=' + self.dst_dir
                ] + self.custom_data['crossbuild_arch_params'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        if ret == 0:

            modules_dir = wayround_org.utils.path.join(
                self.dst_dir, 'lib', 'modules'
                )

            files = os.listdir(modules_dir)

            if len(files) != 1:
                logging.error(
                    "Can't find directory in {}".format(modules_dir)
                    )
                ret = 1
            else:
                modules_dir = \
                    wayround_org.utils.path.join(modules_dir, files[0])

                for i in ['build', 'source']:

                    new_link = wayround_org.utils.path.join(
                        modules_dir,
                        i
                        )

                    wayround_org.utils.file.remove_if_exists(new_link)

                    os.symlink(
                        wayround_org.utils.path.join(
                            os.path.sep + self.usr_list_item[0],
                            'src',
                            'linux-{}'.format(
                                self.package_info['pkg_nameinfo'][
                                    'groups']['version']
                                )
                            ),
                        new_link
                        )

        return ret

    def builder_action_distr_firmware(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'firmware_install',
                'INSTALL_MOD_PATH=' + self.dst_dir
                ] + self.custom_data['crossbuild_arch_params'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def _builder_action_distr_headers_001(self, called_as, log, h_all=False):

        ret = 0

        command = 'headers_install'
        if h_all:
            command = 'headers_install_all'

        install_hdr_path = wayround_org.utils.path.join(
            self.dst_dir, 'usr'
            )

        if self.is_crossbuilder:

            install_hdr_path = wayround_org.utils.path.join(
                self.dst_dir, 'usr', 'crossbuilders',
                self.target
                #, usr
                )

        if ret == 0:

            ret = autotools.make_high(
                self.buildingsite,
                log=log,
                options=[],
                arguments=[command] +
                ['INSTALL_HDR_PATH=' + install_hdr_path] +
                self.custom_data['crossbuild_arch_params'],
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=self.separate_build_dir,
                source_configure_reldir=self.source_configure_reldir
                )

        if h_all:
            print('-----------------')
            print("Now You need to create asm symlink in include dir")
            if self.is_crossbuilder:
                print("and pack this building site")
            if not self.is_crossbuilder and not self.is_crossbuild:
                print("and continue with 'distr_man+' action")
            print('-----------------')
            ret = 1

        return ret

    def builder_action_distr_headers_normal(self, called_as, log):
        return self._builder_action_distr_headers_001(
            called_as,
            log,
            h_all=False
            )

    def builder_action_distr_headers_all(self, called_as, log):
        return self._builder_action_distr_headers_001(
            called_as,
            log,
            h_all=True
            )

    def builder_action_distr_man(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'mandocs'
                ] + self.custom_data['crossbuild_arch_params'],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        if ret == 0:

            if not os.path.isdir(self.custom_data['dst_man_dir']):
                os.makedirs(self.custom_data['dst_man_dir'])

            man_files = glob.glob(
                wayround_org.utils.path.join(
                    self.src_dir, 'Documentation', 'DocBook', 'man', '*.9.gz'
                    )
                )

            man_files.sort()

            logging.info("Copying {} man file(s)".format(len(man_files)))

            for i in man_files:
                base = os.path.basename(i)
                logging.info("copying {}".format(base))
                shutil.copy(
                    wayround_org.utils.path.join(i),
                    wayround_org.utils.path.join(
                        self.custom_data['dst_man_dir'],
                        base
                        )
                    )
        return ret

    def builder_action_copy_source(self, called_as, log):
        try:
            ret = wayround_org.utils.file.copytree(
                self.src_dir,
                wayround_org.utils.path.join(
                    self.dst_dir,
                    self.usr_list_item[0],
                    'src',
                    'linux-{}'.format(
                        self.package_info['pkg_nameinfo']['groups']['version']
                        )
                    ),
                overwrite_files=True,
                clear_before_copy=True,
                dst_must_be_empty=False
                )
        except:
            logging.exception("Some error")
            ret = 2
        else:
            if ret == 0:
                try:
                    new_link = wayround_org.utils.path.join(
                        self.dst_dir,
                        self.usr_list_item[0],
                        'src',
                        'linux'
                        )

                    wayround_org.utils.file.remove_if_exists(new_link)

                    os.symlink(
                        '.{}linux-{}'.format(
                            os.path.sep,
                            self.package_info['pkg_nameinfo'][
                                'groups']['version']
                            ),
                        new_link
                        )
                except:
                    logging.exception("Some error")
                    ret = 3
        return ret
