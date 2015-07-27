
import os.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            # '--disable-nis',
            '--enable-db=ndbm',
            '--enable-read-both-confs',
            '--enable-selinux',
            '--includedir={}'.format(
                os.path.join(
                    self.host_multiarch_dir,
                    'include',
                    'security'
                    )
                )
            #'--enable-securedir=/pam_modules'
            ]  # + self.all_automatic_flags_as_list()
