
import logging
import os.path
import collections

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_custom_data(self):
        ret = dict()
        return ret

    def builder_action_configure(self):

        target = self.package_info['constitution']['target']
        host = self.package_info['constitution']['host']
        build = self.package_info['constitution']['build']
        prefix = self.package_info['constitution']['paths']['usr']

        prefix = self.package_info['constitution']['paths']['usr']
        mandir = self.package_info['constitution']['paths']['man']
        sysconfdir = self.package_info['constitution']['paths']['config']
        localstatedir = self.package_info['constitution']['paths']['var']

        if ('crossbuilder_mode' in self.custom_data
                and self.custom_data['crossbuilder_mode'] == True):
            pass
            #prefix = os.path.join(
            #    '/', 'usr', 'lib', 'unicorn_crossbuilders', target
            #    )
            # mandir = os.path.join(prefix, 'man')
            # sysconfdir = os.path.join(prefix, 'etc')
            # localstatedir = os.path.join(prefix, 'var')

        ret = autotools.configure_high(
            self.buildingsite,
            options=[
                # '--enable-targets='
                # 'i486-pc-linux-gnu,'
                # 'i586-pc-linux-gnu,'
                # 'i686-pc-linux-gnu,'
                # 'i786-pc-linux-gnu,'
                # 'ia64-pc-linux-gnu,'
                # 'x86_64-pc-linux-gnu,'
                # 'aarch64-linux-gnu',

                '--enable-targets=all',

                #                    '--disable-libada',
                #                    '--enable-bootstrap',
                '--enable-64-bit-bfd',
                '--disable-werror',
                '--enable-libada',
                '--enable-libssp',
                '--enable-objc-gc',

                '--prefix=' + prefix,
                '--mandir=' + mandir,
                '--sysconfdir=' + sysconfdir,
                '--localstatedir=' + localstatedir,

                '--host=' + host,
                '--build=' + build,
                '--target=' + target
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

    def builder_action_dst_cleanup(self):
        """
        Standard destdir cleanup
        """
        if ('crossbuilder_mode' in self.custom_data
                and self.custom_data['crossbuilder_mode'] == True):
            logging.info(
                "Destination directory cleanup skipped doe to "
                "'crossbuilder_mode'"
                )
        else:

            if os.path.isdir(self.src_dir):
                logging.info("cleaningup destination dir")
                wayround_org.utils.file.cleanup_dir(self.dst_dir)

        return 0
