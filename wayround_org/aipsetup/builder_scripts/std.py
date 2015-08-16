
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

        if not isinstance(
                buildingsite,
                wayround_org.aipsetup.build.BuildingSiteCtl
                ):
            raise TypeError("`buildingsite' invalid type")

        self.control = buildingsite
        self.buildingsite_path = self.control.path

        '''
        # this is for glibc case, when package_info `host' should stay same
        # as `build', but ./configure --host must be different
        self.internal_host_redefinition = None

        # done whis, but may be it's not needed
        self.internal_build_redefinition = None  # not used
        self.internal_target_redefinition = None  # not used

        # override values is package_info.json
        self.total_host_redefinition = None
        self.total_build_redefinition = None
        self.total_target_redefinition = None
        '''

        self.separate_build_dir = False

        self.source_configure_reldir = '.'

        self.forced_target = False

        #self.apply_host_spec_linking_interpreter_option = False
        #self.apply_host_spec_linking_lib_dir_options = False

        self.apply_host_spec_compilers_options = True

        # None - not used, bool - force value
        self.force_crossbuilder = None
        self.force_crossbuild = None

        self.custom_data = self.define_custom_data()

        self.action_dict = self.define_actions()

        return

    def get_buildingsite_ctl(self):
        return self.control

    def get_package_info(self):
        # TODO: smart cache definitely needed :-/
        return self.control.read_package_info()

    def get_src_dir(self):
        return self.control.getDIR_SOURCE()

    def get_bld_dir(self):
        return self.control.getDIR_BUILDING()

    def get_patches_dir(self):
        return self.control.getDIR_PATCHES()

    def get_dst_dir(self):
        return self.control.getDIR_DESTDIR()

    def get_log_dir(self):
        return self.control.getDIR_BUILD_LOGS()

    def get_tar_dir(self):
        return self.control.getDIR_TARBALL()

    def get_is_crossbuild(self):

        ret = self.force_crossbuild
        if ret is None:
            ret = (
                self.get_build_from_pkgi() != self.get_host_from_pkgi()

                and

                self.get_host_from_pkgi() == self.get_arch_from_pkgi()
                )

        return ret

    def get_is_crossbuilder(self):

        ret = self.force_crossbuilder
        if ret is None:
            ret = (self.get_target_from_pkgi() is not None

                   and (self.get_target_from_pkgi()
                        != self.get_host_from_pkgi())

                   and (self.get_arch_from_pkgi()
                        != self.get_host_from_pkgi())
                   )

        return ret

    def get_host_from_pkgi(self):
        return self.get_package_info()['constitution']['host']

    def get_build_from_pkgi(self):
        return self.get_package_info()['constitution']['build']

    def get_target_from_pkgi(self):
        return self.get_package_info()['constitution']['target']

    def get_arch_from_pkgi(self):
        return self.get_package_info()['constitution']['arch']

    def get_multihost_dir(self):
        return wayround_org.utils.path.join(
            os.path.sep,
            wayround_org.aipsetup.build.ROOT_MULTIHOST_DIRNAME
            )

    def get_dst_multihost_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_multihost_dir()
            )

    def get_host_dir(self):
        return wayround_org.utils.path.join(
            self.get_multihost_dir(),
            self.get_host_from_pkgi()
            )

    def get_dst_host_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_host_dir()
            )

    def get_host_multiarch_dir(self):
        return wayround_org.utils.path.join(
            self.get_host_dir(),
            wayround_org.aipsetup.build.MULTIHOST_MULTIARCH_DIRNAME
            )

    def get_dst_host_multiarch_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_host_multiarch_dir()
            )

    def get_host_arch_dir(self):
        return wayround_org.utils.path.join(
            self.get_host_multiarch_dir(),
            self.get_arch_from_pkgi()
            )

    def get_dst_host_arch_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_host_arch_dir()
            )

    def get_host_crossbuilders_dir(self):
        return wayround_org.utils.path.join(
            self.get_host_dir(),
            wayround_org.aipsetup.build.MULTIHOST_CROSSBULDERS_DIRNAME
            )

    def get_dst_host_crossbuilders_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_host_crossbuilders_dir()
            )

    def get_host_crossbuilder_dir(self):
        return wayround_org.utils.path.join(
            self.get_host_crossbuilders_dir(),
            self.get_target_from_pkgi()
            )

    def get_dst_host_crossbuilder_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_host_crossbuilder_dir()
            )

    def get_host_lib_dir(self):
        return wayround_org.utils.path.join(
            self.get_host_dir(),
            'lib{}'.format(self.get_multilib_variant_int())
            )

    def get_host_arch_lib_dir(self):
        raise Exception("this is invalid methos - don't use it")
        return wayround_org.utils.path.join(
            self.get_host_arch_dir(),
            'lib{}'.format(self.get_multilib_variant_int())
            )

    def get_host_arch_list(self):
        ret = []

        lst = os.listdir(self.get_host_multiarch_dir())

        for i in lst:
            jo = wayround_org.utils.path.join(
                self.get_host_multiarch_dir(),
                i
                )
            if os.path.isdir(jo) and not os.path.islink(jo):
                ret.append(i)

        return sorted(ret)

    # def calculate_default_linker_program(self):
    #    return wayround_org.aipsetup.build.find_dl(self.host_multiarch_dir)

    # def calculate_default_linker_program_ld_parameter(self):
    #    return '--dynamic-linker={}'.format(
    #        self.calculate_default_linker_program()
    #        )

    # def calculate_default_linker_program_gcc_parameter(self):
    #    return '-Wl,{}'.format(
    #        self.calculate_default_linker_program_ld_parameter()
    #        )

    '''
    def calculate_main_multiarch_lib_dir_name(self):

        # raise Exception("Acctention required here :-/")

        # \'''
        if self.host_strong == 'x86_64-pc-linux-gnu':
            ret = 'lib64'
        elif self.host_strong == 'i686-pc-linux-gnu':
            ret = 'lib'
        elif self.host_strong == 'x86-pc-linux-gnu':
            ret = 'lib32'
        else:
            raise Exception("don't know")
        # \'''

        # return 'lib'
        return ret
    '''

    def calculate_pkgconfig_search_paths(self):

        host_archs = self.get_host_arch_list()
        host_archs += [self.get_host_dir()]
        ret = []

        for j in host_archs:

            for i in [
                    wayround_org.utils.path.join(
                        j,
                        'share',
                        'pkgconfig'),
                    wayround_org.utils.path.join(
                        j,
                        'lib',
                        'pkgconfig'),
                    wayround_org.utils.path.join(
                        j,
                        'lib32',
                        'pkgconfig'),
                    wayround_org.utils.path.join(
                        j,
                        'libx32',
                        'pkgconfig'),
                    wayround_org.utils.path.join(
                        j,
                        'lib64',
                        'pkgconfig'),
                    ]:

                if os.path.isdir(i):
                    ret.append(i)

        return ret

    def get_CC_from_pkgi(self):
        return self.get_package_info()['constitution']['CC']

    def get_CXX_from_pkgi(self):
        return self.get_package_info()['constitution']['CXX']

    def calculate_CC(self):
        # NOTE: here well be some additional stuff to find out CC
        return self.get_CC_from_pkgi()

    def calculate_CXX(self):
        # NOTE: here well be some additional stuff to find out CXX
        return self.get_CXX_from_pkgi()

    def get_multilib_variants_from_pkgi(self):
        return self.get_package_info()['constitution']['multilib_variants']

    def calculate_CC_string(self):
        multilib_variants = self.get_multilib_variants_from_pkgi()
        return '{} -{}'.format(self.calculate_CC(), multilib_variants[0])

    def calculate_CXX_string(self):
        multilib_variants = self.get_multilib_variants_from_pkgi()
        if len(multilib_variants) != 1:
            raise Exception("len(multilib_variants) != 1")
        return '{} -{}'.format(self.calculate_CXX(), multilib_variants[0])

    def get_multilib_variant(self):
        multilib_variants = self.get_multilib_variants_from_pkgi()
        if len(multilib_variants) != 1:
            raise Exception("len(multilib_variants) != 1")
        return multilib_variants[0]

    def get_multilib_variant_int(self):
        return int(self.get_multilib_variant()[1:])

    def calculate_compilers_options(self, d):

        if not 'CC' in d:
            d['CC'] = []
        d['CC'].append(self.calculate_CC_string())

        if not 'GCC' in d:
            d['GCC'] = []
        # TODO: probably this calculation needs to be replaced by something
        #       more appropriate
        d['GCC'].append(self.calculate_CC())

        if not 'CXX' in d:
            d['CXX'] = []
        d['CXX'].append(self.calculate_CXX_string())

        return

    def all_automatic_flags(self):

        d = {}

        if self.apply_host_spec_compilers_options:
            self.calculate_compilers_options(d)

        return d

    def all_automatic_flags_as_dict(self):

        af = self.all_automatic_flags()

        ret = {}

        for i in sorted(list(af.keys())):
            ret[i] = ' '.join(af[i])

        return ret

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

    def print_help(self):
        txt = ''
        print("building script: {}".format(__name__))
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

    def check_deprecated_methods(self, called_as, log):
        for i in [
                'builder_action_build_define_add_args',
                'builder_action_build_define_add_opts',
                'builder_action_build_define_distribute_args',
                'builder_action_build_define_distribute_opts',
                'builder_action_configure_define_options',
                'builder_action_make_define_environment',
                ]:
            if hasattr(self, i):
                raise Exception(
                    "deprecated method `{}' is defined".format(i)
                    )
        return

    def builder_action_src_cleanup(self, called_as, log):
        """
        Standard sources cleanup
        """

        if os.path.isdir(self.get_src_dir()):
            log.info("cleaningup source dir")
            wayround_org.utils.file.cleanup_dir(self.get_src_dir())

        return 0

    def builder_action_bld_cleanup(self, called_as, log):
        """
        Standard building dir cleanup
        """

        if os.path.isdir(self.get_bld_dir()):
            log.info("cleaningup building dir")
            wayround_org.utils.file.cleanup_dir(self.get_bld_dir())

        return 0

    def builder_action_dst_cleanup(self, called_as, log):
        """
        Standard destdir cleanup
        """

        if os.path.isdir(self.get_dst_dir()):
            log.info("cleaningup destination dir")
            wayround_org.utils.file.cleanup_dir(self.get_dst_dir())

        return 0

    def builder_action_extract(self, called_as, log):
        """
        Standard sources extraction actions
        """

        ret = autotools.extract_high(
            self.buildingsite_path,
            self.get_package_info()['pkg_info']['basename'],
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
            log
            )

        ret = 0

        if os.path.isfile(
                wayround_org.utils.path.join(
                    self.get_src_dir(),
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

                if os.path.isfile(
                        wayround_org.utils.path.join(
                            self.get_src_dir(),
                            self.source_configure_reldir,
                            i[0]
                            )
                        ):

                    log.info(
                        "found `{}'. trying to execute: {}".format(
                            i[0],
                            ' '.join(i[1])
                            )
                        )

                    wd = wayround_org.utils.path.join(
                        self.get_src_dir(),
                        self.source_configure_reldir
                        )
                    if '/' in i[1][0]:
                        tgt_file = wayround_org.utils.path.join(wd, i[1][0])
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

    def builder_action_configure_define_environment(self, called_as, log):

        ret = {}

        pkg_config_paths = self.calculate_pkgconfig_search_paths()

        ret.update(
            {'PKG_CONFIG_PATH': ':'.join(pkg_config_paths)}
            )

        ret.update(self.builder_action_configure_define_PATH_dict())

        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        ret = [
            '--prefix={}'.format(self.get_host_dir()),

            '--bindir=' +
            wayround_org.utils.path.join(
                self.get_host_arch_dir(),
                'bin'
                ),

            '--sbindir=' +
            wayround_org.utils.path.join(
                self.get_host_arch_dir(),
                'sbin'
                ),

            '--libexecdir=' +
            wayround_org.utils.path.join(
                self.get_host_arch_dir(),
                'libexec'
                ),

            '--includedir=' +
            wayround_org.utils.path.join(
                self.get_host_arch_dir(),
                'include'
                ),

            '--datarootdir=' +
            wayround_org.utils.path.join(
                self.get_host_arch_dir(),
                'share'
                ),

            '--includedir=' +
            wayround_org.utils.path.join(
                self.get_host_arch_dir(),
                'include'
                ),

            # NOTE: removed '--libdir=' because I about to allow
            #       programs to use lib dir name which they desire.
            #       possibly self.calculate_main_multiarch_lib_dir_name()
            #       need to be used here

            #'--libdir=' + wayround_org.utils.path.join(self.host_multiarch_dir, 'lib'),

            # NOTE: --libdir= needed at least for glibc to point it using
            #       valid 'lib' or 'lib64' dir name. else it can put 64-bit
            #       crt*.ofiles into 32-bit lib dir
            '--libdir=' + self.get_host_lib_dir(),

            '--mandir=' + wayround_org.utils.path.join(
                self.get_host_arch_dir(),
                'share',
                'man'
                ),
            '--sysconfdir=/etc',
            # '--sysconfdir=' + wayround_org.utils.path.join(
            #     self.host_multiarch_dir,
            #     'etc'
            #     ),
            '--localstatedir=/var',
            '--enable-shared',

            # WARNING: using --with-sysroot in some cases makes
            #          build processes involving libtool to generate incorrect
            #          *.la files
            # '--with-sysroot={}'.format(self.host_multiarch_dir)

            ] + autotools.calc_conf_hbt_options(self) + \
            self.all_automatic_flags_as_list()

        return ret

    def builder_action_configure_define_script_name(self, called_as, log):
        return 'configure'

    def builder_action_configure_define_run_script_not_bash(
            self,
            called_as,
            log
            ):
        return False

    def builder_action_configure_define_relative_call(self, called_as, log):
        return False

    def builder_action_configure_define_PATH_list(self):
        ret = [
            wayround_org.utils.path.join(self.get_host_arch_dir(), 'bin'),
            wayround_org.utils.path.join(self.get_host_arch_dir(), 'sbin')
            ]
        return ret

    def builder_action_configure_define_PATH_dict(self):
        ret = {
            'PATH': ':'.join(self.builder_action_configure_define_PATH_list())
            }
        return ret

    def builder_action_configure(self, called_as, log):

        log.info(
            "crossbuild?: {}, crossbuilder?: {}".format(
                self.get_is_crossbuild(),
                self.get_is_crossbuilder()
                )
            )

        self.check_deprecated_methods(called_as, log)

        envs = {}
        if hasattr(self, 'builder_action_configure_define_environment'):
            envs = self.builder_action_configure_define_environment(
                called_as,
                log
                )

        opts = []
        if hasattr(self, 'builder_action_configure_define_opts'):
            opts = self.builder_action_configure_define_opts(
                called_as,
                log
                )

        args = []
        if hasattr(self, 'builder_action_configure_define_args'):
            args = self.builder_action_configure_define_args(
                called_as,
                log
                )

        ret = autotools.configure_high(
            self.buildingsite_path,
            log=log,
            options=opts,
            arguments=args,
            environment=envs,
            environment_mode='copy',
            source_configure_reldir=self.source_configure_reldir,
            use_separate_buildding_dir=self.separate_build_dir,
            script_name=self.builder_action_configure_define_script_name(
                called_as,
                log
                ),
            run_script_not_bash=(
                self.builder_action_configure_define_run_script_not_bash(
                    called_as,
                    log
                    )
                ),
            relative_call=(
                self.builder_action_configure_define_relative_call(
                    called_as,
                    log
                    )
                )
            )
        return ret

    def builder_action_build_define_cpu_count(self, called_as, log):
        return os.cpu_count()  # 1

    def builder_action_build_collect_options(self, called_as, log):
        ret = []

        ret += ['-j{}'.format(
                int(
                    self.builder_action_build_define_cpu_count(
                        called_as,
                        log
                        )
                    )
                )
                ]

        if hasattr(self, 'builder_action_build_define_opts'):
            ret += self.builder_action_build_define_opts(
                called_as,
                log
                )
        return ret

    def builder_action_build_define_environment(self, called_as, log):
        ret = self.builder_action_configure_define_environment(called_as, log)

        ret.update(self.all_automatic_flags_as_dict())

        ret.update(self.builder_action_configure_define_PATH_dict())

        pkg_config_paths = self.calculate_pkgconfig_search_paths()

        ret.update({'PKG_CONFIG_PATH': ':'.join(pkg_config_paths)})

        # ret.update({'PKG_CONFIG_PATH': None})

        LD_LIBRARY_PATH = []

        # NOTE: probably it need to be uncommented
        # if 'LD_LIBRARY_PATH' in os.environ:
        #     LD_LIBRARY_PATH += os.environ['LD_LIBRARY_PATH'].split(':')

        # Explanation to all this .libs in LD_LIBRARY_PATH:
        #     if building to nonstandard prefix, for some reason
        #     building breaks with errors similar to

        '''
        [i] [2015-08-05T11:08:26.167109] [pulseaudio build]   CCLD     channelmap-test
        [e] [2015-08-05T11:08:26.41759 ] [pulseaudio build] /multiarch/i686-pc-linux-gnu/lib/gcc/i686-pc-linux-gnu/5.2.0/../../../../i
        686-pc-linux-gnu/bin/ld: warning: libpulsecommon-6.0.so, needed by ./.libs/libpulse.so, not found (try using -rpath or -rpath-
        link)
        [e] [2015-08-05T11:08:26.417712] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_tagstruct_getu8'
        [e] [2015-08-05T11:08:26.41777 ] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_tagstruct_put_format_info'
        [e] [2015-08-05T11:08:26.417815] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_mutex_unlock'
        [e] [2015-08-05T11:08:26.417853] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_format_info_get_channel_ma
        p'
        [e] [2015-08-05T11:08:26.417888] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_init_proplist'
        [e] [2015-08-05T11:08:26.417922] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_tagstruct_put_boolean'
        [e] [2015-08-05T11:08:26.417955] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_rtclock_from_wallclock'
        [e] [2015-08-05T11:08:26.417988] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_timespec_store'
        [e] [2015-08-05T11:08:26.418022] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_memblockq_get_length'
        [e] [2015-08-05T11:08:26.418055] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_tagstruct_get_usec'
        [e] [2015-08-05T11:08:26.418089] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_memblockq_peek'
        [e] [2015-08-05T11:08:26.418127] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_pdispatch_register_reply'
        [e] [2015-08-05T11:08:26.418161] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_memblockq_new'
        [e] [2015-08-05T11:08:26.418199] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_strbuf_tostring_free'
        [e] [2015-08-05T11:08:26.418243] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_snprintf'
        [e] [2015-08-05T11:08:26.41828 ] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_strlist_pop'
        [e] [2015-08-05T11:08:26.418314] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_tagstruct_get_channel_map'
        [e] [2015-08-05T11:08:26.418347] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_tagstruct_free'
        [e] [2015-08-05T11:08:26.41838 ] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_hashmap_new_full'
        [e] [2015-08-05T11:08:26.418412] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_mutex_new'
        [e] [2015-08-05T11:08:26.418445] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_pstream_set_receive_memblo
        ck_callback'
        [e] [2015-08-05T11:08:26.418478] [pulseaudio build] ./.libs/libpulse.so: undefined reference to `pa_smoother_new'
        '''

        dot_libs = [
            #'../tag/.libs',
            '.libs',
            '../.libs',
            '../../.libs',
            '../../../.libs',
            '../../../../.libs',
            './.libs',
            './../.libs',
            './../../.libs',
            './../../../.libs',
            './../../../../.libs',
            ]

        dot_libs.sort()

        LD_LIBRARY_PATH += dot_libs

        ret.update({'LD_LIBRARY_PATH': ':'.join(LD_LIBRARY_PATH)})
        # ret.update({'LD_LIBRARY_PATH': None})

        return ret

    def builder_action_build_define_opts(self, called_as, log):
        return []

    def builder_action_build_define_args(self, called_as, log):
        return []

    def builder_action_build(self, called_as, log):

        self.check_deprecated_methods(called_as, log)

        envs = {}
        if hasattr(self, 'builder_action_build_define_environment'):
            envs = self.builder_action_build_define_environment(
                called_as,
                log
                )

        opts = self.builder_action_build_collect_options(called_as, log)

        args = []
        if hasattr(self, 'builder_action_build_define_args'):
            args = self.builder_action_build_define_args(
                called_as,
                log
                )

        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=opts,
            arguments=args,
            environment=envs,
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret

    def builder_action_distribute_define_environment(self, called_as, log):
        return {}

    def builder_action_distribute_define_opts(self, called_as, log):
        return []

    def builder_action_distribute_define_args(self, called_as, log):
        return ['install', 'DESTDIR={}'.format(self.get_dst_dir())]

    def builder_action_distribute(self, called_as, log):

        self.check_deprecated_methods(called_as, log)

        envs = {}
        if hasattr(self, 'builder_action_distribute_define_environment'):
            envs = self.builder_action_distribute_define_environment(
                called_as,
                log
                )

        opts = []
        if hasattr(self, 'builder_action_distribute_define_opts'):
            opts = self.builder_action_distribute_define_opts(
                called_as,
                log
                )

        args = []
        if hasattr(self, 'builder_action_distribute_define_args'):
            args = self.builder_action_distribute_define_args(
                called_as,
                log
                )

        ret = autotools.make_high(
            self.buildingsite_path,
            log=log,
            options=opts,
            arguments=args,
            environment=envs,
            environment_mode='copy',
            use_separate_buildding_dir=self.separate_build_dir,
            source_configure_reldir=self.source_configure_reldir
            )
        return ret
