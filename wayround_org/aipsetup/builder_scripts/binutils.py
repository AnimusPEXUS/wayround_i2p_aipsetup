
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

        # NOTE: following actions is meaningless for Lalilalo multiarch
        #       approach
        # if self.is_crossbuilder:
        # ret['after_distribute'] = self.builder_action_after_distribute
        # ret['delete_share'] = self.builder_action_delete_share

        return ret

    def builder_action_edit_package_info(self, called_as, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        pi = self.package_info

        if self.is_crossbuilder:
            pi['pkg_info']['name'] = 'cb-binutils-{}'.format(self.target)
        else:
            pi['pkg_info']['name'] = 'binutils'

        bs = self.control
        bs.write_package_info(pi)

        return ret

    def builder_action_extract(self, called_as, log):

        ret = super().builder_action_extract(called_as, log)

        if ret == 0:

            for i in ['gmp', 'mpc', 'mpfr', 'isl', 'cloog']:

                if autotools.extract_high(
                        self.buildingsite,
                        i,
                        log=log,
                        unwrap_dir=False,
                        rename_dir=i
                        ) != 0:

                    log.error("Can't extract component: {}".format(i))
                    ret = 2

        return ret

    def builder_action_configure_define_options(self, called_as, log):

        ret = super().builder_action_configure_define_options(called_as, log)

        if self.is_crossbuilder:
            prefix = wayround_org.utils.path.join(
                self.host_crossbuilders_dir, self.target
                )

            ret = [
                '--prefix=' + prefix,
                '--mandir=' + os.path.join(prefix, 'share', 'man'),
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

            # experiment:
            '--with-sysroot={}'.format(self.host_multiarch_dir)
            ]

        if self.is_crossbuilder:
            ret += ['--with-sysroot']

        return ret

    '''
    def builder_action_after_distribute(self, called_as, log):

        etc_dir = os.path.join(self.dst_dir, 'etc', 'profile.d', 'SET')
        etc_dir_file = os.path.join(
            etc_dir,
            '020.cross_builder.{}.binutils'.format(self.target)
            )

        os.makedirs(etc_dir, exist_ok=True)

        if not os.path.isdir(etc_dir):
            raise Exception("Required dir creation error")

        fi = open(etc_dir_file, 'w')

        fi.write(
            """\
#!/bin/bash
export PATH=$PATH:/usr/crossbuilders/{target}/bin:\
/usr/crossbuilders/{target}/sbin
""".format(target=self.target)
            )

        fi.close()

        return 0
    '''

    '''
    def builder_action_delete_share(self, called_as, log):

        share = os.path.join(self.dst_dir, 'usr', 'share')

        if os.path.isdir(share):
            shutil.rmtree(share)

        return 0
    '''
