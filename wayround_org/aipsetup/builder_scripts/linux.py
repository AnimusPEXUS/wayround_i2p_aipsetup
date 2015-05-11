
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
        ret = dict()
        ret['src_arch_dir'] = wayround_org.utils.path.join(
            self.src_dir, 'arch'
            )
        ret['dst_boot_dir'] = wayround_org.utils.path.join(
            self.dst_dir, 'boot'
            )
        ret['dst_man_dir'] = wayround_org.utils.path.join(
            self.dst_dir, 'usr', 'share', 'man', 'man9'
            )
        return ret

    def define_actions(self):
        return collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('extract', self.builder_action_extract),
            ('configure', self.builder_action_configure),
            ('build', self.builder_action_build),
            ('distr_kernel', self.builder_action_distr_kernel),
            ('distr_modules', self.builder_action_distr_modules),
            ('distr_firmware', self.builder_action_distr_firmware),

            # ('distr_headers_internal',
            #       self.builder_action_distr_headers_internal),

            ('distr_headers_normal', self.builder_action_distr_headers_normal),

            # ('distr_headers_internal_repeat',
            #       self.builder_action_distr_headers_internal_repeat),
            # ('distr_arch_headers_internal',
            #       self.builder_action_distr_arch_headers_internal),
            # ('remove_install_files_from_includes',
            #       self.builder_action_remove_install_files_from_includes),

            ('distr_man', self.builder_action_distr_man),
            ('copy_source', self.builder_action_copy_source)
            ])

    def builder_action_dst_cleanup(self, log):
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

    def builder_action_configure(self, log):
        logging.info("You now need to configure kernel by your needs and")
        logging.info("continue building procedure with command")
        logging.info("'aipsetup build continue build+'")
        return 1

    def builder_action_distr_kernel(self, log):
        if not os.path.exists(self.custom_data['dst_boot_dir']):
            os.makedirs(self.custom_data['dst_boot_dir'])

        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'install',
                'INSTALL_PATH=' + self.custom_data['dst_boot_dir']
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )

        if ret == 0:

            os.rename(
                wayround_org.utils.path.join(
                    self.custom_data['dst_boot_dir'],
                    'vmlinuz'
                    ),
                wayround_org.utils.path.join(
                    dst_boot_dir,
                    'vmlinuz-{}'.format(
                        self.package_info['pkg_nameinfo']['groups']['version']
                        )
                    )
                )
        return ret

    def builder_action_distr_modules(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'modules_install',
                'INSTALL_MOD_PATH=' + self.dst_dir
                ],
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
                            os.path.sep + 'usr',
                            'src',
                            'linux-{}'.format(
                                self.package_info['pkg_nameinfo'][
                                    'groups']['version']
                                )
                            ),
                        new_link
                        )

        return ret

    def builder_action_distr_firmware(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'firmware_install',
                'INSTALL_MOD_PATH=' + self.dst_dir
                ],
            environment={},
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distr_headers_internal(self, log):
        wayround_org.utils.file.copytree(
            wayround_org.utils.path.join(self.src_dir, 'include'),
            wayround_org.utils.path.join(self.dst_dir, 'usr', 'include'),
            overwrite_files=False,
            clear_before_copy=False,
            dst_must_be_empty=False
            )
        return ret

    def builder_action_distr_headers_normal(self, log):

        ret = 0
        arch_params = []
        install_hdr_path = wayround_org.utils.path.join(self.dst_dir, 'usr')

        if self.is_crossbuild:

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

            arch_params += ['ARCH=' + linux_headers_arch]

            install_hdr_path = wayround_org.utils.path.join(
                self.dst_dir, 'usr', 'lib', 'unicorn_crossbuilders',
                target, 'usr'
                )

        if ret == 0:

            ret = autotools.make_high(
                self.buildingsite,
                log=log,
                options=[],
                arguments=[
                    'headers_install',
                    # 'headers_install_all',
                    'INSTALL_HDR_PATH=' + install_hdr_path
                    ] + arch_params,
                environment={},
                environment_mode='copy',
                use_separate_buildding_dir=self.separate_build_dir,
                source_configure_reldir=self.source_configure_reldir
                )
        return ret

    def builder_action_distr_headers_internal_repeat(self, log):

        wayround_org.utils.file.copytree(
            wayround_org.utils.path.join(self.src_dir, 'include'),
            wayround_org.utils.path.join(self.dst_dir, 'usr', 'include'),
            overwrite_files=False,
            clear_before_copy=False,
            dst_must_be_empty=False
            )

        return ret

    def builder_action_distr_arch_headers_internal(self, log):
        archs = os.listdir(self.custom_data['src_arch_dir'])
        archs.sort()
        for i in archs[:]:
            fp = wayround_org.utils.path.join(
                self.custom_data['src_arch_dir'],
                i
                )
            if not os.path.isdir(fp) or os.path.islink(fp):
                archs.remove(i)

        for i in archs:
            fp = wayround_org.utils.path.join(
                self.custom_data['src_arch_dir'], i, 'include', 'asm'
                )

            if os.path.isdir(fp):

                wayround_org.utils.file.copytree(
                    fp,
                    wayround_org.utils.path.join(
                        self.dst_dir, 'usr', 'include', 'asm-{}'.format(i)
                        ),
                    overwrite_files=False,
                    clear_before_copy=False,
                    dst_must_be_empty=False
                    )

        log.info("""
Please make correct 04.DESTDIR/usr/include/asm by 'ln -s' manually.

Continue with command
'aipsetup3 build continue remove_install_files_from_includes+'
""")

        ret = 1
        return ret

    def builder_action_remove_install_files_from_includes(self, log):
        p = subprocess.Popen(
            ['find',
             '(', '-name', '.install',
             '-o', '-name', '..install.cmd',
             '-o', '-name', '.check',
             '-o', '-name', '..check.cmd',
             '-o', '-name', 'Kbuild',
             ')',
             '-delete'],
            cwd=wayround_org.utils.path.join(
                self.dst_dir,
                'usr',
                'include'
                )
            )
        p.wait()
        return ret

    def builder_action_distr_man(self, log):
        ret = autotools.make_high(
            self.buildingsite,
            options=[],
            arguments=[
                'mandocs'
                ],
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

    def builder_action_copy_source(self, log):
        try:
            ret = wayround_org.utils.file.copytree(
                self.src_dir,
                wayround_org.utils.path.join(
                    self.dst_dir,
                    'usr',
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
                        'usr',
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
