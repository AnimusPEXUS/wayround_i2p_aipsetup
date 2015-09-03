
import os.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_opts(self, called_as, log):
        ret = super().builder_action_configure_define_opts(called_as, log)
        ret += [
            # '--disable-nis',
            '--enable-db=ndbm',
            '--enable-read-both-confs',
            '--enable-selinux',
            '--includedir={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'include',
                    'security' # it's not a mistake: 'security' dir is here
                               # required at least by 'polkit'
                    )
                ),
            '--enable-securedir={}'.format(
                wayround_org.utils.path.join(
                    self.calculate_install_prefix(),
                    'lib',
                    'security'
                    )
                )
            ]  # + self.all_automatic_flags_as_list()

        return ret
