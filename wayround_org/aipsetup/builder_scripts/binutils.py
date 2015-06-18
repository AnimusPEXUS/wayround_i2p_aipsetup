
import logging
import os.path
import collections
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        self.forced_target = True
        return None

    def define_actions(self):
        ret = super().define_actions()
        if self.is_crossbuilder:
            ret['edit_package_info'] = self.builder_action_edit_package_info
            ret.move_to_end('edit_package_info', False)

            ret['after_distribute'] = self.builder_action_after_distribute
            # ret['delete_share'] = self.builder_action_delete_share
        return ret

    def builder_action_edit_package_info(self, log):

        ret = 0

        try:
            name = self.package_info['pkg_info']['name']
        except:
            name = None

        if name in ['binutils', None]:
            pi = self.package_info

            pi['pkg_info']['name'] = 'cb-binutils-{target}'.format(
                target=self.target
                )

            bs = self.control

            bs.write_package_info(pi)

        return ret

    def builder_action_extract(self, log):

        ret = super().builder_action_extract(
            log
            )

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

    def builder_action_configure_define_options(self, log):

        ret = super().builder_action_configure_define_options(log)

        if self.is_crossbuilder:
            prefix = os.path.join(
                '/', 'usr', 'crossbuilders', self.target
                )

            ret = [
                '--prefix=' + prefix,
                '--mandir=' + os.path.join(prefix, 'share', 'man'),
                '--sysconfdir=' +
                self.package_info['constitution']['paths']['config'],
                '--localstatedir=' +
                self.package_info['constitution']['paths']['var'],
                '--enable-shared'
                ] + autotools.calc_conf_hbt_options(self)

        ret += [
            #'--enable-targets='
            #'i486-pc-linux-gnu,'
            # 'i586-pc-linux-gnu,'
            # 'i686-pc-linux-gnu,'
            # 'i786-pc-linux-gnu,'
            # 'ia64-pc-linux-gnu,'
            #'x86_64-pc-linux-gnu,'
            #'aarch64-linux-gnu',

            '--enable-targets=all',

            # WARNING: enabling this will cause problem on building native
            #          GCC
            #'--with-sysroot',

            #                    '--disable-libada',
            #                    '--enable-bootstrap',
            '--enable-64-bit-bfd',
            '--disable-werror',
            '--enable-libada',
            '--enable-libssp',
            '--enable-objc-gc',

            '--enable-lto',
            '--enable-ld'
            ]

        if self.is_crossbuilder:
            # NOTE: under question
            ret += ['--with-sysroot']
            # pass

        return ret

    def builder_action_after_distribute(self, log):

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

    def builder_action_delete_share(self, log):

        share = os.path.join(self.dst_dir, 'usr', 'share')

        if os.path.isdir(share):
            shutil.rmtree(share)

        return 0
