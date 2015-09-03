
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

    def builder_action_extract(self, called_as, log):
        ret = autotools.extract_high(
            self.buildingsite_path,
            self.get_package_info()['pkg_info']['basename'],
            log=log,
            unwrap_dir=False,
            rename_dir=False,
            more_when_one_extracted_ok=True
            )
        return ret

    def builder_action_distribute(self, called_as, log):

        man_dir = wayround_org.utils.path.join(
            self.calculate_dst_install_prefix(), 'share', 'man'
            )

        mans = os.listdir(self.get_src_dir())

        for i in mans:

            m = wayround_org.utils.path.join(man_dir, i)
            sm = wayround_org.utils.path.join(self.get_src_dir(), i)

            os.makedirs(m)

            wayround_org.utils.file.copytree(
                src_dir=sm,
                dst_dir=m,
                overwrite_files=True,
                clear_before_copy=False,
                dst_must_be_empty=False
                )

        return 0
