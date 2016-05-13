
import copy
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

        # this is for builder_action_autogen() method
        self.forced_autogen = False

        self.separate_build_dir = False

        self.source_configure_reldir = '.'

        self.forced_target = False

        self.apply_host_spec_compilers_options = True

        # None - not used, bool - force value
        self.force_crossbuilder = None
        self.force_crossbuild = None

        #self.override_get_arch_from_pkgi = False

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
                self.get_host_from_pkgi() != self.get_build_from_pkgi()

                and

                self.get_host_from_pkgi() == self.get_arch_from_pkgi()
                )

        return ret

    def get_is_crossbuilder(self):

        ret = self.force_crossbuilder
        if ret is None:
            ret = (self.get_target_from_pkgi() is not None

                   and

                   (self.get_host_from_pkgi() != self.get_target_from_pkgi())

                   and

                   (self.get_host_from_pkgi() != self.get_arch_from_pkgi())
                   )

        return ret

    def get_is_only_other_arch(self):
        h = self.get_host_from_pkgi()
        b = self.get_build_from_pkgi()
        t = self.get_target_from_pkgi()
        a = self.get_arch_from_pkgi()

        ret = (
            (h == b)

            and

            (
                (t is not None and t == h)
                or
                (t is None)
                )

            and

            (a != h)
            )

        return ret

    def get_host_from_pkgi(self):
        return self.get_package_info()['constitution']['host']

    def get_build_from_pkgi(self):
        return self.get_package_info()['constitution']['build']

    def get_target_from_pkgi(self):
        ret = self.get_package_info()['constitution']['target']
        # if self.override_get_arch_from_pkgi:
        #    ret = self.override_get_arch_from_pkgi
        return ret

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
            self.calculate_main_multiarch_lib_dir_name()
            )

    def get_dst_host_lib_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_host_lib_dir()
            )

    def get_host_arch_lib_dir(self):
        return wayround_org.utils.path.join(
            self.get_host_arch_dir(),
            self.calculate_main_multiarch_lib_dir_name()
            )

    def get_dst_host_arch_lib_dir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.get_host_arch_lib_dir()
            )

    def calculate_install_prefix(self):
        if self.get_host_from_pkgi() == self.get_arch_from_pkgi():
            ret = self.get_host_dir()
        else:
            ret = self.get_host_arch_dir()
        return ret

    def calculate_dst_install_prefix(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.calculate_install_prefix()
            )

    def calculate_install_libdir(self):
        if self.get_host_from_pkgi() == self.get_arch_from_pkgi():
            ret = self.get_host_lib_dir()
        else:
            ret = self.get_host_arch_lib_dir()
        return ret

    def calculate_dst_install_libdir(self):
        return wayround_org.utils.path.join(
            self.get_dst_dir(),
            self.calculate_install_libdir()
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
    #    return wayround_org.aipsetup.build.find_dl(self.get_host_arch_dir())

    # def calculate_default_linker_program_ld_parameter(self):
    #    return '--dynamic-linker={}'.format(
    #        self.calculate_default_linker_program()
    #        )

    # def calculate_default_linker_program_gcc_parameter(self):
    #    return '-Wl,{}'.format(
    #        self.calculate_default_linker_program_ld_parameter()
    #        )

    def calculate_main_multiarch_lib_dir_name(self):

        # NOTE: at least 'guile' requires to be configured with libdir=lib64
        #       so looks like it's "too early" to refuse using this method

        # multilib_variant = str(self.get_multilib_variant_int())

        host = self.get_host_from_pkgi()
        arch = self.get_arch_from_pkgi()

        ret = 'lib'

        if host in [
                'x86_64-pc-linux-gnu',
                'i686-pc-linux-gnu',
                ]:

            if arch == 'i686-pc-linux-gnu':
                ret = 'lib'
            elif arch == 'x86_64-pc-linux-gnu':
                ret = 'lib64'
            else:
                raise Exception("Don't know")

        else:
            raise Exception("Don't know")

        return ret

    # '''
    def _calculate_pkgconfig_search_paths_qt5(self, prefix=None):

        # TODO: what does this do here?

        if prefix is None:
            prefix = self.calculate_install_prefix()

        where_to_search = [
            wayround_org.utils.path.join(
                prefix, 'opt', 'qt', '5', 'share', 'pkgconfig'
                ),
            wayround_org.utils.path.join(
                prefix, 'opt', 'qt', '5', 'lib', 'pkgconfig'
                ),
            wayround_org.utils.path.join(
                prefix, 'opt', 'qt', '5', 'lib64', 'pkgconfig'
                ),
            ]

        ret = []

        for i in where_to_search:

            if os.path.isdir(i):
                ret.append(i)

        return ret
    # '''

    def calculate_pkgconfig_search_paths(self, prefix=None):

        #multilib_variant = str(self.get_multilib_variant_int())

        # host_archs = self.get_host_arch_list()
        # host_archs += [self.get_host_dir()]

        if prefix is None:
            prefix = self.calculate_install_prefix()

        where_to_search = [
            wayround_org.utils.path.join(
                prefix,
                'share',
                'pkgconfig'
                ),
            wayround_org.utils.path.join(
                prefix,
                'lib',
                'pkgconfig'
                ),
            wayround_org.utils.path.join(
                prefix,
                'lib64',
                'pkgconfig'
                ),
            ]

        ret = []

        for i in where_to_search:

            if os.path.isdir(i):
                ret.append(i)

        ret += self._calculate_pkgconfig_search_paths_qt5(prefix)

        return ret

    def calculate_LD_LIBRARY_PATH(self, prefix=None):

        ret = []

        if prefix is None:
            prefix = self.calculate_install_prefix()

        inst_prefix = self.get_host_dir()

        for i in [
                wayround_org.utils.path.join(
                    inst_prefix,
                    'lib'
                    ),
                wayround_org.utils.path.join(
                    inst_prefix,
                    'lib64'
                    ),
                ]:

            if os.path.isdir(i):
                if not i in ret:
                    ret.append(i)

        inst_prefix = prefix

        for i in [
                wayround_org.utils.path.join(
                    inst_prefix,
                    'lib'
                    ),
                wayround_org.utils.path.join(
                    inst_prefix,
                    'lib64'
                    ),
                ]:
            if os.path.isdir(i):
                if not i in ret:
                    ret.append(i)

        return ret

    def calculate_LIBRARY_PATH(self, prefix=None):
        # NOTE: potentially this is different from LD_LIBRARY_PATH.
        #       LIBRARY_PATH is for GCC and it's friends. so it's possible
        #       for it to differ also in code, in future, not only in name.
        ret = self.calculate_LD_LIBRARY_PATH(prefix)
        return ret

    def calculate_C_INCLUDE_PATH(self, prefix=None):

        if prefix is None:
            prefix = self.calculate_install_prefix()

        ret = []

        for i in [
                wayround_org.utils.path.join(
                    prefix,
                    'include'
                    ),
                ]:
            if os.path.isdir(i):
                ret.append(i)

        return ret

    def calculate_PATH(self, prefix=None):

        if prefix is None:
            prefix = self.calculate_install_prefix()

        ret = []
        for i in [
                wayround_org.utils.path.join(
                    prefix,
                    'bin'
                ),
                wayround_org.utils.path.join(
                    prefix,
                    'sbin'
                ),
                wayround_org.utils.path.join(
                    self.get_host_dir(),
                    'bin'
                ),
                wayround_org.utils.path.join(
                    self.get_host_dir(),
                    'sbin'
                )
                ]:
            if not i in ret:
                ret.append(i)
        return ret

    def calculate_PATH_dict(self, prefix=None):
        ret = {
            'PATH': ':'.join(self.calculate_PATH(prefix=prefix))
            }
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
        if len(multilib_variants) != 1:
            raise Exception("len(multilib_variants) != 1")
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
        ret = collections.OrderedDict([
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
        return ret

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
        series_file_path = wayround_org.utils.path.join(
            self.get_patches_dir(),
            'series'
            )

        series = []

        if os.path.isfile(series_file_path):
            with open(series_file_path) as f:
                series = f.read().split('\n')

        for i in series:
            p_file = wayround_org.utils.path.join(
                self.get_patches_dir(),
                i
            )

            if os.path.isfile(p_file):
                log.info("applying patch {}".format(i))

                with open(p_file) as f:
                    p_text = f.read()

                p = subprocess.Popen(
                    ['patch', '-p1'],
                    cwd=self.get_src_dir(),
                    stdin=subprocess.PIPE,
                    stdout=log.stdout,
                    stderr=log.stderr
                    )
                p.communicate(bytes(p_text, 'utf-8'))
                if p.wait() != 0:
                    ret = 1

        return 0

    def builder_action_autogen(self, called_as, log):

        cfg_script_name = self.builder_action_configure_define_script_name(
            called_as,
            log
            )

        ret = 0

        do_work = False

        if os.path.isfile(
                wayround_org.utils.path.join(
                    self.get_src_dir(),
                    self.source_configure_reldir,
                    cfg_script_name
                    )
                ):

            log.info("configurer found. no generator use presumed")
        else:
            log.info("configurer not found. generator use presumed")
            do_work = True

        if self.forced_autogen:
            log.info(
                "generator use is forced".format(
                    cfg_script_name
                )
            )
            do_work = True

        if do_work:

            log.info(
                "trying to find and use generator mesures"
                )

            for i in [
                    ('autogen.sh', ['./autogen.sh']),
                    ('bootstrap.sh', ['./bootstrap.sh']),
                    ('bootstrap', ['./bootstrap']),
                    ('genconfig.sh', ['./genconfig.sh']),
                    ('configure.ac', ['autoreconf', '-i']),
                    ('configure.in', ['autoreconf', '-i']),
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

        ret.update(
            {'PKG_CONFIG_PATH': ':'.join(
                self.calculate_pkgconfig_search_paths())}
            )

        ret.update(
            {'LD_LIBRARY_PATH': ':'.join(self.calculate_LD_LIBRARY_PATH())}
            )

        ret.update(
            {'LIBRARY_PATH': ':'.join(self.calculate_LIBRARY_PATH())}
            )

        ret.update(
            {'C_INCLUDE_PATH': ':'.join(self.calculate_C_INCLUDE_PATH())}
            )

        ret.update({'PATH': ':'.join(self.calculate_PATH())})
        ret.update({'CC': self.calculate_CC_string()})
        ret.update({'CXX': self.calculate_CXX_string()})

        return ret

    def builder_action_configure_define_opts(self, called_as, log):

        ret = []

        ret += [
            '--prefix={}'.format(self.calculate_install_prefix())
            ]

        ret += [

            #'--includedir=' +
            # wayround_org.utils.path.join(
            #    self.get_host_arch_dir(),
            #    'include'
            #    ),

            #'--localedir=' +
            # wayround_org.utils.path.join(
            #    self.get_host_arch_dir(),
            #    'share'
            #    ),

            # NOTE: removed '--libdir=' because I about to allow
            #       programs to use lib dir name which they desire.
            #       possibly self.calculate_main_multiarch_lib_dir_name()
            #       need to be used here
            # NOTE: --libdir= needed at least for glibc to point it using
            #       valid 'lib' or 'lib64' dir name. else it can put 64-bit
            #       crt*.o files into 32-bit lib dir
            # NOTE: using lib for 32 bit and lib64 for 64 bit libs is failed
            #       many programs still can't install in lib64 even if I
            #       trying for force them do. so lib name will be fixed
            #       'lib' name for ever :E
            # NOTE: note about crt*.o still in power. can't build gcc with
            #       multilib support and rename lib64 to lib and
            #       place it into another location. so lib and lib64
            #       need to reamin in one dir
            # NOTE: 'python', 'tcl' and some other pacakges will install
            #       some libs into 'lib' dir no metter what

            # '--libdir=' + wayround_org.utils.path.join(
            #    self.get_host_arch_dir(), 'lib'),
            # '--libdir=' + self.get_host_lib_dir(),
            # '--libdir=' + wayround_org.utils.path.join(
            #    self.get_host_arch_dir(),
            #    'lib'
            #    ),

            '--libdir=' + self.calculate_install_libdir(),

            '--sysconfdir=/etc',
            # '--sysconfdir=' + wayround_org.utils.path.join(
            #     self.get_host_arch_dir(),
            #     'etc'
            #     ),
            '--localstatedir=/var',
            '--enable-shared',

            # WARNING: using --with-sysroot in some cases makes
            #          build processes involving libtool to generate incorrect
            #          *.la files
            # '--with-sysroot={}'.format(self.get_host_arch_dir())

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

        #sleeptime = 5
        #log.info("sleep: \033[0;1m{}\033[0m seconds".format(sleeptime))
        # time.sleep(sleeptime)
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
        ret = self.builder_action_build_define_environment(called_as, log)
        return ret

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
