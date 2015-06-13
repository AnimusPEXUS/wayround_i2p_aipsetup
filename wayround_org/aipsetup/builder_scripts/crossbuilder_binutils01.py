
import logging
import os.path
import collections
import shutil

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools


import wayround_org.aipsetup.builder_scripts.binutils


class Builder(wayround_org.aipsetup.builder_scripts.binutils.Builder):

    def define_actions(self):
        lst = [('apply_pkg_nameinfo', self.builder_action_edit_package_info)]
        r = super().define_actions()

        for i in r.keys():
            lst.append((i, r[i]))

        #lst += [('after_distribute', self.builder_action_after_distribute)]

        #lst += [('delete_share', self.builder_action_delete_share)]

        return collections.OrderedDict(lst)

    def builder_action_edit_package_info(self):

        ret = 0

        files = os.listdir(self.tar_dir)

        tar = None
        for i in files:
            if i.startswith('binutils'):
                tar = i

        if tar is None:
            ret = 1
        else:
            bs = wayround_org.aipsetup.build.BuildingSiteCtl(self.buildingsite)
            bs.apply_pkg_nameinfo_on_buildingsite(tar)
        return ret

    def builder_action_extract(self):
        ret = autotools.extract_high(
            self.buildingsite,
            'binutils',
            unwrap_dir=True,
            rename_dir=False
            )
        return ret

    def builder_action_configure(self):

        """
        ;-)
        """

        """
        prefix = os.path.join(
            '/', 'usr'
            )
        """

        prefix = os.path.join(
            '/', 'usr', 'lib', 'unicorn_crossbuilders', self.target, 'usr'
            )
        mandir = os.path.normpath(os.path.join(prefix, 'share', 'man'))
        sysconfdir = os.path.normpath(os.path.join(prefix, '..', 'etc'))
        localstatedir = os.path.normpath(os.path.join(prefix, '..', 'var'))

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
                '--enable-targets=all',

                '--with-sysroot',
                '--enable-multiarch',
                '--enable-multilib',

                #                    '--disable-libada',
                #                    '--enable-bootstrap',
                '--enable-64-bit-bfd',
                '--disable-werror',
                '--enable-libada',
                '--enable-libssp',
                '--enable-objc-gc',
                # '--enable-targets='
                # 'i486-pc-linux-gnu,'
                # 'i586-pc-linux-gnu,'
                # 'i686-pc-linux-gnu,'
                # 'i786-pc-linux-gnu,'
                # 'ia64-pc-linux-gnu,'
                # 'x86_64-pc-linux-gnu,'
                # 'aarch64-linux-gnu',

                '--prefix=' + prefix,
                '--mandir=' + mandir,
                '--sysconfdir=' + sysconfdir,
                '--localstatedir=' + localstatedir,

                '--host=' + self.host,
                '--build=' + self.build,
                '--target=' + self.target
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

    def builder_action_after_distribute(self):

        etc_dir = os.path.join(self.dst_dir, 'etc', 'profile.d', 'SET')
        etc_dir_file = os.path.join(
            etc_dir,
            '011.{}.binutils'.format(self.target)
            )

        os.makedirs(etc_dir, exist_ok=True)

        if not os.path.isdir(etc_dir):
            raise Exception("Required dir creation error")

        fi = open(etc_dir_file, 'w')

        fi.write(
            """\
#!/bin/bash
export PATH=$PATH:/usr/lib/unicorn_crossbuilders/{target}/usr/bin:\
/usr/lib/unicorn_crossbuilders/{target}/usr/sbin
""".format(target=self.target)
            )

        fi.close()

        return 0

    def builder_action_delete_share(self):

        share = os.path.join(self.dst_dir, 'usr', 'share')

        if os.path.isdir(share):
            shutil.rmtree(share)

        return 0
