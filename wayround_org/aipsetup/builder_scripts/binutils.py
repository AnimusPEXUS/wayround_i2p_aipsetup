
import os.path
import collections
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file
import wayround_org.utils.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.forced_target = True

        self.apply_host_spec_linking_interpreter_option = False
        self.apply_host_spec_linking_lib_dir_options = False
        self.apply_host_spec_compilers_options = False

        return None

    def define_actions(self):
        ret = super().define_actions()

        ret['edit_package_info'] = self.builder_action_edit_package_info
        ret.move_to_end('edit_package_info', False)

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.get_package_info()['pkg_info']['name']
        except:
            name = None

        pi = self.get_package_info()

        if self.get_is_crossbuilder():
            pi['pkg_info']['name'] = 'cb-binutils-{}'.format(
                self.get_target_from_pkgi()
                )
        else:
            pi['pkg_info']['name'] = 'binutils'

        bs = self.control
        bs.write_package_info(pi)

        return ret

    def builder_action_extract(self, called_as, log):

        ret = super().builder_action_extract(called_as, log)

        if ret == 0:

            for i in [
                'gmp', 
                'mpc', 'mpfr', 'isl', 'cloog']:

                if autotools.extract_high(
                        self.buildingsite_path,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    log.error("Can't extract component: {}".format(i))
                    ret = 2

        return ret

    def builder_action_configure_define_environment(self, called_as, log):
        return {}

    def builder_action_configure_define_opts(self, called_as, log):

        ret = super().builder_action_configure_define_opts(called_as, log)

        if self.get_is_crossbuilder():
            prefix = wayround_org.utils.path.join(
                self.get_host_crossbuilders_dir(),
                self.target
                )

            ret = [
                '--prefix={}'.format(prefix),
                '--mandir={}'.format(
                    wayround_org.utils.path.join(
                        prefix,
                        'share',
                        'man'
                        )
                    ),
                '--sysconfdir=/etc',
                '--localstatedir=/var',
                '--enable-shared'
                ] + autotools.calc_conf_hbt_options(self)

        ret += [
            '--enable-targets=all',

            '--enable-64-bit-bfd',
            '--disable-werror',
            '--enable-libada',
            '--enable-libssp',
            '--enable-objc-gc',

            '--enable-lto',
            '--enable-ld',

            # NOTE: no google software in Lailalo
            '--disable-gold',
            '--without-gold',

            # this is required. else libs will be searched in /lib and
            # /usr/lib, but not in /multihost/xxx/lib!:
            '--with-sysroot={}'.format(self.get_host_dir()),

            # more experiment:
            '--enable-multiarch',
            '--enable-multilib',
            ]

        if self.get_is_crossbuilder():
            ret += ['--with-sysroot']

        return ret

    def builder_action_build_define_environment(self, called_as, log):
        return {}

    #def builder_action_build_define_cpu_count(self, called_as, log):
    #    return 1
