
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
                    self.get_host_arch_dir(),
                    'include',
                    'security'
                    )
                )
            #'--enable-securedir=/pam_modules'
            ]  # + self.all_automatic_flags_as_list()

        return ret
