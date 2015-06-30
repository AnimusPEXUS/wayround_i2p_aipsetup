
import os.path

import wayround_org.aipsetup.builder_scripts.std


class Builder(wayround_org.aipsetup.builder_scripts.std.Builder):

    def builder_action_configure_define_options(self, called_as, log):
        return super().builder_action_configure_define_options(called_as, log) + [
            # '--disable-nis',
            '--enable-db=ndbm',
            '--enable-read-both-confs',
            '--enable-selinux'
            #'--enable-securedir=/pam_modules'
            ]
    """
    def builder_action_distribute(self, called_as, log):
        ret= super().builder_action_distribute(called_as, log)

        if ret == 0:

            os.makedirs(
                os.path.join(
                    self.dst_dir, 'usr', 'lib'
                    ),
                exist_ok=True
                )
            os.makedirs(
                os.path.join(
                    self.dst_dir, 'usr', 'lib64'
                    ),
                exist_ok=True
                )

            os.symlink(
                os.path.join('..', '..', 'pam_modules'),
                os.path.join(self.dst_dir, 'usr', 'lib', 'security')
                )
            os.symlink(
                os.path.join('..', '..', 'pam_modules'),
                os.path.join(self.dst_dir, 'usr', 'lib64', 'security')
                )
        return ret
    """
