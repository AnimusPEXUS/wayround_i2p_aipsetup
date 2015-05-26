
import os.path
import collections

import wayround_org.aipsetup.buildtools.autotools as autotools


import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def define_actions(self):
        return collections.OrderedDict([
            ('dst_cleanup', self.builder_action_dst_cleanup),
            ('src_cleanup', self.builder_action_src_cleanup),
            ('bld_cleanup', self.builder_action_bld_cleanup),
            ('extract', self.builder_action_extract),
            ('distribute', self.builder_action_distribute)
            ])

    def builder_action_extract(self, log):
        ret = autotools.extract_high(
            self.buildingsite,
            self.package_info['pkg_info']['basename'],
            log=log,
            unwrap_dir=False,
            rename_dir=False,
            more_when_one_extracted_ok=True
            )
        return ret

    def builder_action_distribute(self, log):

        man_dir = os.path.join(self.dst_dir, 'usr', 'share', 'man')

        mans = os.listdir(self.src_dir)

        for i in mans:

            m = os.path.join(man_dir, i)
            sm = os.path.join(self.src_dir, i)

            os.makedirs(m)

            wayround_org.utils.file.copytree(
                src_dir=sm,
                dst_dir=m,
                overwrite_files=True,
                clear_before_copy=False,
                dst_must_be_empty=False
                )

        return 0
