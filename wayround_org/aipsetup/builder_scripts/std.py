
import logging
import os.path
import subprocess
import collections
import inspect
import time

import wayround_org.utils.file
import wayround_org.utils.log
import wayround_org.utils.path

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

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = False

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
        return self.build != self.host_strong

    @property
    def is_crossbuilder(self):
        return self.target is not None and (self.target != self.host_strong)

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
    def host_multiarch_dir(self):
        return wayround_org.utils.path.join(
            os.path.sep,
            'multiarch',
            self.host_strong
            )

    @property
    def dst_host_multiarch_dir(self):
        return wayround_org.utils.path.join(
            self.dst_dir,
            self.host_multiarch_dir
            )

    @property
    def host_crossbuilders_dir(self):
        return wayround_org.utils.path.join(
            self.host_multiarch_dir,
            'crossbuilders'
            )

    @property
    def dst_host_crossbuilders_dir(self):
        return wayround_org.utils.path.join(
            self.dst_dir,
            self.host_crossbuilders_dir
            )

    @property
    def host_multiarch_lib_dir(self):
        return wayround_org.utils.path.join(
            os.path.sep,
            'multiarch',
            self.host_strong,
            'lib'
            )

    @property
    def build(self):
        return self.package_info['constitution']['build']

    def calculate_default_linker_program(self):
        return wayround_org.aipsetup.build.find_dl(self.host_multiarch_dir)

    def calculate_default_linker_program_ld_parameter(self):
        return '--dynamic-linker={}'.format(
            self.calculate_default_linker_program()
            )

    def calculate_default_linker_program_gcc_parameter(self):
        return '-Wl,{}'.format(
            self.calculate_default_linker_program_ld_parameter()
            )

    def calculate_pkgconfig_search_paths(self):
        return [
            wayround_org.utils.path.join(
                self.host_multiarch_dir,
                'share',
                'pkgconfig'),
            wayround_org.utils.path.join(
                self.host_multiarch_dir,
                'lib',
                'pkgconfig'),
            wayround_org.utils.path.join(
                self.host_multiarch_dir,
                'lib32',
                'pkgconfig'),
            wayround_org.utils.path.join(
                self.host_multiarch_dir,
                'libx32',
                'pkgconfig'),
            wayround_org.utils.path.join(
                self.host_multiarch_dir,
                'lib64',
                'pkgconfig'),
            ]

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
        # TODO: add some default patch handler
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

            log.info(
                "configuration script not found. trying to find and use"
                " generator mesures"
                )

            for i in [
                    ('autogen.sh', ['./autogen.sh']),
                    ('bootstrap.sh', ['./bootstrap.sh']),
                    ('bootstrap', ['./bootstrap']),
                    ('genconfig.sh', ['./genconfig.sh']),
                    ('configure.ac', ['autoconf']),
                    ('configure.in', ['autoconf']),
                    ]:

                log.info(
                    "found `{}'. trying to execute: {}".format(
                        i[0],
                        ' '.join(i[1])
                        )
                    )

                if os.path.isfile(
                        wayround_org.utils.path.join(
                            self.src_dir,
                            self.source_configure_reldir,
                            i[0]
                            )
                        ):
                    wd = wayround_org.utils.path.join(
                        self.src_dir,
                        self.source_configure_reldir
                        )
                    if '/' in i[1][0]:
                        tgt_file = os.path.join(wd, i[1][0])
                        log.info("changing mode (+x) for: {}".format(tgt_file))
                        chmod_p = subprocess.Popen(
                            ['chmod', '+x', tgt_file],
                            cwd=wd
                            )
                        chmod_p.wait()

                    if i[1][0].endswith('.sh'):
                        i[1].insert(0, 'bash')

                    p = subprocess.Popen(
                        i[1],
                        cwd=wd,
                        stdout=log.stdout,
                        stderr=log.stderr
                        )
                    ret = p.wait()
                    break
            else:
                log.error(
                    "./{} not found and no generators found".format(
                        cfg_script_name
                        )
                    )
                ret = 2
        return ret

    def builder_action_configure_define_compilers_options(self, d):
        if not 'CC' in d:
            d['CC'] = []
        d['CC'].append('{}-gcc'.format(self.host_strong))

        if not 'GCC' in d:
            d['GCC'] = []
        d['GCC'].append('{}-gcc'.format(self.host_strong))

        if not 'CXX' in d:
            d['CXX'] = []
        d['CXX'].append('{}-g++'.format(self.host_strong))

        return

    def builder_action_configure_define_linking_interpreter_option(self, d):

        if not 'LDFLAGS' in d:
            d['LDFLAGS'] = []

        d['LDFLAGS'].append(
            self.calculate_default_linker_program_gcc_parameter()
            )

        return

    def builder_action_configure_define_linking_lib_dir_options(self, d):

        if not 'LDFLAGS' in d:
            d['LDFLAGS'] = []

        d['LDFLAGS'].append('-L{}'.format(self.host_multiarch_lib_dir))

        return

    def all_automatic_flags_as_dict(self):

        af = self.all_automatic_flags()

        ret = {}

        for i in sorted(list(af.keys())):
            ret[i] = ' '.join(af[i])

        return ret

    def all_automatic_flags(self):

        d = {}

        if self.apply_host_spec_linking_interpreter_option:
            self.builder_action_configure_define_linking_interpreter_option(d)

        if self.apply_host_spec_linking_lib_dir_options:
            self.builder_action_configure_define_linking_lib_dir_options(d)

        if self.apply_host_spec_compilers_options:
            self.builder_action_configure_define_compilers_options(d)

        print(
            'd:\n{}'.format(d)
            )

        return d

    def all_automatic_flags_as_list(self):

        af = self.all_automatic_flags()

        ret = []

        for i in sorted(list(af.keys())):
            ret.append(
                '{}={}'.format(
                    i,
                    ' '.join(af[i])
                    )
                )

        return ret

    def builder_action_configure_define_options(self, called_as, log):

        ret = [
            '--prefix={}'.format(self.host_multiarch_dir),
            '--includedir=' +
            os.path.join(
                '/',
                'multiarch',
                self.host,
                'include'
                ),
            '--libdir=' + os.path.join(self.host_multiarch_dir, 'lib'),
            '--mandir=' + os.path.join(
                self.host_multiarch_dir,
                'share',
                'man'
                ),
            '--sysconfdir=/etc',
            # '--sysconfdir=' + os.path.join(
            #     self.host_multiarch_dir,
            #     'etc'
            #     ),
            '--localstatedir=/var',
            '--enable-shared',

            ] + autotools.calc_conf_hbt_options(self) + \
            self.all_automatic_flags_as_list()

        return ret

    def builder_action_configure_define_script_name(self, called_as, log):
        return 'configure'

    def builder_action_configure_define_run_script_not_bash(
            self, called_as, log
            ):
        return False

    def builder_action_configure_define_relative_call(self, called_as, log):
        return False

    def builder_action_configure_define_environment(self, called_as, log):
        return {}

    def builder_action_make_define_environment(self, called_as, log):
        return self.builder_action_configure_define_environment(called_as, log)

    def builder_action_configure(self, called_as, log):

        defined_options = self.builder_action_configure_define_options(
            called_as,
            log
            )

        defined_script_name = self.builder_action_configure_define_script_name(
            called_as,
            log
            )

        envs = self.builder_action_configure_define_environment(
            called_as,
            log
            )

        pkg_config_paths = self.calculate_pkgconfig_search_paths()

        envs.update(
            {'PKG_CONFIG_PATH': ':'.join(pkg_config_paths)}
            )

        ret = autotools.configure_high(
            self.buildingsite,
            log=log,
            options=defined_options,
            arguments=[],
            environment=envs,
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
                'DESTDIR={}'.format(self.dst_dir)
                ],
            environment=self.builder_action_make_define_environment(
                called_as,
                log),
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
