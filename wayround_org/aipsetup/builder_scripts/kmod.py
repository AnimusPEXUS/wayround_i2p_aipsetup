
import logging
import os.path

import wayround_org.aipsetup.build
import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.utils.file


import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, log):
        return super().builder_action_configure_define_options(log) + [
            '--with-xz',
            '--with-zlib',
            ]

    def define_actions(self):
        ret = super().define_actions()
        ret['make_links'] = self.builder_action_make_links
        return ret

    def builder_action_make_links(self, log):

        os.makedirs(
            os.path.join(self.dst_dir, 'usr', 'sbin'),
            exist_ok=True
            )

        for i in ['depmod', 'insmod', 'modinfo', 'modprobe', 'rmmod']:

            ffn = os.path.join(self.dst_dir, 'usr', 'sbin', i)

            if os.path.exists(ffn):
                os.unlink(ffn)

            p1 = os.path.join('..', 'bin', 'kmod')
            p2 = ffn
            log.info(
                "link: {} -> {}".format(
                    os.path.relpath(p2, self.buildingsite),
                    p1
                    )
                )
            os.symlink(p1, p2)

        for i in ['lsmod']:

            ffn = os.path.join(self.dst_dir, 'usr', 'bin', i)

            if os.path.exists(ffn):
                os.unlink(ffn)

            p1 = os.path.join('.', 'kmod')
            p2 = ffn
            log.info(
                "link: {} -> {}".format(
                    os.path.relpath(p2, self.buildingsite),
                    p1
                    )
                )
            os.symlink(p1, p2)
        return 0
