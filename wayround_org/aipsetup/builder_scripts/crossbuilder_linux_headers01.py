
import collections

import wayround_org.aipsetup.buildtools.autotools as autotools
import wayround_org.aipsetup.builder_scripts.linux


class Builder(wayround_org.aipsetup.builder_scripts.linux.Builder):

    def define_actions(self):
        return collections.OrderedDict([
            ('src_cleanup', self.builder_action_src_cleanup),
            ('extract', self.builder_action_extract),
            ('distr_headers_normal', self.builder_action_distr_headers_normal)
            ])

    def builder_action_extract(self):
        ret = autotools.extract_high(
            self.buildingsite,
            'linux',
            unwrap_dir=True,
            rename_dir=False
            )
        return ret
