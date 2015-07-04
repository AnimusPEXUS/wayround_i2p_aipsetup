
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

        bs = wayround_org.aipsetup.build.BuildingSiteCtl(buildingsite)

        # this is for glibc case, when package_info `host' should stay same
        # as `build', but ./configure --host must be different
        self.internal_host_redefinition = None

        self.control = bs

        self.separate_build_dir = False

        self.source_configure_reldir = '.'

        self.forced_target = False

        self.custom_data = self.define_custom_data()

        self.action_dict = self.define_actions()

        return

    @property
    def buildingsite(self):
        return self.control.path

    @property
    def package_info(self):
        # TODO: make cache
        return self.control.read_package_info()

    @property
    def src_dir(self):
        return self.control.getDIR_SOURCE()

    @property
    def bld_dir(self):
        return self.control.getDIR_BUILDING()

    @property
    def patches_dir(self):
        return self.control.getDIR_PATCHES()

    @property
    def dst_dir(self):
        return self.control.getDIR_DESTDIR()

    @property
    def log_dir(self):
        return self.control.getDIR_BUILD_LOGS()

    @property
    def tar_dir(self):
        return self.control.getDIR_TARBALL()

    @property
    def is_crossbuild(self):
        return (self.package_info['constitution']['build']
                != self.package_info['constitution']['host'])

    @property
    def is_crossbuilder(self):
        return (
            self.package_info['constitution']['target']
            != self.package_info['constitution']['host']
            # if not commented - crossbuild considered as crossbuilder by
            # autotools configure script
            # or self.package_info['constitution']['target']
            # != self.package_info['constitution']['build']
            )

    @property
    def target(self):
        return self.package_info['constitution']['target']

    @property
    def host(self):
        ret = self.package_info['constitution']['host']
        if self.internal_host_redefinition is not None:
            ret = self.internal_host_redefinition
        return ret

    @property
    def host_strong(self):
        return self.package_info['constitution']['host']

    @property
    def build(self):
        return self.package_info['constitution']['build']

    def calculate_default_linker_program(self):
        ret = wayround_org.aipsetup.build.find_dl(
            os.path.join(
                '/',
                'multiarch',
                self.host
                )
            )
        return ret

    def calculate_default_linker_program_ld_parameter(self):
        return '--dynamic-linker=' + self.calculate_default_linker_program()

    def calculate_default_linker_program_gcc_parameter(self):
        return '-Wl,' + self.calculate_default_linker_program_ld_parameter()

    def print_help(self):
        txt = ''
        print("building script: {}".format(self))
        print('{:40}    {}'.format('[command]', '[comment]'))
        for i in self.action_dict.keys():
            txt += '{:40}    {}\n'.format(
                i,
                inspect.getdoc(self.action_dict[i])
                )
        print(txt)
        return 0

    def get_defined_actions(self):
        return self.action_dict

    def define_custom_data(self):
        return None

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

    def builder_action_src_cleanup(self, called_as, log):
        """
        Standard sources cleanup
        """

        if os.path.isdir(self.src_dir):
            log.info("cleaningup source dir")
            wayround_org.utils.file.cleanup_dir(self.src_dir)

        return 0

    def builder_action_bld_cleanup(self, called_as, log):
        """
        Standard building dir cleanup
        """

        if os.path.isdir(self.bld_dir):
            log.info("cleaningup building dir")
            wayround_org.utils.file.cleanup_dir(self.bld_dir)

        return 0

    def builder_action_dst_cleanup(self, called_as, log):
        """
        Standard destdir cleanup
        """

        if os.path.isdir(self.dst_dir):
            log.info("cleaningup destination dir")
            wayround_org.utils.file.cleanup_dir(self.dst_dir)

        return 0

    def builder_action_extract(self, called_as, log):
        """
        Standard sources extraction actions
        """

        ret = autotools.extract_high(
            self.buildingsite,
            self.package_info['pkg_info']['basename'],
            log=log,
            unwrap_dir=True,
            rename_dir=False
            )

        return ret

    def builder_action_patch(self, called_as, log):
        return 0

    def builder_action_autogen(self, called_as, log):
        cfg_script_name = self.builder_action_configure_define_script_name(
            called_as,
            log)
        ret = 0
        if os.path.isfile(
                wayround_org.utils.path.join(
                    self.src_dir,
                    self.source_configure_reldir,
                    cfg_script_name
                    )
                ):
            log.info(
                "./{} found. generator will not be used".format(
                    cfg_script_name
                    )
                )
        else:
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
                        ),
                    stdout=log.stdout,
                    stderr=log.stderr
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
                        ),
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                ret = p.wait()
            elif os.path.isfile(
                    wayround_org.utils.path.join(
                        self.src_dir,
                        self.source_configure_reldir,
                        'configure.ac'
                        )
                    ):
                p = subprocess.Popen(
                    ['autoconf'],
                    cwd=os.path.join(
                        self.src_dir,
                        self.source_configure_reldir
                        ),
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                ret = p.wait()
            elif os.path.isfile(
                    wayround_org.utils.path.join(
                        self.src_dir,
                        self.source_configure_reldir,
                        'configure.in'
                        )
                    ):
                p = subprocess.Popen(
                    ['autoconf'],
                    cwd=os.path.join(
                        self.src_dir,
                        self.source_configure_reldir
                        ),
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                ret = p.wait()
            else:
                log.error(
                    "./{} not found and no generators found".format(
                        cfg_script_name
                        )
                    )
                ret = 2
        return ret

    def builder_action_configure_define_options(self, called_as, log):
        """
        """

        """
        rpath = os.path.join(
            '/',
            'multiarch',
            self.host,
            'lib'
            )
        """

        ret = [
            '--prefix=' + os.path.join('/', 'multiarch', self.host),
            '--includedir=' +
            os.path.join(
                '/',
                'multiarch',
                self.host,
                'include'
                ),
            '--libdir=' + os.path.join('/', 'multiarch', self.host, 'lib'),
            '--mandir=' + os.path.join(
                '/',
                'multiarch',
                self.host,
                'share',
                'man'
                ),
            '--sysconfdir=/etc',
            # '--sysconfdir=' + os.path.join(
            #     '/',
            #     'multiarch',
            #     self.host,
            #     'etc'
            #     ),
            '--localstatedir=/var',
            '--enable-shared',

            # TODO: find way to modify binutils+gcc+glibc chane so it
            #       uses needed interpreter without this f*ckin parameter...
            'LDFLAGS=' + self.calculate_default_linker_program_gcc_parameter()

            #'LDFLAGS=-Wl,--dynamic-linker=' + \
            #    dl + \
            #    ' -Wl,-rpath={}'.format(rpath) + \
            #    ' -Wl,-rpath-link={}'.format(rpath)
            ] + autotools.calc_conf_hbt_options(self)

        return ret

    def builder_action_configure_define_script_name(self, called_as, log):
        return 'configure'

    def builder_action_configure_define_run_script_not_bash(
            self, called_as, log):
        return False

    def builder_action_configure_define_relative_call(self, called_as, log):
        return False

    def builder_action_configure_define_environment(self, called_as, log):
        return {}

    def builder_action_make_define_environment(self, called_as, log):
        return self.builder_action_configure_define_environment(called_as, log)

    def builder_action_configure(self, called_as, log):

        defined_options = \
            self.builder_action_configure_define_options(called_as, log)
        defined_script_name = \
            self.builder_action_configure_define_script_name(called_as, log)

        ret = autotools.configure_high(
            self.buildingsite,
            log=log,
            options=defined_options,
            arguments=[],
            environment=self.builder_action_configure_define_environment(
                called_as,
                log),
            environment_mode='copy',
            source_configure_reldir=self.source_configure_reldir,
            use_separate_buildding_dir=self.separate_build_dir,
            script_name=defined_script_name,
            run_script_not_bash=self.builder_action_configure_define_run_script_not_bash(
                called_as,
                log
                ),
            relative_call=self.builder_action_configure_define_relative_call(
                called_as,
                log
                )
            )
        return ret

    def builder_action_build(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute(self, called_as, log):
        ret = autotools.make_high(
            self.buildingsite,
            log=log,
            options=[],
            arguments=[
                'install',
                'DESTDIR=' + self.dst_dir
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
